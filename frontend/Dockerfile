# 1) Set the Base image: Version of node used:
FROM node:20.11.1

# 2) Set the working directory of the container to /app:
WORKDIR /app

# 3) Copies all dependencies in the requirement txt file to /app directory in the container:
COPY ./frontend-requirement.txt /app
# 4) Install all dependencies in the frontend-requirement.txt in the working directory of the container:
# 4) Saves all dependencies to package.json:
RUN npm install --save $(cat frontend-requirement.txt)

# 5) Copy all files code and folder in frontend directory to the container so that the code can be executed in container:
COPY . /app/

# 6) Instruct Docker that the Frontend container will listen on port 3000:
EXPOSE 3000

# 7) Specifies that when container is started it should run the command "npm start":
CMD ["npm", "start"]

