FROM node:18-slim

WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build TypeScript code
RUN npm run build

# Set executable permissions for the entry point
RUN chmod +x dist/index.js

# Start the MCP server
CMD ["node", "dist/index.js"]
