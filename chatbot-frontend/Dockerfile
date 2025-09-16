# Use a lightweight Nginx web server image
FROM nginx:1.25-alpine

# Set the working directory for Nginx
WORKDIR /usr/share/nginx/html

# Remove the default Nginx welcome page
RUN rm -rf ./*

# Copy your local 'build' folder's contents into the image
COPY build/ .

# Copy your custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]