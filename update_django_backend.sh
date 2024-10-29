#!/bin/bash

# Thư mục đích
TARGET_DIR="django_backend"

# Danh sách các thư mục cần loại trừ
EXCLUSIVE=("model_api" ".git" ".gitignore" "nginx_service" ".env" "Docker-compose.yaml" "update_django_backend.sh")

# Tạo thư mục đích nếu chưa tồn tại
mkdir -p "$TARGET_DIR"

# Di chuyển các file và thư mục trừ các thư mục trong danh sách EXCLUSIVE
for item in *; do
  if [[ ! " ${EXCLUSIVE[@]} " =~ " ${item} " ]]; then
    mv "$item" "$TARGET_DIR/"
  fi
done
