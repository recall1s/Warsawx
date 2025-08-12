import os
import json
import random
import string
import hashlib
import webbrowser
import requests
import time
from datetime import datetime, timedelta
from getpass import getpass
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import sys
import threading
import subprocess
import platform
from uuid import uuid4
import glob
import select

# Конфигурация
APP_NAME = "warsawx"
BASE_DIR = os.path.join(os.getenv('APPDATA', os.path.expanduser('~/.config')), APP_NAME)
CONFIG = {
    "app_title": "WarsawX",
    "icon_url": "https://images.boosty.to/user/41038539/avatar?change_time=1754911465&croped=1&mh=320&mw=320",
    "admin_username": "Recall's",
    "min_username_len": 3,
    "max_username_len": 17,
    "support_chat": "warsawx_support",
    "favorites_chat": "warsawx_favorites"
}

# Пути к файлам
PATHS = {
    "users": os.path.join(BASE_DIR, "Users"),
    "nicknames": os.path.join(BASE_DIR, "nicknames.txt"),
    "language": os.path.join(BASE_DIR, "language.txt"),
    "lockouts": os.path.join(BASE_DIR, "lockouts.json"),
    "support": os.path.join(BASE_DIR, "support_chats"),
    "updates": os.path.join(BASE_DIR, "updates"),
    "master_key": os.path.join(BASE_DIR, "master.key"),
    "integrity": os.path.join(BASE_DIR, "integrity.sig"),
    "app_exe": os.path.join(BASE_DIR, "warsawx")
}

def setup_directories():
    """Создает все необходимые директории и файлы при первом запуске"""
    try:
        # Создаем основную директорию
        os.makedirs(BASE_DIR, exist_ok=True)
        
        # Создаем поддиректории
        os.makedirs(PATHS["users"], exist_ok=True)
        os.makedirs(PATHS["support"], exist_ok=True)
        os.makedirs(PATHS["updates"], exist_ok=True)
        
        # Создаем необходимые файлы
        required_files = {
            PATHS["nicknames"]: "",
            PATHS["language"]: "en",
            PATHS["lockouts"]: {},
            PATHS["integrity"]: hashlib.sha256(open(__file__, 'rb').read()).hexdigest(),
        }
        
        for file_path, default_content in required_files.items():
            if not os.path.exists(file_path):
                if isinstance(default_content, (dict, list)):
                    with open(file_path, 'w') as f:
                        json.dump(default_content, f)
                else:
                    with open(file_path, 'w') as f:
                        f.write(str(default_content))
        
        # Создаем мастер-ключ
        if not os.path.exists(PATHS["master_key"]):
            with open(PATHS["master_key"], 'wb') as f:
                f.write(get_random_bytes(32))
        
        return True
    except Exception as e:
        print(f"Ошибка при создании файловой структуры: {e}")
        return False

# Шифрование данных
class CryptoManager:
    @staticmethod
    def get_key():
        with open(PATHS["master_key"], 'rb') as f:
            return f.read()

    @staticmethod
    def encrypt(data, key=None):
        key = key or CryptoManager.get_key()
        iv = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        ct = cipher.encrypt(pad(data.encode(), AES.block_size))
        return base64.b64encode(iv + ct).decode()

    @staticmethod
    def decrypt(enc_data, key=None):
        key = key or CryptoManager.get_key()
        enc_data = base64.b64decode(enc_data)
        iv = enc_data[:16]
        ct = enc_data[16:]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        return pt.decode()

# Управление пользователями
class UserManager:
    @staticmethod
    def validate_username(username):
        if len(username) < CONFIG["min_username_len"] or len(username) > CONFIG["max_username_len"]:
            return False
        allowed = string.ascii_letters + string.digits + "'-_"
        return all(c in allowed for c in username)

    @staticmethod
    def is_username_taken(username):
        if not os.path.exists(PATHS["nicknames"]) or os.path.getsize(PATHS["nicknames"]) == 0:
            return False
        with open(PATHS["nicknames"], 'r') as f:
            return username in f.read().split()

    @staticmethod
    def create_user(username, password):
        user_file = os.path.join(PATHS["users"], f"{username}.json")
        salt = os.urandom(16)
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        
        user_data = {
            "password": hashlib.sha256(password.encode()).hexdigest(),
            "salt": base64.b64encode(salt).decode(),
            "created": datetime.now().isoformat(),
            "friends": [],
            "blocked": [],
            "chats": {
                CONFIG["support_chat"]: {"created": datetime.now().isoformat()},
                CONFIG["favorites_chat"]: {"created": datetime.now().isoformat()}
            }
        }

        with open(user_file, 'w') as f:
            json.dump(user_data, f)
        
        with open(PATHS["nicknames"], 'a') as f:
            f.write(username + "\n")
        
        return True

    @staticmethod
    def get_user(username):
        user_file = os.path.join(PATHS["users"], f"{username}.json")
        if not os.path.exists(user_file):
            return None
        with open(user_file, 'r') as f:
            return json.load(f)

    @staticmethod
    def update_user(username, data):
        user_file = os.path.join(PATHS["users"], f"{username}.json")
        with open(user_file, 'w') as f:
            json.dump(data, f)

    @staticmethod
    def authenticate(username, password):
        user = UserManager.get_user(username)
        if not user:
            return False
        
        salt = base64.b64decode(user["salt"])
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        stored_hash = hashlib.sha256(password.encode()).hexdigest()
        
        return user["password"] == stored_hash

# Система поддержки
class SupportSystem:
    @staticmethod
    def create_ticket(username, message):
        ticket_id = str(uuid4())
        ticket_file = os.path.join(PATHS["support"], f"{username}_{ticket_id}.json")
        
        ticket_data = {
            "id": ticket_id,
            "user": username,
            "message": message,
            "created": datetime.now().isoformat(),
            "status": "open",
            "responses": []
        }
        
        with open(ticket_file, 'w') as f:
            json.dump(ticket_data, f)
        
        return ticket_id

    @staticmethod
    def get_tickets(status="open"):
        tickets = []
        for file in glob.glob(os.path.join(PATHS["support"], "*.json")):
            with open(file, 'r') as f:
                data = json.load(f)
                if data["status"] == status:
                    tickets.append(data)
        return sorted(tickets, key=lambda x: x["created"])

    @staticmethod
    def respond_to_ticket(ticket_id, response, responder):
        for file in glob.glob(os.path.join(PATHS["support"], "*.json")):
            with open(file, 'r') as f:
                data = json.load(f)
            
            if data["id"] == ticket_id:
                data["responses"].append({
                    "from": responder,
                    "message": response,
                    "time": datetime.now().isoformat()
                })
                
                with open(file, 'w') as f:
                    json.dump(data, f)
                
                return True
        return False

    @staticmethod
    def close_ticket(ticket_id):
        for file in glob.glob(os.path.join(PATHS["support"], "*.json")):
            with open(file, 'r') as f:
                data = json.load(f)
            
            if data["id"] == ticket_id:
                data["status"] = "closed"
                
                with open(file, 'w') as f:
                    json.dump(data, f)
                
                return data["user"]
        return None

# Система обновлений
class UpdateManager:
    @staticmethod
    def check_for_updates():
        # В реальной реализации здесь будет запрос к серверу
        return False

    @staticmethod
    def download_update():
        # Заглушка для реальной реализации
        return True

    @staticmethod
    def apply_update():
        # В реальной реализации здесь будет замена исполняемого файла
        return True

# Основной класс приложения
class WarsawXApp:
    def __init__(self):
        if not setup_directories():
            print("Не удалось инициализировать файловую систему. Приложение будет закрыто.")
            sys.exit(1)
            
        self.current_user = None
        self.check_integrity()
        self.check_updates()
        self.ensure_admin()
        self.load_language()
        self.run()

    def check_integrity(self):
        # Проверка целостности файлов
        if os.path.exists(PATHS["integrity"]):
            with open(PATHS["integrity"], 'r') as f:
                stored_hash = f.read().strip()
            
            current_hash = hashlib.sha256(open(__file__, 'rb').read()).hexdigest()
            
            if stored_hash != current_hash:
                print("Целостность приложения нарушена!")
                sys.exit(1)

    def check_updates(self):
        if UpdateManager.check_for_updates():
            if UpdateManager.download_update():
                UpdateManager.apply_update()
                print("Приложение было обновлено. Пожалуйста, перезапустите.")
                sys.exit(0)

    def ensure_admin(self):
        if not UserManager.is_username_taken(CONFIG["admin_username"]):
            UserManager.create_user(CONFIG["admin_username"], os.urandom(16).hex())

    def load_language(self):
        # Загрузка языковых настроек
        if os.path.exists(PATHS["language"]):
            with open(PATHS["language"], 'r') as f:
                self.language = f.read().strip()
        else:
            self.language = "en"

    def run(self):
        while True:
            if not self.current_user:
                self.auth_menu()
            else:
                if self.current_user == CONFIG["admin_username"]:
                    self.admin_menu()
                else:
                    self.main_menu()

    def auth_menu(self):
        print(f"\n{CONFIG['app_title']}")
        print("1. Войти")
        print("2. Зарегистрироваться")
        print("3. Выход")
        
        choice = input("Выберите действие: ")
        
        if choice == "1":
            self.login()
        elif choice == "2":
            self.register()
        elif choice == "3":
            sys.exit()
        else:
            print("Неверный выбор")

    def login(self):
        username = input("Имя пользователя: ")
        password = getpass("Пароль: ")
        
        if UserManager.authenticate(username, password):
            self.current_user = username
            print(f"Добро пожаловать, {username}!")
        else:
            print("Неверные учетные данные")

    def register(self):
        while True:
            username = input("Придумайте имя пользователя: ")
            if not UserManager.validate_username(username):
                print(f"Имя должно быть от {CONFIG['min_username_len']} до {CONFIG['max_username_len']} символов (A-Z, a-z, 0-9, '_-)")
                continue
                
            if UserManager.is_username_taken(username):
                print("Имя уже занято")
            else:
                break
        
        password = getpass("Придумайте пароль: ")
        UserManager.create_user(username, password)
        print("Регистрация успешна!")

    def main_menu(self):
        while True:
            print("\nГлавное меню")
            print("1. Чаты")
            print("2. Друзья")
            print("3. Профиль")
            print("4. Поддержка")
            print("5. Выход")
            
            choice = input("Выберите действие: ")
            
            if choice == "1":
                self.chats_menu()
            elif choice == "2":
                self.friends_menu()
            elif choice == "3":
                self.profile_menu()
            elif choice == "4":
                self.support_menu()
            elif choice == "5":
                self.current_user = None
                return
            else:
                print("Неверный выбор")

    def support_menu(self):
        print("\nПоддержка")
        print("1. Новый запрос")
        print("2. Мои запросы")
        print("3. Назад")
        
        choice = input("Выберите действие: ")
        
        if choice == "1":
            message = input("Опишите ваш вопрос: ")
            ticket_id = SupportSystem.create_ticket(self.current_user, message)
            print(f"Запрос создан (ID: {ticket_id})")
        elif choice == "2":
            tickets = SupportSystem.get_tickets()
            user_tickets = [t for t in tickets if t["user"] == self.current_user]
            
            for ticket in user_tickets:
                print(f"\nID: {ticket['id']}")
                print(f"Дата: {ticket['created']}")
                print(f"Статус: {ticket['status']}")
                print(f"Сообщение: {ticket['message']}")
                
                for resp in ticket["responses"]:
                    print(f"\nОтвет от {resp['from']}:")
                    print(resp["message"])
        elif choice == "3":
            return
        else:
            print("Неверный выбор")

    def admin_menu(self):
        while True:
            print("\nАдмин-панель")
            print("1. Запросы в поддержку")
            print("2. Обновить приложение")
            print("3. Назад")
            
            choice = input("Выберите действие: ")
            
            if choice == "1":
                self.admin_support_tickets()
            elif choice == "2":
                self.admin_update_app()
            elif choice == "3":
                return
            else:
                print("Неверный выбор")

    def admin_support_tickets(self):
        tickets = SupportSystem.get_tickets()
        
        print("\nОткрытые запросы:")
        for ticket in tickets:
            print(f"\nID: {ticket['id']}")
            print(f"Пользователь: {ticket['user']}")
            print(f"Дата: {ticket['created']}")
            print(f"Сообщение: {ticket['message']}")
            
            print("\n1. Ответить")
            print("2. Закрыть")
            print("3. Пропустить")
            
            action = input("Выберите действие: ")
            
            if action == "1":
                response = input("Ваш ответ: ")
                SupportSystem.respond_to_ticket(ticket["id"], response, CONFIG["admin_username"])
            elif action == "2":
                username = SupportSystem.close_ticket(ticket["id"])
                print(f"Запрос от {username} закрыт")

    def admin_update_app(self):
        print("\nОбновление приложения")
        if UpdateManager.check_for_updates():
            print("Доступно новое обновление")
            if input("Установить обновление? (y/n): ").lower() == 'y':
                if UpdateManager.download_update():
                    if UpdateManager.apply_update():
                        print("Приложение будет обновлено после перезапуска")
                        sys.exit(0)
        else:
            print("У вас последняя версия")

    def view_profile(self, username):
        user = UserManager.get_user(username)
        if not user:
            print("Пользователь не найден")
            return
        
        print(f"\nПрофиль: {username}")
        print(f"Дата регистрации: {user['created']}")
        
        if self.current_user == CONFIG["admin_username"]:
            print("\nАдминистратор:")
            print("1. Отправить сообщение")
            print("2. Назад")
            
            choice = input("Выберите действие: ")
            if choice == "1":
                message = input("Сообщение: ")
                # Реализация отправки сообщения

    # Заглушки для меню
    def chats_menu(self):
        print("\nЧаты - в разработке")
        time.sleep(1)
    
    def friends_menu(self):
        print("\nДрузья - в разработке")
        time.sleep(1)
    
    def profile_menu(self):
        print("\nПрофиль - в разработке")
        time.sleep(1)

if __name__ == "__main__":
    # Проверка операционной системы
    if platform.system() == "Linux":
        # Для Linux используем другую базовую директорию
        BASE_DIR = os.path.join(os.path.expanduser('~/.config'), APP_NAME)
        PATHS = {key: os.path.join(BASE_DIR, path) for key, path in PATHS.items()}
        PATHS["app_exe"] = os.path.join(BASE_DIR, "warsawx")
    
    # Обычный запуск приложения
    app = WarsawXApp()
