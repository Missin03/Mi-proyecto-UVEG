# Revisa que el APK y el AAB de release estén firmados, optimizados y sin permisos peligrosos.
# Uso: powershell -File scripts\verificar.ps1   (antes: gradlew assembleRelease bundleRelease)
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$raiz = Split-Path $PSScriptRoot -Parent
$sdk = "$env:LOCALAPPDATA\Android\Sdk"
$bt = "$sdk\build-tools\36.0.0"
$env:JAVA_HOME = "$env:USERPROFILE\.jdks\jbr-21.0.11"
$apk = "$raiz\app\build\outputs\apk\release\app-release.apk"
$aab = "$raiz\app\build\outputs\bundle\release\app-release.aab"

function Titulo($t) { Write-Host ''; Write-Host "== $t ==" -ForegroundColor Green }

Titulo 'Archivos de distribucion'
foreach ($f in $apk, $aab) {
    $h = (Get-FileHash $f -Algorithm SHA256).Hash.ToLower()
    '{0,-16} {1,10:N0} bytes   SHA-256 {2}...' -f (Split-Path $f -Leaf), (Get-Item $f).Length, $h.Substring(0, 24)
}

Titulo 'Datos del paquete (aapt2 dump badging)'
& "$bt\aapt2.exe" dump badging $apk | Select-String "^(package|minSdkVersion|sdkVersion|targetSdkVersion|application-label:)" |
    ForEach-Object { ($_.Line -replace " platformBuildVersion.*", '') }

Titulo 'Permisos'
$permisos = & "$bt\aapt2.exe" dump permissions $apk | Select-String "uses-permission" | Where-Object { $_ -notmatch 'DYNAMIC_RECEIVER_NOT_EXPORTED' }
if ($permisos) { $permisos } else { 'Permisos del sistema solicitados: ninguno (sin internet, camara, ubicacion ni contactos)' }

Titulo 'Firma del APK (apksigner verify)'
& "$bt\apksigner.bat" verify --verbose --print-certs $apk | Select-String "^(Verified using v2|Number of signers|Signer #1 certificate DN)"

Titulo 'Firma del AAB (jarsigner -verify)'
& "$env:JAVA_HOME\bin\jarsigner.exe" -verify $aab | Select-String 'verified'

Titulo 'Validacion del AAB (bundletool validate)'
Push-Location $raiz
& "$raiz\gradlew.bat" -q :app:bundletool "-Pbt=validate --bundle=build/outputs/bundle/release/app-release.aab" 2>$null |
    Select-String 'App Bundle information|Version|Modules|Module:' | Select-Object -First 4
Pop-Location
