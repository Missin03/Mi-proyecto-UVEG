# Agenda Académica para Android

Versión móvil de la Agenda Académica (Retos 2 y 3). Permite registrar tareas escolares por materia,
fecha de entrega y estado. Se preparó para el **Reto 4** del módulo *Despliegue de aplicaciones web y
móviles v2* (UVEG): empaquetado AAB firmado y publicación **simulada** en Google Play.

- **Paquete:** `io.github.missin03.agendaacademica` · versión 1.0.0 (código 1)
- **SDK:** mínimo 26 (Android 8.0), objetivo y compilación 36
- **Tecnologías:** Java 17, AndroidX AppCompat 1.7.0, Material Components 1.12.0, SQLite
- **Permisos:** ninguno. Sin internet, anuncios ni cuentas. [Política de privacidad](PRIVACIDAD.md)

## Estructura

```
android-agenda/
├── app/src/main/java/.../  # MainActivity, TareaActivity, LegalActivity, BaseDatos
├── app/src/main/res/       # Diseños, textos, icono adaptable y reglas de respaldo
├── play/                   # Icono 512, gráfico 1024x500, capturas y consola simulada
└── scripts/                # Verificación, recursos gráficos, emulador y capturas
```

## Compilar la versión firmada

Requisitos: JDK 21 (el de Android Studio sirve) y Android SDK 36.

1. Crear la llave de subida fuera del repositorio:
   ```powershell
   keytool -genkeypair -keystore upload-keystore.jks -storetype PKCS12 -alias subida -keyalg RSA -keysize 4096 -validity 10000
   ```
2. Crear `keystore.properties` (ignorado por Git) con `storeFile`, `storePassword`, `keyAlias` y `keyPassword`.
3. Compilar y verificar:
   ```powershell
   .\gradlew.bat clean bundleRelease assembleRelease lintRelease
   .\scripts\verificar.ps1
   ```

Salidas: `app/build/outputs/bundle/release/app-release.aab` y `app/build/outputs/apk/release/app-release.apk`.

## Simular la entrega de Google Play

`bundletool` genera los APK divididos a partir del AAB, como lo hace la tienda, e instala solo los que
necesita el dispositivo conectado:

```powershell
.\gradlew.bat :app:bundletool "-Pbt=build-apks --bundle=build/outputs/bundle/release/app-release.aab --output=build/outputs/agenda.apks --ks=RUTA.jks --ks-key-alias=subida --ks-pass=file:RUTA.pass --aapt2=RUTA/aapt2.exe"
.\gradlew.bat :app:bundletool "-Pbt=install-apks --apks=build/outputs/agenda.apks"
```

## Consola de publicación simulada

`play/consola/index.html` reproduce los apartados de Play Console: crear app, ficha, categoría y
contacto, contenido de la app, carga del AAB, precios y países, y checklist con envío a revisión. Es una
**simulación académica**: no se conecta con Google. Al cargar el AAB, el navegador calcula su SHA-256 y
lo compara con el de la compilación (`scripts/datos_consola.py` genera `datos.js`).

```powershell
python scripts\datos_consola.py      # datos del AAB real
python scripts\capturas_consola.py   # capturas de cada sección con Edge
```
