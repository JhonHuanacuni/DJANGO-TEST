#!/bin/sh

# Sección SSH
if [ -n "$RAILWAY_SSH_PUBKEY" ]; then
    echo "🔑 Añadiendo clave SSH..."
    mkdir -p /home/railway/.ssh
    echo "$RAILWAY_SSH_PUBKEY" >> /home/railway/.ssh/authorized_keys
    chmod 600 /home/railway/.ssh/authorized_keys
else
    echo "⚠️ Advertencia: No se encontró RAILWAY_SSH_PUBKEY"
fi

# Sección templates
REPO_SOURCE="/app/template_source"
VOLUME_TARGET="/app/media/templateCarnet"

if [ -d "$REPO_SOURCE" ]; then
    echo "🔄 Sincronizando plantillas..."
    mkdir -p "$VOLUME_TARGET"
    rsync -ar --delete --exclude='.gitkeep' "$REPO_SOURCE/" "$VOLUME_TARGET/"
else
    echo "⚠️ Advertencia: Directorio source no encontrado: $REPO_SOURCE"
fi

# Iniciar Supervisor
echo "🚀 Iniciando servicios..."
exec "$@"