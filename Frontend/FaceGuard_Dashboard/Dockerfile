# Use official Node.js image
FROM node:18

# Set working directory inside container
WORKDIR /app

# Copy package files first for install
COPY package*.json ./

# Install node_modules
RUN npm install

# Copy all your project files into the container
COPY . .

# Expose dev server port (Vite uses 5173 by default unless changed)
EXPOSE 5173

# Run dev server
CMD ["npm", "run", "dev"]


