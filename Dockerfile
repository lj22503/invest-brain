FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for chromadb
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python requirements
COPY src/mcp_server/requirements.txt .
COPY src/mcp_server/requirements-datasource.txt .
RUN pip install --no-cache-dir -r requirements.txt -r requirements-datasource.txt

# Copy source code
COPY src/ ./src/
COPY data/ ./data/

# Set Python path
ENV PYTHONPATH=/app/src

# Create placeholder env for Glama validation
ENV DEEPSEEK_API_KEY=placeholder
ENV OPENAI_API_KEY=placeholder
ENV ANTHROPIC_API_KEY=placeholder

# Expose HTTP SSE port
EXPOSE 8080

# Run via SSE MCP protocol
ENTRYPOINT ["python", "-m", "mcp_server.server"]
