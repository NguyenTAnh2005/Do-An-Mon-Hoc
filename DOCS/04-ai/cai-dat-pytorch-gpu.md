# Cài đặt PyTorch có hỗ trợ GPU (CUDA)

> **Mục đích file này:** các lệnh cần chạy để cài lại PyTorch bản hỗ trợ GPU NVIDIA, dùng khi train YOLOv8 trên máy có RTX (vd Asus TUF A15 FA507NU — RTX 4050).

```bash
# Gỡ bản cũ nếu có
pip uninstall torch torchvision torchaudio -y

# Bản PyTorch hỗ trợ NVIDIA — chọn 1 trong 2 tuỳ driver CUDA đang có
# CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
# CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Script kiểm tra (bật venv, trỏ đúng thư mục)
python -c "import torch; print('GPU hợp lệ:', torch.cuda.is_available())"
```
