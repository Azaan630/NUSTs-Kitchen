FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --default-timeout=100 --no-cache-dir -r requirements.txt -i https://pypi.org/simple/
COPY . .
CMD ["python", "main.py"]
ENV PIP_ROOT_USER_ACTION=ignored