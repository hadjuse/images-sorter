# Multi-stage build optimisé pour le frontend
# Stage 1: Builder - Construction de l'application
FROM node:18-alpine AS builder

# Variables d'environnement pour optimiser la build
ENV NODE_ENV=production \
    NPM_CONFIG_CACHE=/tmp/.npm \
    NPM_CONFIG_UPDATE_NOTIFIER=false

# Installation des dépendances système nécessaires pour la build
RUN apk add --no-cache \
    python3 \
    make \
    g++

# Définir le répertoire de travail
WORKDIR /build

# Copier les fichiers de dépendances en premier pour optimiser le cache
COPY package*.json ./

# Installer les dépendances (avec cache optimisé)
# NOTE: Must include devDependencies for build tools like typescript and vite
RUN npm install --include=dev --silent

# DEBUG: List what was installed
RUN ls -la node_modules/.bin/ | head -20 || echo "No .bin folder"

# Copier le code source
COPY . .

# Construire l'application
RUN npm run build

# Nettoyer les node_modules après la build pour réduire la taille
RUN rm -rf node_modules

# Stage 2: Runtime - Serveur Nginx léger
FROM nginx:1.29-alpine AS runtime

# Variables d'environnement de production
ENV NGINX_ENVSUBST_TEMPLATE_SUFFIX=.template \
    NGINX_ENVSUBST_OUTPUT_DIR=/etc/nginx/conf.d

# Installation des outils nécessaires
RUN apk add --no-cache \
    curl \
    ca-certificates \
    && rm -rf /var/cache/apk/*

# Copier les assets construits depuis le builder
COPY --from=builder /build/dist /usr/share/nginx/html

# Copier la configuration Nginx optimisée
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Créer un utilisateur non-root
RUN addgroup -g 1000 -S nginx-user && \
    adduser -u 1000 -D -S -G nginx-user nginx-user

# Ajuster les permissions
RUN chown -R nginx-user:nginx-user /usr/share/nginx/html && \
    chown -R nginx-user:nginx-user /var/cache/nginx && \
    chown -R nginx-user:nginx-user /var/log/nginx && \
    chown -R nginx-user:nginx-user /etc/nginx/conf.d && \
    touch /var/run/nginx.pid && \
    chown -R nginx-user:nginx-user /var/run/nginx.pid

# Basculer vers l'utilisateur non-root
USER nginx-user

# Exposer le port
EXPOSE 8080

# Health check optimisé
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

# Démarrer Nginx
CMD ["nginx", "-g", "daemon off;"]