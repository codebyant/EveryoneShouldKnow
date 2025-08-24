# Use the Python base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the necessary files to the bot container
COPY bot.py /app
COPY requirements.txt /app
COPY locales /app/locales

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Default command to run the bot when the container starts
CMD ["python", "bot.py"]