@echo off
setlocal enabledelayedexpansion

rem Create target folders if they don't exist
if not exist static\css mkdir static\css
if not exist static\js mkdir static\js

set "URL_CSS=https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css"
set "URL_JS=https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"
set "OUT_CSS=static\css\bootstrap.min.css"
set "OUT_JS=static\js\bootstrap.bundle.min.js"

echo Downloading Bootstrap files...

call :fetch "%URL_CSS%" "%OUT_CSS%" || goto :error
call :fetch "%URL_JS%" "%OUT_JS%" || goto :error

echo Bootstrap files downloaded successfully!
exit /b 0

:fetch
setlocal enabledelayedexpansion
set "url=%~1"
set "out=%~2"
set /a tries=0

:tryagain
set /a tries+=1

rem Prefer curl if available
where curl >nul 2>&1
if !errorlevel! equ 0 (
    curl -fsSL "!url!" -o "!out!"
) else (
    rem Fallback to PowerShell's Invoke-WebRequest; expand batch variables before calling PowerShell
    powershell -NoProfile -Command "try { Invoke-WebRequest -Uri '!url!' -OutFile '!out!' -ErrorAction Stop } catch { exit 1 }"
)

rem Verify the file was created
if exist "!out!" (
    endlocal & exit /b 0
)

rem Retry up to 3 times
if !tries! lss 3 (
    timeout /t 1 >nul
    goto tryagain
)

endlocal & exit /b 1

:error
echo Failed to download %~2 after multiple attempts.
exit /b 1
