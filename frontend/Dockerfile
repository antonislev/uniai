# frontend/Dockerfile

### Stage 1: build with Node ###
FROM node:22-alpine AS build

WORKDIR /app
# Copy package files and install deps
COPY package*.json ./
RUN npm install
# Copy the rest of your source
COPY . .
# Build the production assets
RUN npm run build

### Stage 2: serve with Nginx ###
FROM nginx:alpine

# Copy built assets from the builder
COPY --from=build /app/dist /usr/share/nginx/html
# Copy your custom Nginx config (if you have one)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Let Nginx run in the foreground
CMD ["nginx", "-g", "daemon off;"]

