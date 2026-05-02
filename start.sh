#!/bin/bash
echo "Starting EduQuery services..."
sudo service mysql start
docker rm -f qdrant 2>/dev/null
docker run -d --name qdrant -p 6333:6333 -p 6334:6334 \
  -v ~/eduquery/qdrant_storage:/qdrant/storage \
  qdrant/qdrant
sleep 5
sudo fuser -k 8000/tcp 2>/dev/null
source venv/bin/activate
PYTHONPATH=. uvicorn src.api.main:app --reload --port 8000