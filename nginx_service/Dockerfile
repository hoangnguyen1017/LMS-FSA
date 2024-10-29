# Dockerfile
FROM nginx:latest

# Copy custom configuration file
COPY nginx.conf /etc/nginx/nginx.conf
COPY SSL /etc/nginx/SSL

# https
EXPOSE 443
# django port
# EXPOSE 8001
# http
EXPOSE 8080