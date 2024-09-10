# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    xvfb \
    libxi6 \
    libgconf-2-4 \
    libnss3 \
    libasound2 \
    fonts-liberation \
    libappindicator3-1 \
    xdg-utils \
    libxrandr2 \
    libxss1 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libgbm1 \
    libgtk-3-0 \
    chromium

# Download and install ChromeDriver
RUN wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver

# Set the display port to avoid the "no display" error
ENV DISPLAY=:99

# Set environment variable to disable Streamlit welcome email prompt
ENV STREAMLIT_DISABLE_EMAIL_SIGNUP "true"

# Set working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Run app.py when the container launches
CMD ["streamlit", "run", "streamlit.py"]
