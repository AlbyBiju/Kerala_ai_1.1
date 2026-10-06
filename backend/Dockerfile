FROM python:3.12-slim

WORKDIR /app

# System dependencies: OCR engine, PDF rasterizer, and WeasyPrint native libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    poppler-utils \
    libcairo2 \
    libpango-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
