# VPS Setup - Step by Step Deploy Guide

**Пошаговая инструкция развертывания Docker контейнеров на VPS**

---

## 📋 ПРЕДВАРИТЕЛЬНЫЕ ТРЕБОВАНИЯ

### VPS Рекомендации

```
ОЙ МИНИМУМ:
  CPU: 1 core
  RAM: 2 GB
  Disk: 20 GB
  OS: Ubuntu 20.04 LTS или выше
  Cost: $5-10/month

РЕКОМЕНДУЕМО:
  CPU: 2 cores
  RAM: 4 GB
  Disk: 50 GB
  OS: Ubuntu 22.04 LTS
  Cost: $15-25/month
```

### Популярные VPS провайдеры

- **DigitalOcean** - $5/month, easy setup
- **Linode** - $5/month, reliable
- **Hetzner** - €3/month, cheap
- **Vultr** - $2.50/month, global
- **AWS Lightsail** - $3.50/month

---

## 🚀 ЭТАП 1: SSH Доступ к VPS

### Шаг 1.1: Получить IP VPS

После создания VPS, провайдер дает:
```
IP Address:    123.45.67.89
Username:      root (или ubuntu)
Password:      your_password (или используй SSH ключ)
Port:          22 (обычно)
```

### Шаг 1.2: SSH подключение

**На Mac/Linux:**
```bash
ssh root@123.45.67.89
# или
ssh -i ~/.ssh/id_rsa root@123.45.67.89
```

**На Windows (PowerShell):**
```powershell
ssh root@123.45.67.89
```

**На Windows (Putty):**
- Скачай Putty
- Host: 123.45.67.89
- Port: 22
- Click "Open"

### Шаг 1.3: Проверить подключение

```bash
# Должен увидеть приглашение:
root@vps:~#

# Проверить OS
cat /etc/os-release
# Должен быть Ubuntu 20.04+

# Проверить интернет
ping 8.8.8.8
# Должны быть ответы
```

---

## 🔧 ЭТАП 2: Установка Docker & Docker Compose

### Шаг 2.1: Обновить систему

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

**Если спросит про конфиги:**
```
Keep the local version
```

### Шаг 2.2: Установить Docker

```bash
# Удалить старые версии (если есть)
sudo apt-get remove docker docker-engine docker.io containerd runc -y 2>/dev/null || true

# Установить зависимости
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Добавить Docker GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Добавить Docker репозиторий
echo \
  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Обновить и установить Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io
```

### Шаг 2.3: Проверить Docker

```bash
sudo docker --version
# Docker version 20.10+

sudo docker run hello-world
# Должен вывести "Hello from Docker!"
```

### Шаг 2.4: Установить Docker Compose

```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

sudo chmod +x /usr/local/bin/docker-compose

sudo docker-compose --version
# Docker Compose version 2.x+
```

### Шаг 2.5: Добавить пользователя в группу Docker (опционально)

```bash
# Чтобы не писать sudo каждый раз
sudo usermod -aG docker $USER

# Активировать новую группу
newgrp docker

# Проверить
docker ps
# Должно работать без sudo
```

---

## 📁 ЭТАП 3: Клонирование репо

### Шаг 3.1: Выбрать папку

```bash
# Рекомендуется /opt
cd /opt

# Или можно домашнюю папку
cd ~

# Или создать свою
mkdir -p /home/web-crawler && cd /home/web-crawler
```

### Шаг 3.2: Клонировать репо

```bash
# HTTPS версия (не нужен SSH ключ)
git clone https://github.com/KomarovAI/web-crawler.git

# SSH версия (если настроен SSH ключ)
# git clone git@github.com:KomarovAI/web-crawler.git

cd web-crawler
```

### Шаг 3.3: Проверить файлы

```bash
ls -la

# Должны быть:
# crawler.py
# crawler_full.py
# docker-compose.yml
# Dockerfile
# nginx.conf
# .env.example
# requirements.txt
```

---

## ⚙️ ЭТАП 4: Конфигурация

### Шаг 4.1: Создать .env файл

```bash
cp .env.example .env
```

### Шаг 4.2: Отредактировать .env

```bash
nano .env

# Или
vim .env

# Или
cat > .env << EOF
START_URL=https://example.com
MAX_PAGES=50
TIMEOUT=10
USE_DB=true
DB_FILE=crawled.db
OUTPUT_DIR=site_archive
EOF
```

### Шаг 4.3: Проверить .env

```bash
cat .env

# Должны быть установлены:
# START_URL=...
# MAX_PAGES=...
# TIMEOUT=...
```

### Шаг 4.4: Создать директории

```bash
mkdir -p site_archive output
chmod 755 site_archive output
```

---

## 🐳 ЭТАП 5: Первый запуск Docker

### Шаг 5.1: Проверить файлы

```bash
ls -la docker-compose.yml Dockerfile .env
# Все должны быть на месте
```

### Шаг 5.2: Создать образ

```bash
# Проверить что docker может запуститься
sudo docker --version
sudo docker ps

# Построить образ (первый раз, медленнее)
sudo docker-compose build

# Expected:
# Building crawler
# Step 1/20: FROM python:3.11-slim as builder
# ...
# Successfully built abc123def456
```

### Шаг 5.3: Проверить образ

```bash
sudo docker images | grep crawler
# Должен быть образ размером ~150MB
```

---

## 🚀 ЭТАП 6: Запуск сервисов

### Способ A: Только базовый краулер (РЕКОМЕНДУЕТСЯ для первого раза)

```bash
# Запустить в фоне
sudo docker-compose up -d crawler

# Проверить статус
sudo docker-compose ps

# Expected:
# web-crawler-basic    Up (healthy)

# Смотреть логи
sudo docker-compose logs -f crawler

# Expected output:
# [1/50]https://example.com
# [2/50]https://example.com/about
# ...
# ✅ 25 pages
# 💾 25 pages in DB

# Остановить когда готово
sudo docker-compose stop
```

### Способ B: С полным архивером

```bash
# Запустить
sudo docker-compose --profile archiver up -d crawler-full

# Смотреть логи
sudo docker-compose logs -f crawler-full

# Остановить
sudo docker-compose down
```

### Способ C: Со всеми сервисами

```bash
# Запустить (crawler + archiver + nginx)
sudo docker-compose --profile archiver --profile web up -d

# Проверить все сервисы
sudo docker-compose ps

# Expected:
# web-crawler-basic    Up (healthy)
# web-crawler-full     Up (healthy)
# web-crawler-nginx    Up (healthy)

# Смотреть логи всех
sudo docker-compose logs -f

# Или конкретного
sudo docker-compose logs -f nginx
```

---

## 📊 ЭТАП 7: Мониторинг

### Шаг 7.1: Проверить статус

```bash
# Все контейнеры
sudo docker ps

# Детальный статус
sudo docker-compose ps

# Ресурсы (CPU, Memory)
sudo docker stats
```

### Шаг 7.2: Смотреть логи

```bash
# Real-time
sudo docker-compose logs -f

# Последние 100 строк
sudo docker-compose logs --tail 100

# Конкретного сервиса
sudo docker-compose logs -f crawler

# С временем
sudo docker-compose logs --timestamps -f
```

### Шаг 7.3: Проверить здоровье

```bash
# Если nginx работает
curl http://localhost/health
# Result: OK

# Или
curl http://your-vps-ip/health
```

---

## 💾 ЭТАП 8: Доступ к результатам

### Способ 1: Копировать файлы локально

```bash
# Скопировать БД
sudo docker cp web-crawler-basic:/app/crawled.db ./

# Скопировать архив
sudo docker cp web-crawler-full:/app/site_archive ./

# Скопировать на локальную машину
scp -r root@123.45.67.89:/opt/web-crawler/crawled.db ./
scp -r root@123.45.67.89:/opt/web-crawler/site_archive ./
```

### Способ 2: Nginx Web UI

```
http://your-vps-ip/archive/

# Если nginx работает, сайт доступен онлайн!
```

### Способ 3: SSH в контейнер

```bash
# Войти в контейнер
sudo docker-compose exec crawler bash

# Внутри контейнера
ls -la
sqlite3 crawled.db "SELECT COUNT(*) FROM pages;"

# Выход
exit
```

---

## 🛑 ЭТАП 9: Остановка и перезагрузка

### Остановить сервисы

```bash
# Мягкая остановка
sudo docker-compose stop

# Полная остановка (удалить контейнеры)
sudo docker-compose down

# Удалить всё включая volumes (ОСТОРОЖНО!)
sudo docker-compose down -v
```

### Перезагрузить сервисы

```bash
# Перезагрузить один сервис
sudo docker-compose restart crawler

# Пересоздать (с новым образом)
sudo docker-compose up -d --force-recreate crawler

# Перестроить образ и запустить
sudo docker-compose up -d --build
```

---

## 🔄 ЭТАП 10: Автозагрузка (опционально)

### Сделать сервисы автоматическим стартом

```bash
# Отредактировать docker-compose.yml
sudo nano docker-compose.yml

# Добавить для каждого сервиса:
restart: always

# Или через команду:
sudo docker-compose up -d --restart-policy always
```

### Создать systemd сервис (для автозагрузки)

```bash
sudo nano /etc/systemd/system/docker-crawler.service

# Вставить:
[Unit]
Description=Docker Web Crawler
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
ExecStart=/usr/bin/docker-compose -f /opt/web-crawler/docker-compose.yml up -d
RemainAfterExit=yes
ExecStop=/usr/bin/docker-compose -f /opt/web-crawler/docker-compose.yml down

[Install]
WantedBy=multi-user.target

# Сохранить (Ctrl+X, Y, Enter)

# Включить автозагрузку
sudo systemctl enable docker-crawler.service

# Проверить
sudo systemctl status docker-crawler.service
```

---

## ✅ ЧЕКЛИСТ РАЗВЕРТЫВАНИЯ

```
☐ VPS создан и доступен по SSH
☐ Docker установлен (docker --version)
☐ Docker Compose установлен (docker-compose --version)
☐ Репо склонирован (git clone ...)
☐ .env файл создан и отредактирован
☐ Образ собран (docker-compose build)
☐ Сервис запущен (docker-compose up -d)
☐ Логи проверены (docker-compose logs)
☐ Контейнер здоров (docker ps shows healthy)
☐ Результаты доступны (БД, архив или web)
☐ Перезагрузка протестирована
☐ Автозагрузка настроена (опционально)
```

---

## 🆘 TROUBLESHOOTING

### Docker не запускается

```bash
# Проверить статус
sudo systemctl status docker

# Перезагрузить Docker
sudo systemctl restart docker

# Проверить логи
sudo journalctl -u docker -n 100
```

### Контейнер не запускается

```bash
# Посмотреть ошибку
sudo docker-compose logs

# Пересоздать
sudo docker-compose down
sudo docker-compose up -d --build
```

### Out of disk space

```bash
# Проверить место
df -h

# Очистить Docker
sudo docker system prune -a

# Или удалить старые образы
sudo docker image prune -a
```

### SSH не подключается

```bash
# Проверить IP VPS
ping your-vps-ip

# Проверить SSH порт
ssh -vvv root@your-vps-ip

# Если firewall блокирует
sudo ufw allow 22
```

---

## 📞 ИТОГОВЫЕ КОМАНДЫ (Скопируй и пусти)

```bash
#!/bin/bash
# install_docker.sh

echo "🚀 Installing Docker..."

sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

echo "✅ Docker installed!"
docker --version
docker-compose --version
```

---

## 🎯 БЫСТРЫЙ СТАРТ (для нетерпеливых)

```bash
# 1. SSH
ssh root@your-vps-ip

# 2. Установить Docker (скопируй команды выше)
# или один скрипт
curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh

# 3. Установить Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 4. Клонировать
cd /opt && sudo git clone https://github.com/KomarovAI/web-crawler.git
cd web-crawler && sudo cp .env.example .env

# 5. Запустить
sudo docker-compose up -d crawler

# 6. Проверить
sudo docker-compose logs -f

# 7. Готово! 🎉
```

---

**Status:** Ready to deploy! 🚀  
**Time needed:** 10-15 minutes for first setup  
**Difficulty:** Easy (just copy-paste commands)
