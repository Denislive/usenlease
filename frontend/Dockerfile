# Stage 1: Build Stage
FROM node:16-alpine AS builder

# Set the working directory for the application
WORKDIR /app

# Copy package.json and package-lock.json to leverage Docker's cache for dependencies
COPY package.json package-lock.json ./

# Install the dependencies
RUN npm install

# Copy the rest of the application code into the container
COPY . .

# Build the frontend application
RUN npm run build

# Stage 2: Production Image
FROM node:16-alpine

# Set the working directory for the application
WORKDIR /app

# Copy only the necessary files from the build stage to the production image
COPY --from=builder /app /app

# Install a simple HTTP server to serve your static files
RUN npm install -g serve

# Expose the port Heroku will use
EXPOSE $PORT

# Run the application in production mode using the "serve" package
CMD ["npm", "start"]
