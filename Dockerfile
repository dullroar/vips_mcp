FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends libvips-tools \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
# server.py uses FastMCP from the MCP 1.x SDK.
RUN python -m pip install --no-cache-dir -r requirements.txt 'mcp<2' \
    && useradd --create-home --user-group vips

COPY . .
USER vips

CMD ["python", "/app/server.py"]
