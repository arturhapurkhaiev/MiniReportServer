Write-Host ""
Write-Host "======================================="
Write-Host " MiniSoft Analytics Server Installer"
Write-Host "======================================="
Write-Host ""

# --------------------------------
# Check Python
# --------------------------------

Write-Host "Checking Python..."

$python = Get-Command python -ErrorAction SilentlyContinue

if (!$python) {
    Write-Host "Python not found. Install Python first."
    exit
}

Write-Host "Python OK"

# --------------------------------
# Install Python libraries
# --------------------------------

Write-Host ""
Write-Host "Installing Python dependencies..."

pip install -r ..\requirements.txt

# --------------------------------
# Check WSL
# --------------------------------

Write-Host ""
Write-Host "Checking WSL..."

$wsl = wsl -l -q

if (!$wsl) {

    Write-Host "WSL not installed. Installing..."

    wsl --install -d Ubuntu

    Write-Host "Restart Windows and run installer again."
    exit
}

Write-Host "WSL OK"

# --------------------------------
# Install Ubuntu dependencies
# --------------------------------

Write-Host ""
Write-Host "Installing Ubuntu packages..."

wsl -d Ubuntu bash -c "bash /mnt/c/MiniReportServer/scripts/install_wsl_deps.sh"

# --------------------------------
# Clone DWH platform
# --------------------------------

Write-Host ""
Write-Host "Deploying DWH platform..."

wsl -d Ubuntu sudo rm -rf /opt/dwh

wsl -d Ubuntu sudo git clone https://github.com/arturhapurkhaiev/dwh-platform.git /opt/dwh

# --------------------------------
# Copy config
# --------------------------------

Write-Host ""
Write-Host "Copying configuration..."

wsl -d Ubuntu mkdir -p /opt/dwh/config

wsl -d Ubuntu cp /mnt/c/MiniReportServer/config/stores.json /opt/dwh/config/

wsl -d Ubuntu cp /mnt/c/MiniReportServer/config/credentials.env /opt/dwh/config/

# --------------------------------
# Build Docker
# --------------------------------

Write-Host ""
Write-Host "Building docker images..."

wsl -d Ubuntu bash -c "cd /opt/dwh && make build"

# --------------------------------
# Start platform
# --------------------------------

Write-Host ""
Write-Host "Starting platform..."

wsl -d Ubuntu bash -c "cd /opt/dwh && make up"

Start-Sleep -Seconds 10

# --------------------------------
# Generate FDW
# --------------------------------

Write-Host ""
Write-Host "Generating FDW..."

wsl -d Ubuntu bash -c "cd /opt/dwh && make platform"

# --------------------------------
# Build DWH
# --------------------------------

Write-Host ""
Write-Host "Building DWH..."

wsl -d Ubuntu bash -c "cd /opt/dwh && make rebuild"

# --------------------------------
# Done
# --------------------------------

Write-Host ""
Write-Host "======================================="
Write-Host " Installation completed"
Write-Host "======================================="
Write-Host ""
Write-Host "Open reports:"
Write-Host "http://localhost:3000"
Write-Host ""
