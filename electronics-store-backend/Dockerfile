# Use an official Ubuntu runtime as a parent image
FROM ubuntu:22.04

# Set environment variables for non-interactive installations
ENV DEBIAN_FRONTEND=noninteractive

# Update package lists, install Java OpenJDK 11, Python, and other necessary packages
RUN apt-get update && \
    apt-get install -y openjdk-11-jdk wget tar python3 python3-pip libopenblas-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists

# Set JAVA_HOME and PATH environment variables
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-arm64
ENV PATH=$PATH:$JAVA_HOME/bin

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose port 5555 for the application
EXPOSE 5555

# Run app.py when the container launches
CMD ["python3", "app.py"]
