# Используем минимальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем только requirements сначала (кэширование слоев)
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальной код приложения
COPY app.py .
COPY templates/ ./templates/
COPY static/ ./static/

# Создаем том для базы данных (опционально)
VOLUME ["/app/data"]

# Открываем порт
EXPOSE 5000

# Переменные окружения
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Запускаем приложение
CMD ["python", "app.py"]
