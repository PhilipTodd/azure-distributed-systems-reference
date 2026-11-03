using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Security.Cryptography;
using System.Security.Cryptography.X509Certificates;
using System.Text.Json;
using Azure.Core;
using Azure.Identity;
using Microsoft.Identity.Client;
using Microsoft.IdentityModel.Protocols;
using Microsoft.IdentityModel.Protocols.OpenIdConnect;
using Microsoft.IdentityModel.Tokens;

// Temporary, stateless hosting gate. No business data, user claims or tokens are logged.
const string tenant = "0e9365ce-9928-49a0-a455-73c5ad29cf34";
const string authority = "https://parameterpilotdev.ciamlogin.com/" + tenant;
const string aquarium = "bcbab13c-f80e-4dc3-8e12-f94bc2491461";
const string tracking = "df2085cf-7b78-4c21-99fb-70f46b48490a";
const string ui = "fc5f67a2-e6a2-4e3f-a49b-2b2410a6060b";
var role = Environment.GetEnvironmentVariable("WEBSITE_SITE_NAME") switch {
    "api-adt-aquarium-dev" => "aquarium", "api-adt-tracking-dev" => "tracking",
    _ => throw new InvalidOperationException("Only the two authorised PP hosts are supported")
};
var settings = JsonDocument.Parse(File.ReadAllText("probe-settings.json"));
var run = settings.RootElement.GetProperty("RunId").GetString()!;
var backend = settings.RootElement.GetProperty("AquariumUrl").GetString()!;
if (backend != "https://api-adt-aquarium-dev.azurewebsites.net")
    throw new InvalidOperationException("Unexpected Aquarium backend");
var metadata = new ConfigurationManager<OpenIdConnectConfiguration>(authority + "/v2.0/.well-known/openid-configuration", new OpenIdConnectConfigurationRetriever());
var builder = WebApplication.CreateBuilder(args);
builder.Logging.ClearProviders();
builder.WebHost.ConfigureKestrel(options => options.Limits.MaxRequestBodySize = 1024);
var app = builder.Build();
var started = DateTimeOffset.UtcNow;
using var http = new HttpClient { Timeout = TimeSpan.FromSeconds(30) };
X509Certificate2? certificate = null;
IConfidentialClientApplication? confidential = null;
if (role == "tracking") {
    // Only the real Tracking MI can retrieve its own certificate. Key stays in process memory.
    var secretUri = settings.RootElement.GetProperty("CertificateSecretUri").GetString()!;
    if (!secretUri.StartsWith("https://kv-adt-tracking-dev.vault.azure.net/secrets/tracking-obo-dev/", StringComparison.Ordinal))
        throw new InvalidOperationException("Unexpected certificate reference");
    var credential = new ManagedIdentityCredential(ManagedIdentityId.SystemAssigned);
    var token = await credential.GetTokenAsync(new TokenRequestContext(["https://vault.azure.net/.default"]));
    using var request = new HttpRequestMessage(HttpMethod.Get, secretUri + "?api-version=7.4");
    request.Headers.Authorization = new("Bearer", token.Token);
    using var response = await http.SendAsync(request);
    response.EnsureSuccessStatusCode();
    using var secret = JsonDocument.Parse(await response.Content.ReadAsStringAsync());
    var pfx = Convert.FromBase64String(secret.RootElement.GetProperty("value").GetString()!);
    try { certificate = X509CertificateLoader.LoadPkcs12(pfx, "", X509KeyStorageFlags.EphemeralKeySet); }
    finally { CryptographicOperations.ZeroMemory(pfx); }
    if (certificate.Thumbprint != settings.RootElement.GetProperty("CertificateThumbprint").GetString())
        throw new InvalidOperationException("Certificate mismatch");
    confidential = ConfidentialClientApplicationBuilder.Create(tracking).WithAuthority(authority).WithCertificate(certificate).Build();
}
app.Use(async (context, next) => {
    context.Response.Headers.CacheControl = "no-store";
    context.Response.Headers["X-PP-Hosting-Probe"] = run;
    if (context.Request.Path == "/health") { await next(); return; }
    var bearer = context.Request.Headers.Authorization.ToString();
    if (!bearer.StartsWith("Bearer ", StringComparison.Ordinal) || bearer.Length > 32768) { context.Response.StatusCode = 401; return; }
    try {
        var config = await metadata.GetConfigurationAsync(context.RequestAborted);
        var handler = new JwtSecurityTokenHandler { MapInboundClaims = false };
        context.User = handler.ValidateToken(bearer[7..], new TokenValidationParameters {
            ValidateIssuer = true, ValidIssuer = config.Issuer, ValidateAudience = true, ValidAudience = role == "aquarium" ? aquarium : tracking,
            ValidateIssuerSigningKey = true, IssuerSigningKeys = config.SigningKeys, ValidateLifetime = true,
            RequireExpirationTime = true, RequireSignedTokens = true, ClockSkew = TimeSpan.FromSeconds(60)
        }, out _);
        if (context.User.FindFirst("tid")?.Value != tenant || !Guid.TryParse(context.User.FindFirst("oid")?.Value, out var oid) || oid == Guid.Empty) { context.Response.StatusCode = 403; return; }
        var caller = context.User.FindFirst("azp")?.Value;
        var scope = (role == "aquarium" ? "Aquarium" : "Tracking") + (context.Request.Path == "/write" ? ".Write" : ".Read");
        if (!(caller == ui || (role == "aquarium" && caller == tracking)) || context.User.FindFirst("scp")?.Value.Split(' ').Contains(scope) != true) { context.Response.StatusCode = 403; return; }
        await next();
    } catch (SecurityTokenException) { context.Response.StatusCode = 401; }
});
app.MapGet("/health", () => Results.Json(new { role, run, started }));
app.MapGet("/read", () => Results.Json(new { role, run, authenticated = true }));
// No write occurs: this endpoint tests scope enforcement only.
app.MapPost("/write", () => Results.NoContent());
if (role == "tracking") {
    app.MapGet("/obo", async (HttpContext context) => {
        try {
            var result = await confidential!.AcquireTokenOnBehalfOf(["api://" + aquarium + "/Aquarium.Read"], new UserAssertion(context.Request.Headers.Authorization.ToString()[7..])).ExecuteAsync(context.RequestAborted);
            async Task<int> Call(string path, HttpMethod method, string? bearer) {
                using var request = new HttpRequestMessage(method, backend + path);
                if (bearer is not null) request.Headers.Authorization = new("Bearer", bearer);
                using var response = await http.SendAsync(request, context.RequestAborted);
                return (int)response.StatusCode;
            }
            var read = await Call("/read", HttpMethod.Get, result.AccessToken);
            var write = await Call("/write", HttpMethod.Post, result.AccessToken);
            var unauthenticated = await Call("/read", HttpMethod.Get, null);
            // Original Tracking-audience token represents a same-origin caller lacking Aquarium authority.
            var wrongAudience = await Call("/read", HttpMethod.Get, context.Request.Headers.Authorization.ToString()[7..]);
            return Results.Json(new { read, write, unauthenticated, wrongAudience, passed = read == 200 && write == 403 && unauthenticated == 401 && wrongAudience == 401 });
        } catch (MsalException) { return Results.StatusCode(502); }
    });
}
app.Lifetime.ApplicationStopped.Register(() => certificate?.Dispose());
await app.RunAsync();
