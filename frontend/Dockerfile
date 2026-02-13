FROM node:20-slim

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the frontend code
COPY . .

# Set the API base URL for the frontend to find the backend container
ENV REACT_APP_API_BASE=http://localhost:8000
# Ensure React runs on the requested port 3001
ENV PORT=3001

EXPOSE 3001

CMD ["npm", "run", "dev"]