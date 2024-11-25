# containers-itmo/bad.Dockerfile

# Использование полного базового образа Python без оптимизации размера
FROM python:3.10.0

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Установка ненужных пакетов, которые не требуются для выполнения приложения
RUN apt-get update && apt-get install -y git build-essential

# Обновление pip до последней версии и установка зависимостей без использования флага --no-cache-dir
RUN pip install --upgrade pip
COPY qa/requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# Копирование всего кода приложения в контейнер
COPY qa /app

# Создание директории для логов
RUN mkdir -p /app/logs

# Определение volume для логов
VOLUME ["/app/logs"]

# Открытие порта для приложения
EXPOSE 8080

# Запуск приложения от имени root, что повышает риски безопасности
CMD ["python", "/app/main.py"]