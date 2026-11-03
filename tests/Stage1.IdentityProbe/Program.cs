using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Security.Cryptography;
using System.Security.Cryptography.X509Certificates;
using System.Text.Json;
using Microsoft.Identity.Client;
using Microsoft.IdentityModel.Protocols;
using Microsoft.IdentityModel.Protocols.OpenIdConnect;
using Microsoft.IdentityModel.Tokens;

var root = Path.GetFullPath(Path.Combine(AppContext.BaseDirectory,"../../../../../"));
var registrations = JsonDocument.Parse(File.ReadAllText(Path.Combine(root,"docs/infrastructure/evidence/customer-registrations-2026-11-03.json")));
var certs = JsonDocument.Parse(File.ReadAllText(Path.Combine(root,"docs/infrastructure/evidence/obo-certificates-2026-11-03.json")));
var tenant = registrations.RootElement.GetProperty("tenantId").GetString()!;
string Client(string service) => registrations.RootElement.GetProperty("applications").GetProperty(service).GetProperty("clientId").GetString()!;
var ui = Client("ui"); var aquarium = Client("aquarium"); var tracking = Client("tracking");
var authority = registrations.RootElement.GetProperty("authority").GetString()!;
var thumbprint = certs.RootElement.GetProperty("local").GetProperty("thumbprint").GetString()!;
var requestKey = Convert.ToHexString(RandomNumberGenerator.GetBytes(24));
var manager = new ConfigurationManager<OpenIdConnectConfiguration>(authority+"/v2.0/.well-known/openid-configuration",new OpenIdConnectConfigurationRetriever());
var builder=WebApplication.CreateBuilder(args);
builder.Logging.ClearProviders();
builder.WebHost.UseUrls("http://localhost:4200");
var app=builder.Build();
app.Use(async(context,next)=>{
    if(context.Request.Host.Value!="localhost:4200") {context.Response.StatusCode=400;return;}
    context.Response.Headers.CacheControl="no-store";
    context.Response.Headers["X-Content-Type-Options"]="nosniff";
    context.Response.Headers["Referrer-Policy"]="no-referrer";
    await next();
});
app.MapGet("/",()=>Results.File(Path.Combine(root,"tests/Stage1.IdentityProbe/index.html"),"text/html"));
app.MapGet("/probe.js",()=>Results.File(Path.Combine(root,"tests/Stage1.IdentityProbe/probe.js"),"text/javascript"));
app.MapGet("/msal-browser.js",()=>Results.File(Path.Combine(root,"tests/Stage1.IdentityProbe/node_modules/@azure/msal-browser/lib/msal-browser.js"),"text/javascript"));
app.MapGet("/config",()=>Results.Json(new{authority,tenantId=tenant,clientId=ui,aquariumScope="api://"+aquarium+"/Aquarium.Read",trackingScope="api://"+tracking+"/Tracking.Read",requestKey,hosting=File.Exists(Path.Combine(root,"tests/Stage1.IdentityProbe/.hosting.json"))}));
var checks = new List<IdentityCheck>();
app.MapGet("/results",()=>Results.Json(checks));
// No data mutation: this Local probe exercises a real HTTP scope check only.
app.MapPost("/aquarium-write-probe",async(HttpContext context)=>{
    if(context.Request.Headers["X-Probe-Key"]!=requestKey)return Results.StatusCode(403);
    var authorization=context.Request.Headers.Authorization.ToString();
    if(!authorization.StartsWith("Bearer ",StringComparison.Ordinal))return Results.Unauthorized();
    var metadata=await manager.GetConfigurationAsync(context.RequestAborted);
    ClaimsPrincipal user;
    try{user=IdentityTokenRules.Validate(authorization[7..],aquarium,metadata);}
    catch(SecurityTokenException){return Results.Unauthorized();}
    return IdentityTokenRules.HasScope(user,"Aquarium.Write")?Results.NoContent():Results.StatusCode(403);
});
app.MapPost("/verify",async(HttpContext context)=>{
    if(context.Request.Headers.Origin!="http://localhost:4200" || context.Request.Headers["X-Probe-Key"]!=requestKey) return Results.StatusCode(403);
    context.Request.Body= new LimitedStream(context.Request.Body,64*1024);
    var tokens=await context.Request.ReadFromJsonAsync<ProbeTokens>();
    if(tokens is null) return Results.BadRequest();
    checks.Clear();
    async Task Check(string name,Func<Task> action){try{await action();checks.Add(new(name,true));}catch(Exception e){checks.Add(new(name,false,e is MsalException m?m.ErrorCode:e.GetType().Name));}}
    static void Ensure(bool condition){if(!condition)throw new InvalidOperationException();}
    var hostingPath=Path.Combine(root,"tests/Stage1.IdentityProbe/.hosting.json");
    if(File.Exists(hostingPath)) {
        using var hosting=JsonDocument.Parse(await File.ReadAllTextAsync(hostingPath));
        var gateway=hosting.RootElement.GetProperty("gateway").GetString()!;
        Ensure(gateway=="https://apim-adt-platform-dev.azure-api.net");
        var runId=hosting.RootElement.GetProperty("runId").GetString()!;
        using var remote=new HttpClient{Timeout=TimeSpan.FromSeconds(60)};
        async Task<(int Status,JsonElement? Body)> Call(string url,string token) {
            using var request=new HttpRequestMessage(HttpMethod.Get,url);
            request.Headers.Authorization=new("Bearer",token);
            using var response=await remote.SendAsync(request,context.RequestAborted);
            JsonElement? body=null;
            if(response.IsSuccessStatusCode){using var json=JsonDocument.Parse(await response.Content.ReadAsStringAsync());body=json.RootElement.Clone();}
            return ((int)response.StatusCode,body);
        }
        foreach(var service in new[]{"aquarium","tracking"}) {
            var path=hosting.RootElement.GetProperty("paths").GetProperty(service).GetString()!;
            Ensure(path=="pp-stage1-"+runId+"/"+service);
            var token=service=="aquarium"?tokens.AquariumToken:tokens.TrackingToken;
            var wrongToken=service=="aquarium"?tokens.TrackingToken:tokens.AquariumToken;
            await Check(service+"ValidTokenThroughApim",async()=>{var result=await Call(gateway+"/"+path+"/read",token);Ensure(result.Status==200 && result.Body?.GetProperty("run").GetString()==runId);});
            await Check(service+"DirectBackendValidTokenDenied",async()=>Ensure((await Call("https://api-adt-"+service+"-dev.azurewebsites.net/read",token)).Status==403));
            await Check(service+"WrongAudienceThroughApimDenied",async()=>Ensure((await Call(gateway+"/"+path+"/read",wrongToken)).Status==401));
            await Check(service+"TamperedSignatureThroughApimDenied",async()=>{var parts=token.Split('.');parts[2]=(parts[2][0]=='A'?"B":"A")+parts[2][1..];Ensure((await Call(gateway+"/"+path+"/read",string.Join('.',parts))).Status==401);});
        }
        await Check("deployedTrackingCertificateOboAndAquariumReadOnlyEnforcement",async()=>{
            var path=hosting.RootElement.GetProperty("paths").GetProperty("tracking").GetString()!;
            var result=await Call(gateway+"/"+path+"/obo",tokens.TrackingToken);
            Ensure(result.Status==200 && result.Body?.GetProperty("passed").GetBoolean()==true);
        });
        var hostedEvidence=new{date="2026-11-03",runId,passed=checks.All(c=>c.Passed),checks,limitations="Stateless verification endpoints, no business data or ownership feature implementation. Customer tokens remain in process memory only."};
        await File.WriteAllTextAsync(Path.Combine(root,"docs/infrastructure/evidence/hosting-customer-verification-2026-11-03.json"),JsonSerializer.Serialize(hostedEvidence,new JsonSerializerOptions{WriteIndented=true}));
        return Results.Json(hostedEvidence);
    }
    var configuration=await manager.GetConfigurationAsync(CancellationToken.None);
    ClaimsPrincipal Validate(string token,string audience,string? issuer=null){
        return IdentityTokenRules.Validate(token,audience,configuration,issuer);
    }
    static bool Scope(ClaimsPrincipal user,string name)=>IdentityTokenRules.HasScope(user,name);
    ClaimsPrincipal? aquariumUser=null,trackingUser=null;
    await Check("aquariumSignedTokenAudienceIssuerScope",()=>{aquariumUser=Validate(tokens.AquariumToken,aquarium);Ensure(Scope(aquariumUser,"Aquarium.Read") && aquariumUser.FindFirst("azp")?.Value==ui);return Task.CompletedTask;});
    await Check("trackingSignedTokenAudienceIssuerScope",()=>{trackingUser=Validate(tokens.TrackingToken,tracking);Ensure(Scope(trackingUser,"Tracking.Read") && trackingUser.FindFirst("azp")?.Value==ui);return Task.CompletedTask;});
    await Check("stableTenantAndObjectIdAcrossApis",()=>{Ensure(aquariumUser is not null && trackingUser is not null && aquariumUser.FindFirst("tid")?.Value==tenant && trackingUser.FindFirst("tid")?.Value==tenant && Guid.TryParse(aquariumUser.FindFirst("oid")?.Value,out var oid) && oid!=Guid.Empty && aquariumUser.FindFirst("oid")?.Value==trackingUser.FindFirst("oid")?.Value);return Task.CompletedTask;});
    await Check("trackingTokenContainsOnlyApprovedScopes",()=>{Ensure(trackingUser is not null && Scope(trackingUser,"Tracking.Read") && trackingUser.FindFirst("scp")!.Value.Split(' ',StringSplitOptions.RemoveEmptyEntries).All(scope=>scope is "Tracking.Read" or "Tracking.Write"));return Task.CompletedTask;});
    await Check("wrongServiceAudienceRejected",()=>{try{Validate(tokens.TrackingToken,aquarium);}catch(SecurityTokenInvalidAudienceException){return Task.CompletedTask;}throw new InvalidOperationException();});
    await Check("wrongIssuerRejected",()=>{try{Validate(tokens.TrackingToken,tracking,"https://login.microsoftonline.com/f4fcd45c-104f-4dd3-b7bf-3475e83ce097/v2.0");}catch(SecurityTokenInvalidIssuerException){return Task.CompletedTask;}throw new InvalidOperationException();});
    await Check("tamperedSignatureRejected",()=>{var parts=tokens.TrackingToken.Split('.');parts[2]=(parts[2][0]=='A'?"B":"A")+parts[2][1..];try{Validate(string.Join('.',parts),tracking);}catch(SecurityTokenInvalidSignatureException){return Task.CompletedTask;}throw new InvalidOperationException();});
    using var store=new X509Store(StoreName.My,StoreLocation.CurrentUser);
    store.Open(OpenFlags.ReadOnly);
    var certificate=store.Certificates.Find(X509FindType.FindByThumbprint,thumbprint,false).OfType<X509Certificate2>().Single();
    Ensure(certificate.HasPrivateKey && certificate.NotAfter.ToUniversalTime()>DateTime.UtcNow);
    var confidential=ConfidentialClientApplicationBuilder.Create(tracking).WithAuthority(authority).WithCertificate(certificate).Build();
    string? downstreamAccessToken=null;
    await Check("localCertificateAuthenticatedObo",async()=>{
        var result=await confidential.AcquireTokenOnBehalfOf(["api://"+aquarium+"/Aquarium.Read"],new UserAssertion(tokens.TrackingToken)).ExecuteAsync();
        var downstream=Validate(result.AccessToken,aquarium);
        Ensure(Scope(downstream,"Aquarium.Read") && downstream.FindFirst("azp")?.Value==tracking && downstream.FindFirst("oid")?.Value==trackingUser?.FindFirst("oid")?.Value && downstream.FindFirst("tid")?.Value==tenant);
        Ensure(!Scope(downstream,"Aquarium.Write"));
        downstreamAccessToken=result.AccessToken;
    });
    async Task<int> WriteProbe(string token){
        using var http=new HttpClient{Timeout=TimeSpan.FromSeconds(15)};
        using var request=new HttpRequestMessage(HttpMethod.Post,"http://localhost:4200/aquarium-write-probe");
        request.Headers.Authorization=new("Bearer",token);
        request.Headers.Add("X-Probe-Key",requestKey);
        using var result=await http.SendAsync(request);
        return (int)result.StatusCode;
    }
    await Check("readOnlyOboTokenWriteRequestDenied",async()=>{Ensure(downstreamAccessToken is not null);Ensure(await WriteProbe(downstreamAccessToken!)==403);});
    await Check("consentedUiWriteTokenPassesScopeProbe",async()=>{Ensure(aquariumUser is not null && Scope(aquariumUser,"Aquarium.Write"));Ensure(await WriteProbe(tokens.AquariumToken)==204);});
    await Check("wrongAudienceOboAssertionRejected",async()=>{
        try{await confidential.AcquireTokenOnBehalfOf(["api://"+aquarium+"/Aquarium.Read"],new UserAssertion(tokens.AquariumToken)).ExecuteAsync();}
        catch(MsalServiceException e) when(e.ErrorCode=="invalid_grant"){return;}
        throw new InvalidOperationException();
    });
    await Check("unconsentedDownstreamWriteRejected",async()=>{
        try{await confidential.AcquireTokenOnBehalfOf(["api://"+aquarium+"/Aquarium.Write"],new UserAssertion(tokens.TrackingToken)).ExecuteAsync();}
        catch(MsalServiceException e) when(e.ErrorCode is "invalid_grant" or "interaction_required"){return;}
        throw new InvalidOperationException();
    });
    var evidence=new{date="2026-11-03",tenantId=tenant,passed=checks.All(c=>c.Passed),checks,validatedTrackingScopes=trackingUser?.FindFirst("scp")?.Value.Split(' '),localCertificateThumbprint=thumbprint,readOnlyTest="Requires HTTP 403 for actual signed Aquarium.Read-only OBO token and HTTP 204 for the consented UI token positive control. Original incorrect request-scope-subset assumption retained in initial evidence.",limitations="Local verification client; no product API/ownership/APIM enforcement test. Development private-key loading has separate managed-identity evidence. Tokens/auth codes/private keys omitted."};
    await File.WriteAllTextAsync(Path.Combine(root,"docs/infrastructure/evidence/customer-identity-verification-2026-11-03.json"),JsonSerializer.Serialize(evidence,new JsonSerializerOptions{WriteIndented=true}));
    return Results.Json(evidence);
});
Console.WriteLine("Local identity verification ready at http://localhost:4200. Tokens are not logged.");
await app.RunAsync();

record ProbeTokens(string AquariumToken,string TrackingToken);
record IdentityCheck(string Name,bool Passed,string? Error=null);

static class IdentityTokenRules {
    public static ClaimsPrincipal Validate(string token,string audience,OpenIdConnectConfiguration configuration,string? issuer=null){
        var handler=new JwtSecurityTokenHandler{MapInboundClaims=false};
        return handler.ValidateToken(token,new TokenValidationParameters{ValidateIssuer=true,ValidIssuer=issuer??configuration.Issuer,ValidateAudience=true,ValidAudience=audience,ValidateIssuerSigningKey=true,IssuerSigningKeys=configuration.SigningKeys,ValidateLifetime=true,RequireExpirationTime=true,RequireSignedTokens=true,ClockSkew=TimeSpan.FromSeconds(60)},out _);
    }
    public static bool HasScope(ClaimsPrincipal user,string name)=>user.FindFirst("scp")?.Value.Split(' ',StringSplitOptions.RemoveEmptyEntries).Contains(name)==true;
}

sealed class LimitedStream(Stream inner,long limit):Stream {
    long count;
    public override bool CanRead=>true; public override bool CanSeek=>false;public override bool CanWrite=>false;public override long Length=>throw new NotSupportedException();public override long Position{get=>count;set=>throw new NotSupportedException();}
    public override int Read(byte[] buffer,int offset,int size){var read=inner.Read(buffer,offset,size);count+=read;if(count>limit)throw new InvalidOperationException();return read;}
    public override async ValueTask<int> ReadAsync(Memory<byte> buffer,CancellationToken cancellationToken=default){var read=await inner.ReadAsync(buffer,cancellationToken);count+=read;if(count>limit)throw new InvalidOperationException();return read;}
    public override void Flush()=>throw new NotSupportedException();public override long Seek(long offset,SeekOrigin origin)=>throw new NotSupportedException();public override void SetLength(long value)=>throw new NotSupportedException();public override void Write(byte[] buffer,int offset,int count)=>throw new NotSupportedException();
}
