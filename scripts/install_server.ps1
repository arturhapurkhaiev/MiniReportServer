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

wsl -l > $null

if ($LASTEXITCODE -ne 0) {

    Write-Host "WSL not installed"
    exit
}

Write-Host "WSL OK"
Write-Host ""

# ------------------------------------------------
# INSTALL UBUNTU PACKAGES
# ------------------------------------------------

Write-Host "Installing Ubuntu packages..."

wsl bash /mnt/c/MiniReportServer/scripts/install_wsl_deps.sh

Write-Host ""

# ------------------------------------------------
# CLONE DWH PLATFORM
# ------------------------------------------------

Write-Host "Installing DWH platform..."

wsl bash -c "sudo rm -rf /opt/dwh"
wsl bash -c "sudo git clone https://github.com/arturhapurkhaiev/dwh-platform.git /opt/dwh"

Write-Host ""

# ------------------------------------------------
# COPY CONFIG
# ------------------------------------------------

Write-Host "Copying configuration..."

wsl bash -c "sudo mkdir -p /opt/dwh/config"

wsl bash -c "sudo cp /mnt/c/MiniReportServer/config/stores.json /opt/dwh/config/"
wsl bash -c "sudo cp /mnt/c/MiniReportServer/config/credentials.env /opt/dwh/config/"

Write-Host ""

# ------------------------------------------------
# BUILD PLATFORM
# ------------------------------------------------

Write-Host "Building platform..."

wsl bash -c "cd /opt/dwh && make build"
wsl bash -c "cd /opt/dwh && make up"
wsl bash -c "cd /opt/dwh && make platform"
wsl bash -c "cd /opt/dwh && make rebuild"

Write-Host ""
Write-Host "Server installation finished"
Write-Host ""
