# Use an official Node.js runtime as a parent image
FROM node:14

# Set the working directory
WORKDIR /app

# Copy package.json and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of your application code
COPY . .

# Build the application (optional, if needed for production)
RUN npm run build  # This step can be optional for development, but useful for production

# Expose the port your app runs on
EXPOSE 3000

# Command to run your app (development mode)
CMD ["npm", "run", "dev"]
