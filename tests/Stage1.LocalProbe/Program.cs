using System.Net;
using System.Security.Cryptography;
using System.Text.Json;
using Microsoft.Azure.Cosmos;
using Microsoft.Data.SqlClient;

// Local dependency capability tests, not service features or Azure permission tests.
var runtime = Environment.GetEnvironmentVariable("PP_LOCAL_RUNTIME") ?? throw new InvalidOperationException("Use the Local coordinator");
var config = JsonSerializer.Deserialize<LocalConfig>(File.ReadAllText(Path.Combine(runtime, "probe.json")))!;
if (config.SqlPort is < 1024 or > 65535 || config.CosmosPort is < 1024 or > 65535)
    throw new InvalidOperationException("Invalid Local ports");
var fixture = JsonSerializer.Deserialize<Fixture>(File.ReadAllText(config.FixturePath), new JsonSerializerOptions { PropertyNameCaseInsensitive = true })!;
if (fixture.Database != "ParameterPilotLocalBootstrap" || fixture.Container != "local-bootstrap" || fixture.PartitionKey != "/tankId" || fixture.Items.Any(i=>i.marker != "pp-local-bootstrap-v1"))
    throw new InvalidOperationException("Only dedicated Local bootstrap fixtures are permitted");
var checks = new List<Check>();
async Task Test(string name, Func<Task> action) {
    try { await action(); checks.Add(new(name,true)); }
    catch(Exception e) { checks.Add(new(name,false,e is CosmosException c ? "Cosmos"+(int)c.StatusCode : e.GetType().Name)); }
}
static void Ensure(bool value) { if (!value) throw new InvalidOperationException(); }
var cs = new SqlConnectionStringBuilder { DataSource="tcp:127.0.0.1,"+config.SqlPort, UserID="sa", Password=File.ReadAllText(Path.Combine(runtime,"sql-password")), Encrypt=true, TrustServerCertificate=true, ConnectTimeout=15 };
using var sql = new SqlConnection(cs.ConnectionString);
await sql.OpenAsync();
async Task<object?> Sql(string text) { using var command=new SqlCommand(text,sql);return await command.ExecuteScalarAsync(); }
await Test("sqlDeveloperEdition",async()=>Ensure(((string)(await Sql("SELECT SERVERPROPERTY('Edition')"))!).Contains("Developer")));
await Sql("IF DB_ID(N'ParameterPilotLocalBootstrap') IS NULL CREATE DATABASE [ParameterPilotLocalBootstrap];");
sql.ChangeDatabase("ParameterPilotLocalBootstrap");
await Sql("IF SCHEMA_ID(N'LocalBootstrap') IS NULL EXEC(N'CREATE SCHEMA LocalBootstrap'); IF OBJECT_ID(N'LocalBootstrap.SyntheticFixture') IS NULL CREATE TABLE LocalBootstrap.SyntheticFixture(Id nvarchar(40) NOT NULL PRIMARY KEY, Value int NOT NULL);");
async Task SeedSql() {
    foreach(var item in fixture.Items) {
        using var command=new SqlCommand("UPDATE LocalBootstrap.SyntheticFixture SET Value=@value WHERE Id=@id; IF @@ROWCOUNT=0 INSERT LocalBootstrap.SyntheticFixture VALUES(@id,@value);",sql);
        command.Parameters.AddWithValue("@id",item.id);command.Parameters.AddWithValue("@value",item.value);
        await command.ExecuteNonQueryAsync();
    }
}
await Test("sqlSeedRepeatable",async()=>{await SeedSql();await SeedSql();Ensure(Convert.ToInt32(await Sql("SELECT COUNT(*) FROM LocalBootstrap.SyntheticFixture WHERE Id IN ('fixture-a','fixture-b')"))==2);});
await Test("sqlTransactionRollback",async()=>{
    using(var transaction=sql.BeginTransaction()) {
        using var command=new SqlCommand("UPDATE LocalBootstrap.SyntheticFixture SET Value=999 WHERE Id='fixture-a'",sql,transaction);await command.ExecuteNonQueryAsync();transaction.Rollback();
    }
    Ensure(Convert.ToInt32(await Sql("SELECT Value FROM LocalBootstrap.SyntheticFixture WHERE Id='fixture-a'"))==42);
});
if(args.SequenceEqual(new[]{"--sql-only"})) {
    var sqlEvidence=new {passed=checks.All(c=>c.Passed),checks,scope="Approved Local SQL image only; no Cosmos or Azure operation"};
    await File.WriteAllTextAsync(Path.Combine(runtime,"sql-result.json"),JsonSerializer.Serialize(sqlEvidence,new JsonSerializerOptions{WriteIndented=true}));
    Console.WriteLine(JsonSerializer.Serialize(sqlEvidence));
    return sqlEvidence.passed?0:1;
}
var pin=File.ReadAllText(Path.Combine(runtime,"cosmos-cert-sha256"));
var options=new CosmosClientOptions { ConnectionMode=ConnectionMode.Gateway, RequestTimeout=TimeSpan.FromSeconds(20), LimitToEndpoint=true,
    HttpClientFactory=()=>new HttpClient(new HttpClientHandler {
        ServerCertificateCustomValidationCallback=(request,certificate,chain,errors)=>request.RequestUri?.Host=="localhost" && request.RequestUri.Port==config.CosmosPort && certificate is not null && Convert.ToHexString(SHA256.HashData(certificate.RawData))==pin
    }) };
// This emulator does not enforce authentication. The placeholder key is Local-only.
using var cosmos=new CosmosClient("https://localhost:"+config.CosmosPort,Convert.ToBase64String(new byte[64]),options);
var database=await cosmos.CreateDatabaseIfNotExistsAsync(fixture.Database);
var container=(await database.Database.CreateContainerIfNotExistsAsync(fixture.Container,fixture.PartitionKey)).Container;
await Test("cosmosPartitionKey",async()=>{var properties=await container.ReadContainerAsync();Ensure(properties.Resource.PartitionKeyPath=="/tankId");});
await Test("cosmosSeedRepeatable",async()=>{for(var repeat=0;repeat<2;repeat++)foreach(var item in fixture.Items)await container.UpsertItemAsync(item,new PartitionKey(item.tankId));foreach(var item in fixture.Items)Ensure((await container.ReadItemAsync<Item>(item.id,new PartitionKey(item.tankId))).Resource.value==item.value);});
await Test("cosmosWrongPartitionNotFound",async()=>{try{await container.ReadItemAsync<Item>("fixture-a",new PartitionKey("synthetic-tank-b"));}catch(CosmosException e) when(e.StatusCode==HttpStatusCode.NotFound){return;}throw new InvalidOperationException();});
await Test("cosmosEtagConflict",async()=>{
    var first=await container.ReadItemAsync<Item>("fixture-a",new PartitionKey("synthetic-tank-a"));
    await container.ReplaceItemAsync(first.Resource with {value=43},"fixture-a",new PartitionKey("synthetic-tank-a"));
    try{await container.ReplaceItemAsync(first.Resource,"fixture-a",new PartitionKey("synthetic-tank-a"),new ItemRequestOptions {IfMatchEtag=first.ETag});}
    catch(CosmosException e) when(e.StatusCode==HttpStatusCode.PreconditionFailed){await container.UpsertItemAsync(fixture.Items[0],new PartitionKey("synthetic-tank-a"));return;}
    throw new InvalidOperationException();
});
await Test("cosmosSamePartitionBatchCommit",async()=>{
    using var result=await container.CreateTransactionalBatch(new PartitionKey("synthetic-tank-a"))
        .UpsertItem(new Item("batch-a","synthetic-tank-a","pp-local-bootstrap-v1",1))
        .UpsertItem(new Item("batch-b","synthetic-tank-a","pp-local-bootstrap-v1",2)).ExecuteAsync();
    Ensure(result.IsSuccessStatusCode);
    Ensure((await container.ReadItemAsync<Item>("batch-a",new PartitionKey("synthetic-tank-a"))).Resource.value==1);
    Ensure((await container.ReadItemAsync<Item>("batch-b",new PartitionKey("synthetic-tank-a"))).Resource.value==2);
});
await Test("cosmosSamePartitionBatchRollback",async()=>{
    using var result=await container.CreateTransactionalBatch(new PartitionKey("synthetic-tank-a"))
        .ReplaceItem("fixture-a",fixture.Items[0] with {value=999})
        .CreateItem(fixture.Items[0]).ExecuteAsync();
    Ensure(!result.IsSuccessStatusCode);
    Ensure((await container.ReadItemAsync<Item>("fixture-a",new PartitionKey("synthetic-tank-a"))).Resource.value==42);
});
foreach(var id in new[]{"batch-a","batch-b"}) {try{await container.DeleteItemAsync<Item>(id,new PartitionKey("synthetic-tank-a"));}catch(CosmosException e) when(e.StatusCode==HttpStatusCode.NotFound) {}}
var evidence=new { passed=checks.All(c=>c.Passed), checks, scope="Local-only synthetic dependency checks; no Azure access or product-feature claim" };
await File.WriteAllTextAsync(Path.Combine(runtime,"result.json"),JsonSerializer.Serialize(evidence,new JsonSerializerOptions{WriteIndented=true}));
Console.WriteLine(JsonSerializer.Serialize(evidence));
return evidence.passed?0:1;

record LocalConfig(int SqlPort,int CosmosPort,string FixturePath);
record Fixture(string Database,string Container,string PartitionKey,Item[] Items);
record Item(string id,string tankId,string marker,int value);
record Check(string Name,bool Passed,string? Error=null);
