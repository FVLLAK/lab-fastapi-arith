# Use a lightweight Python base image
FROM python:3.11-slim

# Prevent Python from writing .pyc files and force unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set work directory inside the container
WORKDIR /app

# Copy dependency files
COPY requirements.txt .

# Optional: copy pre-downloaded wheels if you build offline (as your Jenkins logs show)
COPY wheels/ /wheels/

# Install dependencies using wheels (offline mode)
RUN pip install --no-index --find-links=/wheels -r requirements.txt

# Copy the rest of the project
COPY . .

# Expose Flask port
EXPOSE 5000

# Default command to run the app
CMD ["python", "app.py"]
