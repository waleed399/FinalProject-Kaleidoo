# Use an official Node runtime as a parent image
FROM node:14

# Set the working directory in the container
WORKDIR /app

# Copy the package.json and package-lock.json files
COPY package*.json ./

# Install the dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the React app
RUN npm run build

# Install a lightweight HTTP server
RUN npm install -g serve

# Expose port 3000 for the React app
EXPOSE 3000

# Serve the build folder
CMD ["serve", "-s", "build"]