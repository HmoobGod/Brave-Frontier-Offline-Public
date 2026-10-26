@echo off
setlocal EnableExtensions
cd /d "%~dp0"
echo.
echo Brave Frontier Global - Offline Android Demo v0.13.1

echo -----------------------------------------------
set "ANDROID_SDK_ROOT=%LOCALAPPDATA%\Android\Sdk"
if defined ANDROID_HOME set "ANDROID_SDK_ROOT=%ANDROID_HOME%"
if not exist "%ANDROID_SDK_ROOT%\platforms\android-35\android.jar" (
  echo Missing Android SDK API 35 at:
  echo %ANDROID_SDK_ROOT%\platforms\android-35
  echo Install Android Studio and SDK Platform 35 first.
  echo Open https://developer.android.com/studio for official download.
  pause
  exit /b 1
)
if not defined JAVA_HOME (
  if exist "%ProgramFiles%\Android\Android Studio\jbr\bin\java.exe" (
    set "JAVA_HOME=%ProgramFiles%\Android\Android Studio\jbr"
  )
)
if defined JAVA_HOME (
  set "PATH=%JAVA_HOME%\bin;%PATH%"
)
where java >nul 2>&1 || (echo Java 17+ is required. Install Android Studio. & pause & exit /b 1)
set "GRADLEBIN=%~dp0.tools\gradle-8.9\bin\gradle.bat"
if not exist "%GRADLEBIN%" (
  echo Downloading the official Gradle 8.9 distribution - one-time setup...
  powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; $d=Join-Path $PWD '.tools'; New-Item -Force -ItemType Directory $d | Out-Null; $url='https://services.gradle.org/distributions/gradle-8.9-bin.zip'; $zip=Join-Path $d 'gradle-8.9-bin.zip'; Invoke-WebRequest -Uri $url -OutFile $zip; Expand-Archive -Path $zip -DestinationPath $d -Force"
  if errorlevel 1 (echo Could not download Gradle. Check your internet connection. & pause & exit /b 1)
)
echo Building debug APK (this may take several minutes the first time)...
call "%GRADLEBIN%" --no-daemon assembleDebug
if errorlevel 1 (echo Build failed. Copy the Gradle error here so we can troubleshoot. & pause & exit /b 1)
echo.
echo BUILD SUCCESS. Your APK is here:
echo %~dp0app\build\outputs\apk\debug\app-debug.apk
start "" "%~dp0app\build\outputs\apk\debug"
pause
