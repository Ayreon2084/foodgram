## **1. - Локальный деплой.**
---

### **1.1. - Клонировать репозиторий:**

```sh {"id":"01J9RAX7GYEX2ZYG1G85TZW47K"}
git clone git@github.com:Ayreon2084/foodgram.git
```

### **1.2. - Создать в корневой директории проекта файл .env с переменными окружения:**

```sh {"id":"01J9RCXF8A2G1VTX77FP90T3D2"}
POSTGRES_USER=  # имя пользователя в БД PostgreSQL
POSTGRES_PASSWORD=  # пароль пользователя в БД PostgreSQL
POSTGRES_DB=  # название БД PostgreSQL
DB_HOST=  # имя контейнера, где забущена БД PostgreSQL
DB_PORT=  # порт, по которому Django будет обращаться к БД PostgreSQL
SECRET_KEY=  # секретный код из settings.py для Django проекта
DEBUG=  # статус режима отладки (default=False)
ALLOWED_HOSTS=  # список доступных хостов
DOMAIN=  # список доступных доменов
```

### **1.3. - Выполнить в корневой директории проекта команду:**

```sh {"id":"01J9RDA26E4GS2Q258PEAS9EFW"}
docker compose -f docker-compose.yml up --build
```

## **2. - Деплой на сервер.**
---

### **2.1. - Краткая инструкция:**

- Выполнить шаги 1.1 и 1.2 из 1. Локальный деплой.
- Собрать образы и залить на Docker Hub.
- Написать такой конфигурационный файл для Docker Compose, чтобы он брал образы с Docker Hub.
- Развернуть и запустить Docker на сервере.
- Загрузить на сервер новый конфиг для Docker Compose и запустить контейнеры.
- Настроить «внешний» Nginx — тот, что вне контейнера — для работы с приложением в контейнерах.

### **2.2. - Пуш образов на Docker Hub:**

```sh {"id":"01J9RDK7Z6PQCSEYTM0RTR0D83"}
sudo docker push <docker_hub_username>/<image_name>
```

### **2.3. - Установка Docker Compose на сервер:**

```sh {"id":"01J9RDN28EEBKKTD1CK7CCSYQJ"}
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt install docker-compose-plugin 
```

### **2.4. - Клонировать файлы на сервер:**

- Создать на сервере директорию проекта.
- Склонировать в директорию проекта на сервере файлы .env и docker-compose.production.yml:

```sh {"id":"01J9RDR1C0RJS2V3ACGFTS8RZ0"}
scp -i <path_to_SSH>/<SSH_name> <local_file> \
    <username>@<server_ip>:/home/username/<remore_directory>/<remote_file> 
```

где:
- path_to_SSH — путь к файлу с SSH-ключом;
- SSH_name — имя файла с SSH-ключом (без расширения);
- local_name - имя файла для копирования;
- username — ваше имя пользователя на сервере;
- server_ip — IP вашего сервера;
- remote_directory - директория на сервере;
- remote_file - файл на сервере.

### **2.5. - Запуск Docker Compose в режиме демона:**

```sh {"id":"01J9RE0VAD33S1BS7CWDCCTABF"}
cd <remote_directory>
sudo docker compose -f docker-compose.production.yml up -d
```

Проект запущен!