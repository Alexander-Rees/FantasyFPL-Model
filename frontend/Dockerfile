# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Serve stage
FROM nginx:1.25-alpine
RUN adduser -D -H -u 101 app && mkdir -p /usr/share/nginx/html && chown -R app /usr/share/nginx/html
COPY --from=builder /app/build /usr/share/nginx/html
EXPOSE 80
USER app
ENTRYPOINT ["nginx", "-g", "daemon off;"]

