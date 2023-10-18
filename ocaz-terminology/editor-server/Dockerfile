FROM python:3.11-bullseye
WORKDIR /app
COPY requirements.txt ./
RUN python3 -m pip install --requirement requirements.txt
# COPY src/ ./src/
# ENV LANG C.UTF-8
# ENV TZ Asia/Tokyo
# EXPOSE 8000
# CMD ["uvicorn", "--host=0.0.0.0", "--port=8000", "--app-dir=src", "server:app"]
