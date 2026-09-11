```bash
# Gỡ bản cũ nếu có
pip uninstall torch torchvision torchaudio -y

# Bản pytorch hỗ trọ nvidia
# tải phiên bản 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
# Bản 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121


#script cmd kiểm tra (bật venv, trỏ đúng thư mục)
python -c "import torch; print('GPU hợp lệ:', torch.cuda.is_available())"
```
