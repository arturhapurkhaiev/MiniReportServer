Write-Host ""
Write-Host "MiniSoft Analytics Server Installer"
Write-Host ""

# --------------------------------
# Install Python libraries
# --------------------------------

Write-Host "Installing Python dependencies..."

pip install -r ..\requirements.txt

# --------------------------------
# Install WSL dependencies
# --------------------------------

Write-Host ""
Write-Host "Installing WSL dependencies..."

wsl -d Ubuntu bash -c "bash /mnt/c/MiniReportServer/scripts/install_wsl_deps.sh"

# --------------------------------
# Clone DWH platform
# --------------------------------

Write-Host ""
Write-Host "Cloning DWH platform..."

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
# Build docker image
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

Start-Sleep -Seconds 8

# --------------------------------
# Generate FDW + build DWH
# --------------------------------

Write-Host ""
Write-Host "Building DWH..."

wsl -d Ubuntu bash -c "cd /opt/dwh && make platform"

wsl -d Ubuntu bash -c "cd /opt/dwh && make rebuild"

Write-Host ""
Write-Host "Installation completed"
Write-Host ""
Write-Host "Open reports:"
Write-Host "http://localhost:3000"
