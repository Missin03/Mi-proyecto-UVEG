#!/bin/sh
# Empaqueta, firma y sube Agenda Académica a App Store Connect.
# Se ejecuta en macOS con Xcode 16 o superior y una cuenta del Apple Developer Program.
# Uso: EQUIPO_APPLE=ABCDE12345 ./scripts/exportar_ipa.sh
set -e
cd "$(dirname "$0")/.."

npx cap sync ios                                   # copia www/ al proyecto nativo

# 1. Archivo (.xcarchive) en Release, firmado con el certificado "Apple Distribution"
xcodebuild -project ios/App/App.xcodeproj -scheme App -configuration Release \
  -destination 'generic/platform=iOS' -archivePath build/AgendaAcademica.xcarchive \
  DEVELOPMENT_TEAM="$EQUIPO_APPLE" -allowProvisioningUpdates archive

# 2. Exporta el .ipa con el perfil de aprovisionamiento de App Store
sed "s/\$(EQUIPO_APPLE)/$EQUIPO_APPLE/" ios/App/ExportOptions.plist > build/ExportOptions.plist
xcodebuild -exportArchive -archivePath build/AgendaAcademica.xcarchive \
  -exportOptionsPlist build/ExportOptions.plist -exportPath build/ipa -allowProvisioningUpdates

# 3. Comprueba la firma y el perfil incluidos en el .ipa
unzip -oq build/ipa/App.ipa -d build/ipa/contenido
codesign -dv --verbose=2 build/ipa/contenido/Payload/App.app
security cms -D -i build/ipa/contenido/Payload/App.app/embedded.mobileprovision | grep -A1 -E 'Name|TeamName'

# 4. Sube el build (también se puede arrastrar el .ipa a la app Transporter)
xcrun altool --upload-app -f build/ipa/App.ipa -t ios --apiKey "$ASC_KEY_ID" --apiIssuer "$ASC_ISSUER_ID"
