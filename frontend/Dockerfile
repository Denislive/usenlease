# Use an official Node.js image (preferably version 16 or higher)
FROM node:16

# Set the working directory for the application
WORKDIR /app

# Copy package.json and package-lock.json to the container to leverage Docker's cache for dependencies
COPY package.json package-lock.json ./

# Install the dependencies
RUN npm install

# Copy the rest of the application code into the container
COPY . .

# Expose port 3000 to allow communication with the host machine
EXPOSE 3000

# Run the application in development mode
CMD ["npm", "run", "dev"]
