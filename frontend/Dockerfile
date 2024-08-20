# 1) Set the Base image: Version of node used:
FROM node:20.11.1

# 2) Set the working directory of the container to /app:
WORKDIR /app

# 3) Copy package.json and package-lock.json (if available) to the working directory:
COPY ./frontend/package*.json ./

# 4) Install all dependencies listed in package.json:
RUN npm install

# 5) Copy the rest of your application code to the working directory:
COPY ./frontend ./

# 6) Instruct Docker that the Frontend container will listen on port 3000:
EXPOSE 3000

# 7) Specifies that when the container is started it should run the command "npm start":
CMD ["npm", "start"]

