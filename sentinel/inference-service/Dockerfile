FROM node:18
WORKDIR /app
COPY package*.json ./
RUN npm install --production
COPY . .
# Ensure the model is copied into the image
COPY cheat_model.onnx . 
EXPOSE 3001
CMD ["node", "server.js"]