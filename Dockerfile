FROM python:3.12-slim

WORKDIR /app


# libgomp1 needed to run xgboost in parallel
# lists/ contains the temp files of apt-get
RUN apt-get update \
    && apt-get install -y libgomp1 \  
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY models/ models/

EXPOSE 8000

CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]