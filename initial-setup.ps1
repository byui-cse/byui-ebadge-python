<#
.SYNOPSIS
Downloads MicroPython firmware, flashes an eBadge, and deploys the logo example.

.DESCRIPTION
Run this script from PowerShell on Windows. esptool and deploy.py use automatic
serial-port detection; the script does not specify a port.
#>

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $RepoRoot

$AssetsDir = Join-Path $RepoRoot "assets"
$FirmwareName = "ESP32_GENERIC_S3-20260824-v1.29.0.bin"
$FirmwareUrl = "https://micropython.org/resources/firmware/$FirmwareName"
$FirmwarePath = Join-Path $AssetsDir $FirmwareName
$LogoPath = Join-Path $AssetsDir "lego-python_badge.bmp"
$DeployScript = Join-Path $RepoRoot "deploy.py"
$ExampleScript = Join-Path $RepoRoot "examples\04_display_logo.py"

New-Item -ItemType Directory -Path $AssetsDir -Force | Out-Null

$PythonCommand = $null
$PythonPrefixArgs = @()
if (Get-Command py -CommandType Application -ErrorAction SilentlyContinue) {
    $PythonCommand = "py"
    $PythonPrefixArgs = @("-3")
} elseif (Get-Command python -CommandType Application -ErrorAction SilentlyContinue) {
    $PythonCommand = "python"
} else {
    throw "Python 3 is required. Install Python and retry."
}

foreach ($RequiredPath in @($DeployScript, $ExampleScript, $LogoPath)) {
    if (-not (Test-Path -LiteralPath $RequiredPath -PathType Leaf)) {
        throw "Required project file is missing: $RequiredPath"
    }
}

& $PythonCommand @PythonPrefixArgs -c "import esptool, mpremote"
if ($LASTEXITCODE -ne 0) {
    throw "Install the host tools first: $PythonCommand -m pip install esptool mpremote"
}

if ((Test-Path -LiteralPath $FirmwarePath -PathType Leaf) -and
    (Get-Item -LiteralPath $FirmwarePath).Length -gt 0) {
    Write-Host "Using existing firmware: $FirmwarePath"
} else {
    $DownloadTemp = "$FirmwarePath.part"
    try {
        Write-Host "Downloading MicroPython firmware to $FirmwarePath"
        Invoke-WebRequest -Uri $FirmwareUrl -OutFile $DownloadTemp
        Move-Item -LiteralPath $DownloadTemp -Destination $FirmwarePath -Force
    } catch {
        Remove-Item -LiteralPath $DownloadTemp -Force -ErrorAction SilentlyContinue
        throw
    }
}

Write-Host "Erasing flash and installing MicroPython (esptool will detect the port)."
& $PythonCommand @PythonPrefixArgs -m esptool erase_flash
if ($LASTEXITCODE -ne 0) {
    throw "esptool could not erase the board flash."
}

& $PythonCommand @PythonPrefixArgs -m esptool --baud 460800 write_flash 0 $FirmwarePath
if ($LASTEXITCODE -ne 0) {
    throw "esptool could not write the firmware."
}

Write-Host "Deploying the eBadge library, prepared Python logo, and example 04."
Write-Host "Waiting for the firmware's first-boot filesystem setup to finish."
Start-Sleep -Seconds 3

$DeploymentSucceeded = $false
for ($Attempt = 1; $Attempt -le 3; $Attempt++) {
    & $PythonCommand @PythonPrefixArgs $DeployScript --install-library --asset $LogoPath $ExampleScript
    if ($LASTEXITCODE -eq 0) {
        $DeploymentSucceeded = $true
        break
    }
    if ($Attempt -lt 3) {
        Write-Warning "Deployment did not connect (attempt $Attempt/3); retrying in 3 seconds."
        Start-Sleep -Seconds 3
    }
}
if (-not $DeploymentSucceeded) {
    throw "deploy.py could not install the library and logo example after 3 attempts."
}

Write-Host "Setup complete. Power-cycle the badge or press its reset button to run the logo example."
