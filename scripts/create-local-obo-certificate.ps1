param([switch]$Apply)
$ErrorActionPreference = 'Stop'
# Noninteractive child PowerShell sessions may not have loaded Cert: yet.
Import-Module "$PSHOME\Modules\Microsoft.PowerShell.Security\Microsoft.PowerShell.Security.psd1"
Import-Module "$env:windir\System32\WindowsPowerShell\v1.0\Modules\PKI\PKI.psd1"
$subject = 'CN=Parameter Pilot Tracking OBO Local Dev'
$existing = @(Get-ChildItem Cert:\CurrentUser\My | Where-Object Subject -eq $subject)
if ($existing.Count -gt 1) { throw 'Multiple Local OBO certificates require explicit reconciliation.' }
if ($existing.Count -eq 0) {
    if (-not $Apply) { Write-Output '{"apply":false,"certificateAbsent":true}'; exit 0 }
    $cert = New-SelfSignedCertificate -Type Custom -Subject $subject `
        -FriendlyName 'Parameter Pilot Tracking OBO Local Dev' `
        -CertStoreLocation Cert:\CurrentUser\My -KeyAlgorithm RSA -KeyLength 3072 `
        -HashAlgorithm SHA256 -KeySpec Signature -KeyUsage DigitalSignature `
        -KeyExportPolicy NonExportable -NotAfter (Get-Date).AddMonths(12) `
        -TextExtension @('2.5.29.37={text}1.3.6.1.5.5.7.3.2')
} else { $cert = $existing[0] }
if (-not $cert.HasPrivateKey -or $cert.NotAfter -le (Get-Date)) { throw 'Local certificate missing private key or expired.' }
$rsa = [System.Security.Cryptography.X509Certificates.RSACertificateExtensions]::GetRSAPrivateKey($cert)
try {
    if ($rsa -isnot [System.Security.Cryptography.RSACng] -or [int]$rsa.Key.ExportPolicy -ne 0) {
        throw 'Expected a non-exportable Windows CNG private key.'
    }
} finally { $rsa.Dispose() }
@{
    thumbprint = $cert.Thumbprint
    subject = $cert.Subject
    notBefore = $cert.NotBefore.ToUniversalTime().ToString('o')
    notAfter = $cert.NotAfter.ToUniversalTime().ToString('o')
    store = 'CurrentUser/My'
    privateKeyExportable = $false
    publicCertificate = [Convert]::ToBase64String($cert.RawData)
} | ConvertTo-Json -Compress
