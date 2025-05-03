FROM python:3.10-slim

# Instalar dependencias
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    libpq-dev \
    build-essential \
    openssh-server \
    supervisor \
    git \
    rsync \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /run/sshd \
    && ssh-keygen -A

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings.production

WORKDIR /app

# Copiar requirements primero para cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar archivos esenciales
COPY media/templateCarnet /app/template_source
COPY entrypoint.sh supervisord.conf ./

# Configurar usuario y permisos (CORREGIDO)
RUN useradd -m -s /bin/bash railway \
    && mkdir -p /home/railway/.ssh \
    && chown -R railway:railway /home/railway/.ssh \
    && chmod 700 /home/railway/.ssh \
    && chmod +x /app/entrypoint.sh \
    && mv /app/supervisord.conf /etc/supervisor/conf.d/

# Copiar el resto del código
COPY . .

EXPOSE 8080 22

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/conf.d/supervisord.conf"]