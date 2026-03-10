Write-Host ""
Write-Host "======================================="
Write-Host " MiniSoft Analytics Server Installer"
Write-Host "======================================="
Write-Host ""

$INSTALL_DIR = "C:\MiniReportServer"

# ------------------------------------------------
# CHECK PYTHON
# ------------------------------------------------

Write-Host "Checking Python..."

$python = Get-Command python -ErrorAction SilentlyContinue

if (!$python) {

    Write-Host "Python not found. Install Python first."
    exit
}

Write-Host "Python OK"
Write-Host ""

# ------------------------------------------------
# INSTALL PYTHON LIBRARIES
# ------------------------------------------------

Write-Host "Installing Python dependencies..."

python -m pip install -r "$INSTALL_DIR\requirements.txt"

Write-Host ""

# ------------------------------------------------
# CHECK WSL
# ------------------------------------------------

Write-Host "Checking WSL..."

wsl -l > $null 2>&1

if ($LASTEXITCODE -ne 0) {

    Write-Host "WSL not installed"
    Write-Host "Install WSL first: wsl --install -d Ubuntu"
    exit
}

Write-Host "WSL OK"
Write-Host ""

# ------------------------------------------------
# INSTALL UBUNTU DEPENDENCIES
# ------------------------------------------------

Write-Host "Installing Ubuntu dependencies..."

wsl bash /mnt/c/MiniReportServer/scripts/install_wsl_deps.sh

Write-Host ""

# ------------------------------------------------
# INSTALL / UPDATE DWH PLATFORM
# ------------------------------------------------

Write-Host "Installing DWH platform..."

$checkRepo = wsl bash -c "if [ -d /opt/dwh ]; then echo 1; else echo 0; fi"

if ($checkRepo -eq "1") {

    Write-Host "Updating existing platform..."

    wsl bash -c "cd /opt/dwh && git pull"

} else {

    Write-Host "Cloning platform..."

    wsl bash -c "sudo git clone https://github.com/arturhapurkhaiev/dwh-platform.git /opt/dwh"

}

# ------------------------------------------------
# FIX PERMISSIONS
# ------------------------------------------------

Write-Host "Fixing permissions..."

wsl bash -c "sudo chown -R \$USER:\$USER /opt/dwh"

Write-Host ""

# ------------------------------------------------
# COPY CONFIG
# ------------------------------------------------

Write-Host "Copying configuration..."

wsl bash -c "mkdir -p /opt/dwh/config"

if (Test-Path "$INSTALL_DIR\config\stores.json") {

    wsl bash -c "cp /mnt/c/MiniReportServer/config/stores.json /opt/dwh/config/"
}

if (Test-Path "$INSTALL_DIR\config\credentials.env") {

    wsl bash -c "cp /mnt/c/MiniReportServer/config/credentials.env /opt/dwh/config/"
}

Write-Host ""

# ------------------------------------------------
# START DOCKER
# ------------------------------------------------

Write-Host "Starting Docker..."

wsl bash -c "sudo service docker start"

Write-Host ""

# ------------------------------------------------
# BUILD PLATFORM
# ------------------------------------------------

Write-Host "Building platform..."

wsl bash -c "cd /opt/dwh && make build"
wsl bash -c "cd /opt/dwh && make up"

Write-Host ""

# ------------------------------------------------
# PLATFORM INIT
# ------------------------------------------------

Write-Host "Initializing platform..."

wsl bash -c "cd /opt/dwh && make platform"

Write-Host ""

# ------------------------------------------------
# REBUILD DWH
# ------------------------------------------------

Write-Host "Rebuilding DWH..."

wsl bash -c "cd /opt/dwh && make rebuild"

Write-Host ""
Write-Host "Server installation finished"
Write-Host ""
