FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

# Install system packages
RUN sed -i 's|http://archive.ubuntu.com/ubuntu/|http://mirrors.aliyun.com/ubuntu/|g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --fix-missing --no-install-recommends \
    python3 python3-pip python3-venv \
    libgl1 libglib2.0-0 git && \
    rm -rf /var/lib/apt/lists/*

#
WORKDIR /code

#
COPY ./requirements.txt /code/requirements.txt

#
COPY ./app /code/app

RUN pip3 install --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

#
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]