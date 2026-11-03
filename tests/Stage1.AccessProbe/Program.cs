using Azure.Core;
using Azure.Identity;
using Microsoft.Azure.Cosmos;
using Microsoft.Data.SqlClient;
using System.Net;
using System.Text;
using System.Text.Json;
using System.Security.Cryptography;
using System.Security.Cryptography.X509Certificates;

var builder = WebApplication.CreateBuilder(args);
builder.Logging.ClearProviders();
var app = builder.Build();
app.MapGet("/", () => Results.Text("Stage 1 access verification host"));
app.Lifetime.ApplicationStarted.Register(() => _ = Task.Run(Probe.Run));
await app.RunAsync();

record ProbeSettings(string RunId, string SqlTable, string MigrationTable, string ForbiddenTable, string[] OtherProductTables, string Mode = "data", Dictionary<string,string>? SecretHashes = null, Dictionary<string,Dictionary<string,string>>? ManagementTags = null, Dictionary<string,RoleAssignmentProbe>? RoleAssignments = null, string? CredentialClientId = null, string? ExpectedPrincipalId = null, string? CertificateSecretUri = null, string? CertificateThumbprint = null);
record RoleAssignmentProbe(string Id, JsonElement Properties);
record ProbeItem(string id, string tankId, int value, string marker);
record CheckResult(string Name, bool Passed, string? Error = null);

static class Probe
{
    static readonly List<CheckResult> Checks = [];
    static async Task Check(string name, Func<Task> action)
    {
        try { await action(); Checks.Add(new(name, true)); }
        catch (Exception e) { Checks.Add(new(name, false, SafeError(e))); }
    }
    static string SafeError(Exception e) => e switch {
        SqlException s => $"SqlException:{s.Number}:{s.State}",
        CosmosException c => $"CosmosException:{(int)c.StatusCode}:{c.SubStatusCode}",
        HttpRequestException h => "HttpStatus:" + (int?)h.StatusCode,
        _ => e.GetType().Name
    };
    static void Ensure(bool condition) { if (!condition) throw new InvalidOperationException(); }
    static async Task Sql(SqlConnection c, string sql) { using var cmd = new SqlCommand(sql,c); await cmd.ExecuteNonQueryAsync(); }
    static async Task<object?> Scalar(SqlConnection c, string sql) { using var cmd = new SqlCommand(sql,c); return await cmd.ExecuteScalarAsync(); }
    static async Task SqlDenied(SqlConnection c, string sql, params int[] numbers)
    {
        try { await Sql(c,sql); }
        catch (SqlException e) when (numbers.Contains(e.Number)) { return; }
        throw new InvalidOperationException();
    }
    static async Task CosmosDenied(Func<Task> action)
    {
        try { await action(); }
        catch (CosmosException e) when (e.StatusCode == HttpStatusCode.Forbidden) { return; }
        throw new InvalidOperationException();
    }
    static async Task<HttpResponseMessage> Request(ManagedIdentityCredential credential,string scope,string url,HttpMethod method,object? body=null)
    {
        var token = await credential.GetTokenAsync(new TokenRequestContext([scope]));
        using var request = new HttpRequestMessage(method,url);
        request.Headers.Authorization = new("Bearer",token.Token);
        if (body is not null) request.Content = new StringContent(JsonSerializer.Serialize(body),Encoding.UTF8,"application/json");
        using var client = new HttpClient { Timeout=TimeSpan.FromSeconds(30) };
        return await client.SendAsync(request);
    }
    static async Task ConfigurationChecks(ManagedIdentityCredential credential,string role,ProbeSettings settings)
    {
        var other = role == "aquarium" ? "tracking" : "aquarium";
        var configScope = "https://azconfig.io/.default";
        var vaultScope = "https://vault.azure.net/.default";
        var armScope = "https://management.azure.com/.default";
        string Key(string service) => "Stage1:Step2:"+settings.RunId+":"+service;
        string Config(string service,string key) => "https://appcs-adt-"+service+"-dev.azconfig.io/kv/"+Uri.EscapeDataString(key)+"?api-version=1.0";
        string Secret(string service,string name) => "https://kv-adt-"+service+"-dev.vault.azure.net/secrets/"+name+"?api-version=7.4";
        var secretName = "pp-step2-"+settings.RunId;
        async Task Denied(string scope,string url,HttpMethod method,object? body=null)
        {
            using var response = await Request(credential,scope,url,method,body);
            if (response.StatusCode!=HttpStatusCode.Forbidden) throw new HttpRequestException("Unexpected verification status",null,response.StatusCode);
        }
        await Check("ownConfigurationRead",async () => {
            using var response = await Request(credential,configScope,Config(role,Key(role)),HttpMethod.Get);
            Ensure(response.StatusCode==HttpStatusCode.OK);
            using var value = JsonDocument.Parse(await response.Content.ReadAsStringAsync());
            Ensure(value.RootElement.GetProperty("value").GetString()=="synthetic-step2-"+settings.RunId+"-"+role);
        });
        await Check("crossServiceConfigurationReadDenied",()=>Denied(configScope,Config(other,Key(other)),HttpMethod.Get));
        await Check("configurationCreateDenied",()=>Denied(configScope,Config(role,Key(role)+":denied-create"),HttpMethod.Put,new {value="must-be-denied"}));
        await Check("configurationUpdateDenied",()=>Denied(configScope,Config(role,Key(role)),HttpMethod.Put,new {value="must-be-denied"}));
        await Check("configurationDeleteDenied",()=>Denied(configScope,Config(role,Key(role)),HttpMethod.Delete));
        await Check("ownSecretRead",async () => {
            using var response = await Request(credential,vaultScope,Secret(role,secretName),HttpMethod.Get);
            Ensure(response.StatusCode==HttpStatusCode.OK);
            using var value = JsonDocument.Parse(await response.Content.ReadAsStringAsync());
            var hash = Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(value.RootElement.GetProperty("value").GetString()!))).ToLowerInvariant();
            Ensure(hash==settings.SecretHashes![role]);
        });
        await Check("crossServiceSecretReadDenied",()=>Denied(vaultScope,Secret(other,secretName),HttpMethod.Get));
        await Check("secretCreateDenied",()=>Denied(vaultScope,Secret(role,secretName+"-denied-create"),HttpMethod.Put,new {value="synthetic-write-must-be-denied"}));
        await Check("secretUpdateDenied",()=>Denied(vaultScope,Secret(role,secretName),HttpMethod.Put,new {value="synthetic-write-must-be-denied"}));
        await Check("secretDeleteDenied",()=>Denied(vaultScope,Secret(role,secretName),HttpMethod.Delete));
        var baseId = "https://management.azure.com/subscriptions/9671ac36-9800-451a-b283-35ea87f8b419/resourceGroups/rg-parameterpilot-dev/providers/";
        var configurationId = baseId+"Microsoft.AppConfiguration/configurationStores/appcs-adt-"+role+"-dev";
        var vaultId = baseId+"Microsoft.KeyVault/vaults/kv-adt-"+role+"-dev";
        var configurationGrant = settings.RoleAssignments![role+":configuration"];
        await Check("configurationRoleAdministrationDenied",()=>Denied(armScope,"https://management.azure.com"+configurationGrant.Id+"?api-version=2022-04-01",HttpMethod.Put,new {properties=configurationGrant.Properties}));
        var vaultGrant = settings.RoleAssignments![role+":vault"];
        await Check("vaultRoleAdministrationDenied",()=>Denied(armScope,"https://management.azure.com"+vaultGrant.Id+"?api-version=2022-04-01",HttpMethod.Put,new {properties=vaultGrant.Properties}));
        // No-op tag payloads avoid changing settings even if an unexpected management grant exists.
        await Check("configurationManagementWriteDenied",()=>Denied(armScope,configurationId+"?api-version=2024-06-01",HttpMethod.Patch,new {tags=settings.ManagementTags![role+":configuration"]}));
        await Check("vaultManagementWriteDenied",()=>Denied(armScope,vaultId+"?api-version=2024-11-01",HttpMethod.Patch,new {tags=settings.ManagementTags![role+":vault"]}));
    }
    static async Task DeveloperChecks(ManagedIdentityCredential credential, ProbeSettings settings, string sqlToken)
    {
        using var connection = new SqlConnection("Server=tcp:sql-adt-platform-dev.database.windows.net,1433;Initial Catalog=ReferenceProjectsDb;Encrypt=True;TrustServerCertificate=False;Connect Timeout=30;") { AccessToken=sqlToken };
        await Check("developerRealSqlLogin", async () => {
            await connection.OpenAsync();
            Ensure((string)(await Scalar(connection,"SELECT USER_NAME()"))! == "__Stage3Developer_"+settings.RunId);
        });
        if (connection.State == System.Data.ConnectionState.Open)
        {
            await Check("developerApprovedObjectSelect",async () => Ensure(Convert.ToInt32(await Scalar(connection,$"SELECT Value FROM {settings.SqlTable} WHERE Id=1"))==42));
            await Check("developerInsertDenied",()=>SqlDenied(connection,$"INSERT INTO {settings.SqlTable} VALUES(2,1)",229));
            await Check("developerUpdateDenied",()=>SqlDenied(connection,$"UPDATE {settings.SqlTable} SET Value=43 WHERE Id=1",229));
            await Check("developerDeleteDenied",()=>SqlDenied(connection,$"DELETE FROM {settings.SqlTable} WHERE Id=1",229));
            await Check("developerDdlDenied",()=>SqlDenied(connection,$"CREATE TABLE {settings.ForbiddenTable}(Id int)",229,262,2760));
            await Check("developerMigrationHistoryReadDenied",()=>SqlDenied(connection,$"SELECT TOP(0) * FROM {settings.MigrationTable}",229));
            foreach (var other in settings.OtherProductTables)
                await Check("developerOtherProductDenied:"+other,()=>SqlDenied(connection,$"SELECT TOP(0) * FROM {other}",229));
            foreach (var permission in new[]{"CONTROL","ALTER ANY USER","ALTER ANY ROLE"})
                await Check("developerSqlAdminDenied:"+permission,async () => Ensure(Convert.ToInt32(await Scalar(connection,$"SELECT HAS_PERMS_BY_NAME(DB_NAME(),'DATABASE','{permission}')"))==0));
        }
        foreach (var service in new[]{"aquarium","tracking"})
        {
            var configUrl=$"https://appcs-adt-{service}-dev.azconfig.io/kv?key=Stage1%3AStep3%3A{settings.RunId}*&api-version=1.0";
            await Check("developerConfigurationRead:"+service,async () => {
                using var response=await Request(credential,"https://azconfig.io/.default",configUrl,HttpMethod.Get);
                Ensure(response.StatusCode==HttpStatusCode.OK);
            });
            await Check("developerConfigurationWriteDenied:"+service,async () => {
                using var response=await Request(credential,"https://azconfig.io/.default",$"https://appcs-adt-{service}-dev.azconfig.io/kv/Stage1%3AStep3%3A{settings.RunId}?api-version=1.0",HttpMethod.Put,new{value="synthetic-must-be-denied"});
                Ensure(response.StatusCode==HttpStatusCode.Forbidden);
            });
            await Check("developerVaultSecretsDenied:"+service,async () => {
                using var response=await Request(credential,"https://vault.azure.net/.default",$"https://kv-adt-{service}-dev.vault.azure.net/secrets/pp-stage3-{settings.RunId}?api-version=7.4",HttpMethod.Get);
                Ensure(response.StatusCode==HttpStatusCode.Forbidden);
            });
        }
        using var cosmos=new CosmosClient("https://cosmos-adt-platform-dev.documents.azure.com:443/",credential,new CosmosClientOptions{ConnectionMode=ConnectionMode.Gateway,SerializerOptions=new CosmosSerializationOptions{PropertyNamingPolicy=CosmosPropertyNamingPolicy.CamelCase}});
        var container=cosmos.GetContainer("ReferenceProjects","parameterpilot-tracking");
        var pk=new PartitionKey("stage3-"+settings.RunId);
        await Check("developerCosmosPointReadAllowed",async () => {
            try { await container.ReadItemAsync<ProbeItem>("stage3-"+settings.RunId,pk); }
            catch(CosmosException e) when(e.StatusCode==HttpStatusCode.NotFound) { return; }
            throw new InvalidOperationException();
        });
        await Check("developerCosmosQueryAllowed",async () => {
            using var query=container.GetItemQueryIterator<ProbeItem>(new QueryDefinition("SELECT * FROM c WHERE c.id=@id").WithParameter("@id","stage3-"+settings.RunId),requestOptions:new QueryRequestOptions{PartitionKey=pk});
            while(query.HasMoreResults) Ensure((await query.ReadNextAsync()).Count==0);
        });
        await Check("developerCosmosCreateDenied",()=>CosmosDenied(async () => await container.CreateItemAsync(new ProbeItem("stage3-"+settings.RunId,"stage3-"+settings.RunId,1,"synthetic-denied"),pk)));
        await Check("developerCosmosOtherProductDenied",()=>CosmosDenied(async () => await cosmos.GetContainer("ReferenceProjects","blastplanning-events").ReadItemAsync<ProbeItem>("stage3-"+settings.RunId,pk)));
        var site="https://management.azure.com/subscriptions/9671ac36-9800-451a-b283-35ea87f8b419/resourceGroups/rg-parameterpilot-dev/providers/Microsoft.Web/sites/api-adt-aquarium-dev";
        await Check("developerResourceMetadataRead",async () => {using var response=await Request(credential,"https://management.azure.com/.default",site+"?api-version=2024-11-01",HttpMethod.Get);Ensure(response.StatusCode==HttpStatusCode.OK);});
        await Check("developerHostAdministrationDenied",async () => {using var response=await Request(credential,"https://management.azure.com/.default",site+"?api-version=2024-11-01",HttpMethod.Patch,new{properties=new{enabled=true,publicNetworkAccess="Disabled"}});Ensure(response.StatusCode==HttpStatusCode.Forbidden);});
    }

    static async Task RegistryChecks(ManagedIdentityCredential credential, string role)
    {
        using var http=new HttpClient{Timeout=TimeSpan.FromSeconds(30)};
        var arm=await credential.GetTokenAsync(new TokenRequestContext(["https://management.azure.com/.default"]));
        using var exchange=await http.PostAsync("https://acradtplatformdev.azurecr.io/oauth2/exchange",new FormUrlEncodedContent(new Dictionary<string,string>{["grant_type"]="access_token",["service"]="acradtplatformdev.azurecr.io",["tenant"]="f4fcd45c-104f-4dd3-b7bf-3475e83ce097",["access_token"]=arm.Token}));
        exchange.EnsureSuccessStatusCode();
        using var exchanged=JsonDocument.Parse(await exchange.Content.ReadAsStringAsync());
        var refresh=exchanged.RootElement.GetProperty("refresh_token").GetString()!;
        async Task<bool> Allowed(string repository,string action)
        {
            using var response=await http.PostAsync("https://acradtplatformdev.azurecr.io/oauth2/token",new FormUrlEncodedContent(new Dictionary<string,string>{["grant_type"]="refresh_token",["service"]="acradtplatformdev.azurecr.io",["scope"]=$"repository:{repository}:{action}",["refresh_token"]=refresh}));
            if(response.StatusCode is HttpStatusCode.Unauthorized or HttpStatusCode.Forbidden) return false;
            response.EnsureSuccessStatusCode();
            using var document=JsonDocument.Parse(await response.Content.ReadAsStringAsync());
            var token=document.RootElement.GetProperty("access_token").GetString()!;
            var encoded=token.Split('.')[1].Replace('-','+').Replace('_','/');
            using var claims=JsonDocument.Parse(Convert.FromBase64String(encoded.PadRight((encoded.Length+3)/4*4,'=')));
            return claims.RootElement.TryGetProperty("access",out var access) && access.EnumerateArray().Any(entry=>entry.GetProperty("name").GetString()==repository && entry.GetProperty("actions").EnumerateArray().Any(value=>value.GetString()==action));
        }
        await Check("runtimeOwnRepositoryPullAuthorised",async()=>Ensure(await Allowed("parameterpilot/"+role+"-api","pull")));
        await Check("runtimeOtherServicePullDenied",async()=>Ensure(!await Allowed("parameterpilot/"+(role=="aquarium"?"tracking":"aquarium")+"-api","pull")));
        await Check("runtimeRepositoryPushDenied",async()=>Ensure(!await Allowed("parameterpilot/"+role+"-api","push")));
        await Check("runtimeUnapprovedRepositoryPullDenied",async()=>Ensure(!await Allowed("parameterpilot/unapproved-repository","pull")));
    }

    static async Task CertificateChecks(ManagedIdentityCredential credential, ProbeSettings settings)
    {
        Ensure(settings.CertificateSecretUri?.StartsWith("https://kv-adt-tracking-dev.vault.azure.net/secrets/tracking-obo-dev/",StringComparison.Ordinal)==true);
        byte[]? pfx=null;
        X509Certificate2? certificate=null;
        try
        {
            await Check("trackingCertificateSecretRead",async()=>{
                using var response=await Request(credential,"https://vault.azure.net/.default",settings.CertificateSecretUri+"?api-version=7.4",HttpMethod.Get);
                response.EnsureSuccessStatusCode();
                using var document=JsonDocument.Parse(await response.Content.ReadAsStringAsync());
                pfx=Convert.FromBase64String(document.RootElement.GetProperty("value").GetString()!);
            });
            await Check("developmentPrivateKeyLoadsEphemerally",()=>{
                ArgumentNullException.ThrowIfNull(pfx);
                certificate=X509CertificateLoader.LoadPkcs12(pfx,"",X509KeyStorageFlags.EphemeralKeySet);
                Ensure(certificate.HasPrivateKey);
                return Task.CompletedTask;
            });
            await Check("developmentCertificateThumbprintMatchesRegistration",()=>{Ensure(certificate?.Thumbprint==settings.CertificateThumbprint);return Task.CompletedTask;});
            await Check("developmentPrivateKeySignsAndPublicKeyVerifies",()=>{
                ArgumentNullException.ThrowIfNull(certificate);
                using var privateKey=certificate.GetRSAPrivateKey();using var publicKey=certificate.GetRSAPublicKey();
                var challenge=RandomNumberGenerator.GetBytes(32);
                var signature=privateKey!.SignData(challenge,HashAlgorithmName.SHA256,RSASignaturePadding.Pkcs1);
                Ensure(publicKey!.VerifyData(challenge,signature,HashAlgorithmName.SHA256,RSASignaturePadding.Pkcs1));
                return Task.CompletedTask;
            });
            await Check("otherServiceCertificateSecretDenied",async()=>{
                using var response=await Request(credential,"https://vault.azure.net/.default",settings.CertificateSecretUri!.Replace("kv-adt-tracking-dev","kv-adt-aquarium-dev",StringComparison.Ordinal)+"?api-version=7.4",HttpMethod.Get);
                Ensure(response.StatusCode==HttpStatusCode.Forbidden);
            });
        }
        finally{certificate?.Dispose();if(pfx is not null)CryptographicOperations.ZeroMemory(pfx);}
    }

    public static async Task Run()
    {
        var host = Environment.GetEnvironmentVariable("WEBSITE_SITE_NAME") ?? "";
        var role = host switch { "api-adt-aquarium-dev" => "aquarium", "api-adt-tracking-dev" => "tracking", _ => "invalid" };
        var expected = role == "aquarium" ? "e43e0132-e184-4669-8431-9f5a3ea5393e" : "6c046dfa-2416-4706-893d-7cc000afecf0";
        var settings = JsonSerializer.Deserialize<ProbeSettings>(await File.ReadAllTextAsync("probe-settings.json"))!;
        if (settings.Mode == "developer") expected = settings.ExpectedPrincipalId ?? throw new InvalidOperationException();
        var started = DateTimeOffset.UtcNow;
        string? observed = null;
        try
        {
            Ensure(role != "invalid" && !string.IsNullOrEmpty(Environment.GetEnvironmentVariable("IDENTITY_ENDPOINT")) && !string.IsNullOrEmpty(Environment.GetEnvironmentVariable("IDENTITY_HEADER")));
            Ensure(settings.RunId.All(char.IsAsciiHexDigit) && settings.RunId.Length == 12);
            Ensure(settings.SqlTable == "[Aquarium].[__Stage1Probe_" + settings.RunId + "]" && settings.MigrationTable == "[Aquarium].[__Stage1MigrationProbe_" + settings.RunId + "]");
            var credential = new ManagedIdentityCredential(settings.Mode == "developer"
                ? ManagedIdentityId.FromUserAssignedClientId(settings.CredentialClientId!)
                : ManagedIdentityId.SystemAssigned); // No developer/environment/CLI credential fallback.
            var sqlToken = await credential.GetTokenAsync(new TokenRequestContext([settings.Mode == "configuration" ? "https://azconfig.io/.default" : "https://database.windows.net/.default"]));
            var payload = sqlToken.Token.Split('.')[1].Replace('-','+').Replace('_','/');
            payload = payload.PadRight((payload.Length + 3) / 4 * 4,'=');
            using (var claims = JsonDocument.Parse(Convert.FromBase64String(payload))) observed = claims.RootElement.GetProperty("oid").GetString();
            Ensure(observed == expected);
            Checks.Add(new(settings.Mode == "developer" ? "managedIdentityObjectIdMatchesApprovedDeveloperProbe" : "managedIdentityObjectIdMatchesHost",true));
            if (settings.Mode == "developer")
            {
                await DeveloperChecks(credential, settings, sqlToken.Token);
            }
            else if (settings.Mode == "certificate")
            {
                Ensure(role=="tracking");
                await CertificateChecks(credential,settings);
            }
            else if (settings.Mode == "registry")
            {
                await RegistryChecks(credential, role);
            }
            else if (settings.Mode == "configuration")
            {
                await ConfigurationChecks(credential,role,settings);
            }
            else
            {
            var connection = new SqlConnection("Server=tcp:sql-adt-platform-dev.database.windows.net,1433;Initial Catalog=ReferenceProjectsDb;Encrypt=True;TrustServerCertificate=False;Connect Timeout=30;") { AccessToken = sqlToken.Token };
            if (role == "aquarium")
            {
                await Check("sqlManagedIdentityLogin", async () => { await connection.OpenAsync(); Ensure((string)(await Scalar(connection,"SELECT USER_NAME()"))! == "api-adt-aquarium-dev"); });
                if (connection.State == System.Data.ConnectionState.Open)
                {
                    await Check("sqlObjectScopedCrud", async () => {
                        await Sql(connection,$"INSERT INTO {settings.SqlTable} (Id,Value) VALUES (1,10)");
                        await Sql(connection,$"UPDATE {settings.SqlTable} SET Value=11 WHERE Id=1");
                        Ensure(Convert.ToInt32(await Scalar(connection,$"SELECT Value FROM {settings.SqlTable} WHERE Id=1")) == 11);
                        await Sql(connection,$"DELETE FROM {settings.SqlTable} WHERE Id=1");
                        Ensure(Convert.ToInt32(await Scalar(connection,$"SELECT COUNT(*) FROM {settings.SqlTable}")) == 0);
                    });
                    await Check("sqlMigrationMetadataReadDenied", () => SqlDenied(connection,$"SELECT TOP(0) * FROM {settings.MigrationTable}",229));
                    await Check("sqlMigrationMetadataWriteDenied", () => SqlDenied(connection,$"INSERT INTO {settings.MigrationTable} (Id) VALUES (1)",229));
                    await Check("sqlDdlDenied", () => SqlDenied(connection,$"CREATE TABLE {settings.ForbiddenTable} (Id int)",262,2760,229));
                    foreach (var table in settings.OtherProductTables)
                        await Check("sqlCrossProductReadDenied:"+table, () => SqlDenied(connection,"SELECT TOP(0) * FROM " + table,229));
                    foreach (var permission in new[]{"CONTROL","ALTER ANY USER","ALTER ANY ROLE","ALTER ANY SCHEMA","CREATE TABLE"})
                        await Check("sqlAdministrationDenied:"+permission,async () => Ensure(Convert.ToInt32(await Scalar(connection,$"SELECT HAS_PERMS_BY_NAME(DB_NAME(),'DATABASE','{permission}')")) == 0));
                    foreach (var sqlRole in new[]{"db_owner","db_datareader","db_datawriter","AquariumMigrations"})
                        await Check("sqlRoleAbsent:"+sqlRole,async () => Ensure(Convert.ToInt32(await Scalar(connection,$"SELECT IS_ROLEMEMBER('{sqlRole}')")) == 0));
                }
            }
            else
            {
                await Check("trackingSqlLoginDenied",async () => {
                    try { await connection.OpenAsync(); }
                    catch (SqlException e) when (e.Number == 18456) { return; }
                    throw new InvalidOperationException();
                });
            }
            await connection.DisposeAsync();
            using var cosmos = new CosmosClient("https://cosmos-adt-platform-dev.documents.azure.com:443/",credential,new CosmosClientOptions {
                ConnectionMode=ConnectionMode.Gateway,
                UseSystemTextJsonSerializerWithOptions=new JsonSerializerOptions(JsonSerializerDefaults.Web),
                RequestTimeout=TimeSpan.FromSeconds(30),
                MaxRetryAttemptsOnRateLimitedRequests=3
            });
            var container = cosmos.GetContainer("ReferenceProjects","parameterpilot-tracking");
            var pk = "stage1-" + settings.RunId;
            if (role == "aquarium")
            {
                await Check("aquariumCosmosAccessDenied",() => CosmosDenied(async () => await container.ReadItemAsync<ProbeItem>("stage1-"+settings.RunId,new PartitionKey(pk))));
            }
            else
            {
                var id = "stage1-"+settings.RunId;
                var suffixes = new[]{"", "-panel", "-idempotency", "-outbox", "-must-not-exist"};
                try
                {
                    await Check("cosmosCreateReadReplaceUpsertDelete",async () => {
                        await container.CreateItemAsync(new ProbeItem(id,pk,1,"synthetic-stage1"),new PartitionKey(pk));
                        Ensure((await container.ReadItemAsync<ProbeItem>(id,new PartitionKey(pk))).Resource.value==1);
                        await container.ReplaceItemAsync(new ProbeItem(id,pk,2,"synthetic-stage1"),id,new PartitionKey(pk));
                        await container.UpsertItemAsync(new ProbeItem(id,pk,3,"synthetic-stage1"),new PartitionKey(pk));
                        Ensure((await container.ReadItemAsync<ProbeItem>(id,new PartitionKey(pk))).Resource.value==3);
                        await container.DeleteItemAsync<ProbeItem>(id,new PartitionKey(pk));
                    });
                    await Check("cosmosSamePartitionTransactionalBatch",async () => {
                        using var response = await container.CreateTransactionalBatch(new PartitionKey(pk))
                            .CreateItem(new ProbeItem(id+"-panel",pk,1,"synthetic-stage1"))
                            .CreateItem(new ProbeItem(id+"-idempotency",pk,1,"synthetic-stage1"))
                            .CreateItem(new ProbeItem(id+"-outbox",pk,1,"synthetic-stage1")).ExecuteAsync();
                        Ensure(response.IsSuccessStatusCode);
                    });
                    await Check("cosmosPartitionScopedQuery",async () => {
                        using var feed = container.GetItemQueryIterator<ProbeItem>(new QueryDefinition("SELECT * FROM c WHERE c.id = @id").WithParameter("@id",id+"-panel"),requestOptions:new QueryRequestOptions {PartitionKey=new PartitionKey(pk)});
                        Ensure((await feed.ReadNextAsync()).Count==1);
                    });
                    await Check("cosmosFailedBatchAtomicity",async () => {
                        using var response = await container.CreateTransactionalBatch(new PartitionKey(pk))
                            .CreateItem(new ProbeItem(id+"-must-not-exist",pk,1,"synthetic-stage1"))
                            .CreateItem(new ProbeItem(id+"-panel",pk,1,"synthetic-stage1")).ExecuteAsync();
                        Ensure(!response.IsSuccessStatusCode);
                        try { await container.ReadItemAsync<ProbeItem>(id+"-must-not-exist",new PartitionKey(pk)); }
                        catch(CosmosException e) when(e.StatusCode==HttpStatusCode.NotFound) { return; }
                        throw new InvalidOperationException();
                    });
                    await Check("cosmosBlastIqContainerDenied",() => CosmosDenied(async () => await cosmos.GetContainer("ReferenceProjects","blastplanning-events").ReadItemAsync<ProbeItem>("stage1-"+settings.RunId,new PartitionKey(pk))));
                }
                finally
                {
                    await Check("cosmosSyntheticDataCleanup",async () => {
                        foreach(var suffix in suffixes)
                            try { await container.DeleteItemAsync<ProbeItem>(id+suffix,new PartitionKey(pk)); }
                            catch(CosmosException e) when(e.StatusCode==HttpStatusCode.NotFound) { }
                    });
                }
            }
            await Check("cosmosManagementReadDenied",async () => {
                var token = await credential.GetTokenAsync(new TokenRequestContext(["https://management.azure.com/.default"]));
                using var http = new HttpClient();
                http.DefaultRequestHeaders.Authorization = new("Bearer",token.Token);
                using var response = await http.GetAsync("https://management.azure.com/subscriptions/9671ac36-9800-451a-b283-35ea87f8b419/resourceGroups/rg-platform-dev/providers/Microsoft.DocumentDB/databaseAccounts/cosmos-adt-platform-dev/sqlDatabases/ReferenceProjects/throughputSettings/default?api-version=2024-11-15");
                if (response.StatusCode!=HttpStatusCode.Forbidden) throw new HttpRequestException("Unexpected verification status",null,response.StatusCode);
            });
            }
        }
        catch (Exception e) { Checks.Add(new("verificationInfrastructure",false,SafeError(e))); }
        var result = new {settings.RunId,Role=role,Host=host,ExpectedPrincipalId=expected,ObservedPrincipalId=observed,StartedUtc=started,CompletedUtc=DateTimeOffset.UtcNow,Passed=Checks.Count>1 && Checks.All(x=>x.Passed),Checks};
        Console.WriteLine("PP_ACCESS_RESULT:"+Convert.ToBase64String(JsonSerializer.SerializeToUtf8Bytes(result)));
    }
}
