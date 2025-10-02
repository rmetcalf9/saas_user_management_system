#!/usr/bin/env bash
set -e

# Install dependencies
apt-get update
apt-get install -y curl gnupg2 ca-certificates lsb-release

# Add nginx.org signing key (modern method)
curl -fsSL https://nginx.org/keys/nginx_signing.key | gpg --dearmor -o /usr/share/keyrings/nginx-archive-keyring.gpg

# Add nginx.org APT source for your current Debian version (bookworm)
echo "deb [signed-by=/usr/share/keyrings/nginx-archive-keyring.gpg] https://nginx.org/packages/debian $(lsb_release -cs) nginx" \
    > /etc/apt/sources.list.d/nginx.list

# Install nginx (latest from official repo)
apt-get update
apt-get install -y nginx

# Symlink logs to Docker stdout/stderr
ln -sf /dev/stdout /var/log/nginx/access.log
ln -sf /dev/stderr /var/log/nginx/error.log
