FROM python:3.11-slim

# -- Environment variables 
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# -- Working directory 
WORKDIR /app

# -- Install dependencies 
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# -- Copy project 
COPY . .

# -- Expose port 
EXPOSE 8000

# -- Run migrations and start server 
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]