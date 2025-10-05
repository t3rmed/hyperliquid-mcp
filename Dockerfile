# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DOCKER_BUILDKIT=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependency files and LICENSE (needed for package build)
COPY pyproject.toml uv.lock* LICENSE ./

# Install dependencies
RUN uv sync --frozen --no-cache

# Copy source code
COPY hyperliquid_mcp_server/ ./hyperliquid_mcp_server/

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port (though MCP typically uses stdio)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import hyperliquid_mcp_server; print('OK')" || exit 1

# Default command
CMD ["uv", "run", "python", "-m", "hyperliquid_mcp_server.main"]