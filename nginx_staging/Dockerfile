# Use the official NGINX image as the base
FROM nginx:1.21-alpine

# Remove the default configuration
RUN rm /etc/nginx/conf.d/default.conf

# Install envsubst for dynamic variable substitution
RUN apk add --no-cache gettext

# Copy the template NGINX configuration file to the container
COPY nginx.conf.template /etc/nginx/templates/nginx.conf.template

# Command to substitute environment variables and start NGINX
CMD ["/bin/sh", "-c", "envsubst '${ENV_WSGI_CONTAINER_NAME} ${ENV_FLOWER_CONTAINER_NAME}' < /etc/nginx/templates/nginx.conf.template > /etc/nginx/conf.d/nginx.conf && nginx -g 'daemon off;'"]
