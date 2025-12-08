# GPU Setup for Docker

## Your GPU
- **Model**: NVIDIA GeForce RTX 3050 Laptop
- **VRAM**: 4GB
- **Driver**: 556.12
- **CUDA**: 12.5

## Prerequisites

### 1. Install NVIDIA Container Toolkit (if not already installed)

```bash
# Add NVIDIA Container Toolkit repository
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# Install the toolkit
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Configure Docker to use NVIDIA runtime
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

### 2. Verify GPU Access in Docker

```bash
docker run --rm --gpus all nvidia/cuda:12.5.0-base-ubuntu22.04 nvidia-smi
```

## Deploy with GPU

Once the NVIDIA Container Toolkit is installed, simply run:

```bash
./deploy-dev.sh
```

The backend will automatically use GPU if available. Check logs:

```bash
docker compose -f docker-compose.dev.yml logs backend | grep -i "device\|cuda\|gpu"
```

## Expected Performance Improvement

- **CPU inference**: 60-120 seconds per image
- **GPU inference**: 2-5 seconds per image (20-60x faster!)

## Important Notes

1. **VRAM Usage**: The InternVL3.5-1B model uses ~2GB VRAM in bfloat16
2. **Available VRAM**: You have 4GB, with ~3.2GB available for the model
3. **Model Loading**: First run will be slower as the model loads to GPU
4. **Automatic Fallback**: If GPU runs out of memory, the code automatically falls back to CPU

## Troubleshooting

### Check if Docker can see GPU
```bash
docker run --rm --gpus all ubuntu nvidia-smi
```

### Check backend GPU usage
```bash
docker compose -f docker-compose.dev.yml exec backend python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU count: {torch.cuda.device_count()}'); print(f'GPU name: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"
```

### Monitor GPU usage while inference is running
```bash
watch -n 0.5 nvidia-smi
```
