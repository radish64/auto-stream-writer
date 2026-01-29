# Use an existing base image
FROM ubuntu:latest

ENV TZ=America/Detroit

# Set the working directory in the container
WORKDIR /app

# Copy application files from host to container
COPY . .

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip ;

RUN pip3 install -r requirements.txt --break-system-packages;

# Set the default command to execute when the container starts
CMD ["waitress-serve", "--listen=0.0.0.0:5000", "server:app"]

EXPOSE 5000
