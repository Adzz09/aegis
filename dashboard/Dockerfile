FROM node:18-alpine

WORKDIR /app

COPY dashboard/package*.json ./
RUN npm install

COPY dashboard/ .

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
