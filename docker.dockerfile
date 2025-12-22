# Use the official Crawl4AI image which has everything ready
FROM unclecode/crawl4ai:all

# Set working directory
WORKDIR /app

# Copy your local code to the container
COPY . /app

# Install your specific app requirements (like langchain)
RUN pip install -r requirements.txt

# Start your application (e.g., a FastAPI or Flask app)
CMD ["python", "main.py"]