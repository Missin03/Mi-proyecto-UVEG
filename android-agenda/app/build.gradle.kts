import java.util.Properties

plugins {
    id("com.android.application")
}

val bundletool: Configuration by configurations.creating

// La llave de subida vive fuera del repositorio; keystore.properties indica su ruta y contraseñas.
val firma = Properties().apply {
    val archivo = rootProject.file("keystore.properties")
    if (archivo.exists()) archivo.inputStream().use { load(it) }
}

android {
    namespace = "io.github.missin03.agendaacademica"
    compileSdk = 36

    defaultConfig {
        applicationId = "io.github.missin03.agendaacademica"
        minSdk = 26
        targetSdk = 36
        versionCode = 1
        versionName = "1.0.0"
    }

    androidResources {
        localeFilters += listOf("es")
    }

    signingConfigs {
        if (!firma.isEmpty) {
            create("subida") {
                storeFile = file(firma.getProperty("storeFile"))
                storePassword = firma.getProperty("storePassword")
                keyAlias = firma.getProperty("keyAlias")
                keyPassword = firma.getProperty("keyPassword")
            }
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
            if (!firma.isEmpty) signingConfig = signingConfigs.getByName("subida")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    lint {
        htmlReport = true
        abortOnError = false
    }
}

dependencies {
    implementation("androidx.appcompat:appcompat:1.7.0")
    implementation("com.google.android.material:material:1.12.0")
    bundletool("com.android.tools.build:bundletool:1.18.1")
    bundletool("org.jetbrains.kotlin:kotlin-stdlib:2.2.0") // la requiere install-apks (ddmlib)
}

// bundletool revisa el AAB y genera los APK divididos, igual que Google Play al entregar la app.
// Ejemplo: gradlew :app:bundletool -Pbt="validate --bundle=build/outputs/bundle/release/app-release.aab"
tasks.register<JavaExec>("bundletool") {
    classpath = bundletool
    mainClass.set("com.android.tools.build.bundletool.BundleToolMain")
    workingDir = projectDir
    args((findProperty("bt") as String? ?: "version").split(" "))
}
