# Stage 1: Build Stage
FROM node:16-alpine AS builder

# Set the work directory for the application
WORKDIR /app

# Copy package.json and package-lock.json to the container to leverage Docker's cache for dependencies
COPY frontend/package.json frontend/package-lock.json ./

# Install the dependencies
RUN npm install

# Copy the rest of the application code into the container
COPY frontend .

# Build the frontend application
RUN npm run build

# Stage 2: Development Image
FROM node:16-alpine

# Set the work directory for the application
WORKDIR /app

# Copy only the necessary files for development
COPY --from=builder /app /app

# Expose port 3000 to allow communication with the host machine
EXPOSE 3000

# Run the application in development mode
CMD ["npm", "run", "dev"]
