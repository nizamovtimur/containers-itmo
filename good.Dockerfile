# containers-itmo/good.Dockerfile

# Использование легковесного базового образа Python с фиксированной версией
FROM python:3.10.0-slim-buster

# Создание системной группы и пользователя для запуска приложения
RUN addgroup --system app && adduser --system --group app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Установка необходимых системных зависимостей с минимальными рекомендациями и очисткой кеша
RUN apt-get update && apt-get install -y --no-install-recommends gcc curl && \
    pip install --upgrade pip && \
    apt-get purge -y --auto-remove gcc && \
    rm -rf /var/lib/apt/lists/*

# Установка зависимостей Python без кеширования pip
COPY qa/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Установка рабочей директории
WORKDIR /app

# Копирование кода приложения
COPY qa /app

# Создание директории для логов и установка прав доступа
RUN mkdir -p /app/logs && chown -R app:app /app/logs

# Переключение на созданного пользователя
USER app

# Определение volume для логов
VOLUME ["/app/logs"]

# Добавление healthcheck для мониторинга состояния приложения
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Открытие порта для приложения
EXPOSE 8080

# Запуск приложения
CMD ["python", "main.py"]