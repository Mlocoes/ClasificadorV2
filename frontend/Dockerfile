FROM node:18-alpine

# Instalar curl para el healthcheck
RUN apk add --no-cache curl

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 3000

# Cambiar a modo desarrollo en lugar de preview
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]
