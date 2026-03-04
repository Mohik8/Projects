# Build stage
FROM node:16.13.0-alpine AS builder

WORKDIR /app

COPY package*.json ./

RUN npm install -g @angular/cli@15.0.1

RUN npm install

# Copy the entire project to the container
COPY . .

RUN ng build --configuration=docker

# Use NGINX to serve the Angular application
FROM nginx:1.21.5-alpine

# Copy the built Angular app from the builder stage to the NGINX web root
COPY --from=builder /app/dist/ucrypt-portal /usr/share/nginx/html

EXPOSE 80

# Start NGINX when the container runs
CMD ["nginx", "-g", "daemon off;"]
