# Build stage
FROM node:22-alpine AS builder

WORKDIR /app

COPY package.json .npmrc ./
RUN npm install

ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL

COPY . .
RUN npm run build

# Production stage
FROM node:22-alpine

WORKDIR /app

# Install serve to run the built Vite app
RUN npm install -g serve

# Copy built app from builder
COPY --from=builder /app/build ./build

EXPOSE 3000

CMD ["serve", "-s", "build", "-l", "3000"]
