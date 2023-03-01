FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m textblob.download_corpora
COPY . .
CMD python main.py stable