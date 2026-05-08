FROM nginx:alpine

# Copiar archivos del frontend
COPY index.html /usr/share/nginx/html/
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

# Healthcheck para Docker
HEALTHCHECK CMD wget --no-verbose --tries=1 --spider http://localhost || exit 1