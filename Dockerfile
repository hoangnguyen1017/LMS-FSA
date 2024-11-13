# Use an official Python runtime as a parent image
FROM pytorch/pytorch:2.2.2-cuda12.1-cudnn8-runtime

WORKDIR /app
# COPY . /app
COPY requirements.txt /app

RUN apt-get update && apt-get install -y libgl1-mesa-dev libglib2.0-dev
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# ENV NAME World

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--reload", "--port", "8000"]