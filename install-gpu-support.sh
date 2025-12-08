#!/bin/bash
set -e

echo "==================================="
echo "NVIDIA Container Toolkit Installer"
echo "==================================="
echo ""

# Check if nvidia-smi is available
if ! command -v nvidia-smi &> /dev/null; then
    echo "❌ Error: nvidia-smi not found. Please install NVIDIA drivers first."
    exit 1
fi

echo "✓ NVIDIA drivers detected"
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
echo ""

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VERSION=$VERSION_ID
    echo "✓ Detected OS: $OS $VERSION"
else
    echo "❌ Cannot detect OS"
    exit 1
fi

# Add NVIDIA Container Toolkit repository
echo ""
echo "Adding NVIDIA Container Toolkit repository..."
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)

curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# Update package list
echo ""
echo "Updating package list..."
sudo apt-get update

# Install NVIDIA Container Toolkit
echo ""
echo "Installing NVIDIA Container Toolkit..."
sudo apt-get install -y nvidia-container-toolkit

# Configure Docker
echo ""
echo "Configuring Docker to use NVIDIA runtime..."
sudo nvidia-ctk runtime configure --runtime=docker

# Restart Docker
echo ""
echo "Restarting Docker daemon..."
sudo systemctl restart docker

# Wait a moment for Docker to restart
sleep 3

# Test GPU access in Docker
echo ""
echo "Testing GPU access in Docker..."
if docker run --rm --gpus all nvidia/cuda:12.5.0-base-ubuntu22.04 nvidia-smi &> /dev/null; then
    echo "✓ GPU access in Docker verified successfully!"
else
    echo "⚠ Warning: GPU test failed. You may need to restart your system."
fi

echo ""
echo "==================================="
echo "✓ Installation Complete!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Deploy with GPU: ./deploy-dev.sh"
echo "2. Check GPU usage: watch nvidia-smi"
echo "3. View logs: docker compose -f docker-compose.dev.yml logs backend"
echo ""
