# Use a Python base image:
FROM python:3.12.3-slim

# sets the working directory inside the container where the subsequent commands (like COPY, RUN, CMD) will be executed:
WORKDIR /app

# Install all dependencies in the docker image:
# Cache Busting: Isolate requirements and install all dependencies as they dont change often
# Better simply copy everything down and then run because if code change, must reinstall dependencies everytime
COPY ./requirements.txt /app
RUN pip install --no-cache-dir --upgrade -r requirements.txt


# Copy code and everything from the root folder to working directory of container:
COPY . /app/

# Start the server: Run on port 80 (default port)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]
