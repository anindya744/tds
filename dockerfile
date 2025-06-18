FROM python:3.12-slim
ENV LAMBDA_TASK_ROOT="/var/task"
WORKDIR ${LAMBDA_TASK_ROOT}
# Install system dependencies using apt (Amazon Linux uses apt, not apt)
RUN apt-get update \
    && apt-get install -y \
        gcc \
        libpq-dev \
        python3-dev \
        build-essential \
    && apt-get clean

# Copy app code and requirements2
COPY requirements2.txt ${LAMBDA_TASK_ROOT}/
COPY . ${LAMBDA_TASK_ROOT}/

# Install Python dependencies into Lambda directory
RUN pip install --upgrade pip
RUN pip install -r requirements2.txt

# Set the handler
# CMD [ "main.handler" ]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]