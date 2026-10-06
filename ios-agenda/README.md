# Agenda Académica para iPhone y iPad

Versión iOS de la Agenda Académica, empaquetada con **Capacitor 8.5.2** (Ionic). Se preparó para el
**Reto 5** del módulo *Despliegue de aplicaciones web y móviles v2* (UVEG): proyecto de Xcode, recursos de
App Store y publicación **simulada** en App Store Connect, trabajando desde Windows.

- **Bundle Identifier:** `io.github.missin03.agendaacademica` · versión 1.0.0 (build 1) · iOS 15 o superior
- **Dispositivos:** iPhone y iPad
- **Privacidad:** sin cuentas, rastreo ni permisos; las tareas se guardan en el dispositivo.
  [Política de privacidad](PRIVACIDAD.md) y `PrivacyInfo.xcprivacy`
- **Exportación:** `ITSAppUsesNonExemptEncryption = NO`

## Estructura

```
ios-agenda/
├── www/                     # App web sin servidor (HTML, CSS y JS con almacenamiento local)
├── ios/App/                 # Proyecto de Xcode generado por Capacitor
│   ├── App/Info.plist
│   ├── App/PrivacyInfo.xcprivacy
│   └── ExportOptions.plist  # Exportación del .ipa para App Store Connect
├── appstore/                # Icono 1024, capturas, video de vista previa y consola simulada
└── scripts/                 # Recursos, video, verificación y exportación del .ipa
```

## En Windows

```powershell
npm install
npx cap sync ios                   # copia www/ al proyecto de Xcode
python scripts\recursos_ios.py     # icono, splash y capturas (WebKit: iPhone 6.9" e iPad 13")
python scripts\video_promocional.py
python scripts\verificar_ios.py    # 17 revisiones del proyecto antes de archivar
```

## En macOS (firma y carga)

Requiere Xcode 16 o superior y una cuenta del Apple Developer Program:

```sh
EQUIPO_APPLE=ABCDE12345 ASC_KEY_ID=... ASC_ISSUER_ID=... ./scripts/exportar_ipa.sh
```

El script archiva en Release, exporta el `.ipa` con `ExportOptions.plist`, comprueba la firma con `codesign` y
lo sube a App Store Connect (también se puede usar la app Transporter).

## App Store Connect simulada

`appstore/connect/index.html` reproduce los pasos de publicación: firma y archivo en Xcode (maqueta), nueva
app, TestFlight, metadatos, clasificación por edades, privacidad, precios y envío a revisión. Es una
**simulación académica** que toma los valores reales del proyecto (`datos.js`, generado por
`verificar_ios.py`); no se conecta con Apple.
