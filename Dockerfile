# One image for the portal mock, the ServiceNow mock, the ingest job and the agent; compose picks the command.
FROM python:3.12-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 AGNO_TELEMETRY=false \
    DESK_RUNTIME_DIR=/runtime FASTEMBED_CACHE_PATH=/models HF_HUB_DISABLE_PROGRESS_BARS=1

COPY requirements.txt .
RUN pip install -r requirements.txt

# Bake the embedding model into the image: after the first build, the stack runs with no internet access.
RUN python -c "from fastembed import TextEmbedding; TextEmbedding('BAAI/bge-small-en-v1.5', cache_dir='/models')"
ENV HF_HUB_OFFLINE=1

COPY desk ./desk
COPY data ./data

EXPOSE 8180 8181 8182
CMD ["uvicorn", "desk.app:app", "--host", "0.0.0.0", "--port", "8180"]
