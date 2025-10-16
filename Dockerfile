# Використовуємо один базовий образ
FROM python:3.11-slim-bookworm

# Встановлюємо системні залежності, необхідні для роботи
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    gallery-dl \
    && rm -rf /var/lib/apt/lists/*

# Встановлюємо робочу директорію
WORKDIR /app

# Копіюємо файл з описом залежностей
COPY pyproject.toml .

# Встановлюємо Python-залежності за допомогою pip
# Це найнадійніший спосіб для Docker
RUN pip install --no-cache-dir .

# Копіюємо решту файлів проєкту
COPY . .

# Вказуємо команду для запуску бота
CMD ["python", "bot.py"]