#!/bin/bash
# Script xóa tất cả cache Python trong dự án

echo "🧹 Đang xóa cache Python..."

# Xóa tất cả thư mục __pycache__ (trừ venv)
find . -type d -name "__pycache__" -not -path "./venv/*" -exec rm -rf {} + 2>/dev/null

# Xóa tất cả file .pyc
find . -type f -name "*.pyc" -not -path "./venv/*" -delete 2>/dev/null

# Xóa tất cả file .pyo
find . -type f -name "*.pyo" -not -path "./venv/*" -delete 2>/dev/null

# Xóa file .DS_Store (macOS)
find . -type f -name ".DS_Store" -not -path "./venv/*" -delete 2>/dev/null

echo "✅ Đã xóa xong tất cả cache!"

