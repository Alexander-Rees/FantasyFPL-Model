# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Serve stage
FROM nginx:1.25-alpine
# nginx image already runs as non-root user 'nginx'
# Just ensure correct ownership of the web root
RUN mkdir -p /usr/share/nginx/html
COPY --from=builder /app/build /usr/share/nginx/html
# Copy custom nginx configuration for React Router
COPY nginx.conf /etc/nginx/conf.d/default.conf
# nginx runs as non-root user by default (nginx:nginx)
EXPOSE 80
ENTRYPOINT ["nginx", "-g", "daemon off;"]

