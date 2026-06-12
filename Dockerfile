# Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy your requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the port Hugging Face expects (7860)
EXPOSE 7860

# Run Streamlit
CMD ["streamlit", "run", "main.py", "--server.port=7860", "--server.address=0.0.0.0"]git