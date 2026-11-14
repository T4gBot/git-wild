FROM python:3.11-slim

#Working directory inside the container
WORKDIR /app


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#Copy the code directory into container dir
COPY . .

# port of Flask
EXPOSE 5000
CMD ["python", "app.py"]