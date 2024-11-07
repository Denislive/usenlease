# Use an official Node.js image (preferably a version 16 or higher)
FROM node:16

# Set working directory
WORKDIR /app

# Copy package.json and install dependencies
COPY package.json package-lock.json ./
RUN npm install

# Copy the rest of the application code
COPY . .

# Expose the app port
EXPOSE 3000

# Run the application
CMD ["npm", "run", "dev"]
