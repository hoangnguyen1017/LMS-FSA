#!/bin/bash

# Thư mục đích
TARGET_DIR="django_backend"

rm -rf "$TARGET_DIR"
git checkout main .
# Danh sách các thư mục cần loại trừ
EXCLUSIVE=(".git" ".gitignore" ".venv" ".env" "model_api" "nginx_service" "Docker-compose.yaml" "scripts" )

# Tạo thư mục đích nếu chưa tồn tại
mkdir -p "$TARGET_DIR"

# Di chuyển các file và thư mục trừ các thư mục trong danh sách EXCLUSIVE
for item in *; do
  if [[ ! " ${EXCLUSIVE[@]} " =~ " ${item} " ]]; then
    mv "$item" "$TARGET_DIR/"
  fi
done
