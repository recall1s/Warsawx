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
import pyaudio
import socket
import wave

# Конфигурация
APP_NAME = "warsawx"
BASE_DIR = os.path.join(os.getenv('APPDATA', os.path.expanduser('~/.config')), APP_NAME)
CONFIG = {
    "app_title": "WarsawX",
    "admin_username": "Recall's",
    "min_username_len": 3,
    "max_username_len": 17,
    "support_chat": "warsawx_support",
    "favorites_chat": "warsawx_favorites",
    "languages": {
        "en": "English",
        "ru": "Русский",
        "cs": "Čeština",
        "zh": "中文",
        "ja": "日本語",
        "pl": "Polski",
        "sr": "Српски",
        "uk": "Українська",
        "ar": "العربية",
        "de": "Deutsch",
        "nl": "Nederlands",
        "el": "Ελληνικά"
    }
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
    "chats": os.path.join(BASE_DIR, "chats"),
    "sessions": os.path.join(BASE_DIR, "sessions"),
    "app_exe": os.path.join(BASE_DIR, "warsawx")
}

# Системные сообщения на разных языках
MESSAGES = {
    "en": {
        # ... [остальные переводы] ...
        "select_language": "Please select your language:",
        "enter_password": "Password: ",
        "perm_code": "Permanent code (3 chars): ",
        "forced_code": "Forced code (12 digits): ",
        "bio": "Bio: ",
        "save_session": "Remember me",
        "call_audio_settings": "Audio Settings",
        "input_device": "Input device: ",
        "output_device": "Output device: ",
        "block_user": "Block user",
        "unblock_user": "Unblock user",
        "create_chat_name": "Enter chat name: ",
        "chat_code": "Chat code: ",
        "invite_to_chat": "Invite to chat",
        "leave_chat": "Leave chat",
        "remove_from_chat": "Remove from chat",
        "chat_settings": "Chat Settings",
        "call_started": "Call started",
        "call_quality": "Call quality: {}",
    },
    "pl": {
        "welcome": "=== WarsawX ===",
        "select_language": "Proszę wybrać język:",
        "register": "Rejestracja",
        "login": "Zaloguj",
        "exit": "Wyjdź",
        "select_option": "Wybierz opcję: ",
        "invalid_choice": "Nieprawidłowy wybór",
        "registration": "--- Rejestracja ---",
        "enter_nickname": "Wprowadź nazwę użytkownika (3-17 znaków, tylko A-Z, a-z, 0-9, -_): ",
        "invalid_nickname": "Nieprawidłowa nazwa. Używaj tylko liter, cyfr, - i _",
        "nickname_taken": "Nazwa użytkownika jest już zajęta",
        "set_password": "Ustaw hasło: ",
        "reg_success": "Rejestracja zakończona sukcesem!",
        "press_enter": "Naciśnij Enter, aby kontynuować...",
        "login_title": "--- Logowanie ---",
        "enter_password": "Hasło: ",
        "perm_code": "Kod stały (3 znaki): ",
        "forced_code": "Kod wymuszony (12 cyfr): ",
        "welcome_user": "Witaj, {}!",
        "auth_failed": "Uwierzytelnienie nie powiodło się",
        "login_failed": "Logowanie nie powiodło się",
        "main_menu": "--- Menu główne ---",
        "create_chat": "Utwórz czat",
        "join_chat": "Dołącz do czatu",
        "profile_settings": "Ustawienia profilu",
        "friends": "Znajomi",
        "support": "Wsparcie",
        "logout": "Wyloguj",
        "back": "Wstecz",
        "chat_created": "Czat utworzony! Udostępnij ten kod: {}",
        "enter_chat_code": "Wprowadź kod czatu: ",
        "chat_not_found": "Czat nie znaleziony",
        "chat_history": "--- Historia czatu ---",
        "type_message": "Wpisz wiadomość (lub /exit, aby wyjść): ",
        "message_sent": "Wiadomość wysłana",
        "admin_menu": "--- Panel administratora ---",
        "view_requests": "Wyświetl prośby o wsparcie",
        "update_app": "Aktualizuj aplikację",
        "verification_requests": "--- Prośby o weryfikację ---",
        "no_requests": "Brak oczekujących próśb",
        "support_menu": "--- Wsparcie ---",
        "new_request": "Nowa prośba",
        "my_requests": "Moje prośby",
        "enter_message": "Wprowadź swoją wiadomość: ",
        "request_created": "Prośba utworzona (ID: {})",
        "view_profile": "Zobacz profil",
        "friends_menu": "--- Znajomi ---",
        "add_friend": "Dodaj znajomego",
        "friend_requests": "Prośby o dodanie do znajomych",
        "my_friends": "Moi znajomi",
        "enter_friend_username": "Wprowadź nazwę znajomego: ",
        "friend_request_sent": "Prośba o dodanie do znajomych wysłana do {}",
        "no_friend_requests": "Brak próśb o dodanie do znajomych",
        "incoming_requests": "Przychodzące prośby o dodanie do znajomych",
        "accept": "Akceptuj",
        "reject": "Odrzuć",
        "friend_added": "{} dodano do znajomych",
        "friend_removed": "{} usunięto ze znajomych",
        "voice_call": "Rozmowa głosowa",
        "call_user": "Zadzwoń do użytkownika",
        "active_calls": "Aktywne rozmowy",
        "enter_username_to_call": "Wprowadź nazwę użytkownika: ",
        "calling": "Dzwonię do {}...",
        "incoming_call": "Przychodzące połączenie od {}",
        "call_options": "1. Odbierz\n2. Odrzuć\n3. Zobacz profil",
        "call_connected": "Połączenie z {} nawiązane",
        "call_ended": "Rozmowa zakończona",
        "end_call": "Zakończ rozmowę",
        "bio": "Bio: ",
        "save_session": "Zapamiętaj mnie",
        "call_audio_settings": "Ustawienia dźwięku",
        "input_device": "Urządzenie wejściowe: ",
        "output_device": "Urządzenie wyjściowe: ",
        "block_user": "Zablokuj użytkownika",
        "unblock_user": "Odblokuj użytkownika",
        "create_chat_name": "Wprowadź nazwę czatu: ",
        "chat_code": "Kod czatu: ",
        "invite_to_chat": "Zaproś do czatu",
        "leave_chat": "Opuść czat",
        "remove_from_chat": "Usuń z czatu",
        "chat_settings": "Ustawienia czatu",
        "call_started": "Rozpoczęto rozmowę",
        "call_quality": "Jakość połączenia: {}",
    }
}

def setup_directories():
    try:
        os.makedirs(BASE_DIR, exist_ok=True)
        os.makedirs(PATHS["users"], exist_ok=True)
        os.makedirs(PATHS["support"], exist_ok=True)
        os.makedirs(PATHS["chats"], exist_ok=True)
        os.makedirs(PATHS["sessions"], exist_ok=True)
        
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
        
        if not os.path.exists(PATHS["master_key"]):
            with open(PATHS["master_key"], 'wb') as f:
                f.write(get_random_bytes(32))
        
        return True
    except Exception as e:
        print(f"Setup error: {e}")
        return False

class SessionManager:
    @staticmethod
    def create_session(username):
        session_id = hashlib.sha256(os.urandom(32)).hexdigest()
        session_file = os.path.join(PATHS["sessions"], f"{session_id}.json")
        
        session_data = {
            "username": username,
            "created": datetime.now().isoformat(),
            "expires": (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        with open(session_file, 'w') as f:
            json.dump(session_data, f)
        
        return session_id
    
    @staticmethod
    def get_session(session_id):
        session_file = os.path.join(PATHS["sessions"], f"{session_id}.json")
        if not os.path.exists(session_file):
            return None
        
        with open(session_file, 'r') as f:
            return json.load(f)
    
    @staticmethod
    def delete_session(session_id):
        session_file = os.path.join(PATHS["sessions"], f"{session_id}.json")
        if os.path.exists(session_file):
            os.remove(session_file)
            return True
        return False

class UserManager:
    @staticmethod
    def validate_username(username):
        if len(username) < CONFIG["min_username_len"] or len(username) > CONFIG["max_username_len"]:
            return False
        allowed = string.ascii_letters + string.digits + "_-'"
        return all(c in allowed for c in username)

    @staticmethod
    def is_username_taken(username):
        if not os.path.exists(PATHS["nicknames"]) or os.path.getsize(PATHS["nicknames"]) == 0:
            return False
        with open(PATHS["nicknames"], 'r') as f:
            return username in f.read().split()

    @staticmethod
    def create_user(username, password, perm_code=None, forced_code=None):
        if not perm_code:
            perm_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
        if not forced_code:
            forced_code = ''.join(random.choices(string.digits, k=12))
        
        user_file = os.path.join(PATHS["users"], f"{username}.json")
        
        user_data = {
            "password": hashlib.sha256(password.encode()).hexdigest(),
            "created": datetime.now().isoformat(),
            "friends": [],
            "blocked": [],
            "friend_requests": [],
            "chats": {},
            "bio": "",
            "perm_code": perm_code,
            "forced_code": forced_code
        }

        with open(user_file, 'w') as f:
            json.dump(user_data, f)
        
        with open(PATHS["nicknames"], 'a') as f:
            f.write(username + "\n")
        
        return perm_code, forced_code

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
    def authenticate(username, password=None, perm_code=None, forced_code=None):
        user = UserManager.get_user(username)
        if not user:
            return False
        
        if password:
            return user["password"] == hashlib.sha256(password.encode()).hexdigest()
        elif perm_code:
            return user["perm_code"] == perm_code
        elif forced_code:
            return user["forced_code"] == forced_code
        
        return False

class ChatManager:
    @staticmethod
    def create_chat(owner, name):
        chat_id = str(uuid4())[:7]
        chat_file = os.path.join(PATHS["chats"], f"{chat_id}.json")
        
        chat_data = {
            "id": chat_id,
            "name": name,
            "owner": owner,
            "participants": [owner],
            "messages": [],
            "created": datetime.now().isoformat(),
            "active_users": []
        }
        
        with open(chat_file, 'w') as f:
            json.dump(chat_data, f)
            
        # Добавляем чат владельцу
        user = UserManager.get_user(owner)
        if user:
            user["chats"][chat_id] = {
                "name": name,
                "created": datetime.now().isoformat()
            }
            UserManager.update_user(owner, user)
        
        return chat_id

    @staticmethod
    def get_chat(chat_id):
        chat_file = os.path.join(PATHS["chats"], f"{chat_id}.json")
        if not os.path.exists(chat_file):
            return None
        with open(chat_file, 'r') as f:
            return json.load(f)

    @staticmethod
    def add_message(chat_id, sender, message):
        chat = ChatManager.get_chat(chat_id)
        if not chat:
            return False
            
        chat["messages"].append({
            "sender": sender,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
        chat_file = os.path.join(PATHS["chats"], f"{chat_id}.json")
        with open(chat_file, 'w') as f:
            json.dump(chat, f)
            
        return True
    
    @staticmethod
    def add_participant(chat_id, username):
        chat = ChatManager.get_chat(chat_id)
        if not chat:
            return False
            
        if username not in chat["participants"]:
            chat["participants"].append(username)
            
            # Добавляем чат пользователю
            user = UserManager.get_user(username)
            if user:
                user["chats"][chat_id] = {
                    "name": chat["name"],
                    "created": datetime.now().isoformat()
                }
                UserManager.update_user(username, user)
            
            chat_file = os.path.join(PATHS["chats"], f"{chat_id}.json")
            with open(chat_file, 'w') as f:
                json.dump(chat, f)
            
            return True
        return False
    
    @staticmethod
    def remove_participant(chat_id, username):
        chat = ChatManager.get_chat(chat_id)
        if not chat:
            return False
            
        if username in chat["participants"]:
            chat["participants"].remove(username)
            
            # Удаляем чат у пользователя
            user = UserManager.get_user(username)
            if user and chat_id in user["chats"]:
                del user["chats"][chat_id]
                UserManager.update_user(username, user)
            
            chat_file = os.path.join(PATHS["chats"], f"{chat_id}.json")
            with open(chat_file, 'w') as f:
                json.dump(chat, f)
            
            return True
        return False
    
    @staticmethod
    def user_joined(chat_id, username):
        chat = ChatManager.get_chat(chat_id)
        if not chat:
            return False
            
        if username not in chat["active_users"]:
            chat["active_users"].append(username)
            
            chat_file = os.path.join(PATHS["chats"], f"{chat_id}.json")
            with open(chat_file, 'w') as f:
                json.dump(chat, f)
            
            return True
        return False
    
    @staticmethod
    def user_left(chat_id, username):
        chat = ChatManager.get_chat(chat_id)
        if not chat:
            return False
            
        if username in chat["active_users"]:
            chat["active_users"].remove(username)
            
            chat_file = os.path.join(PATHS["chats"], f"{chat_id}.json")
            with open(chat_file, 'w') as f:
                json.dump(chat, f)
            
            return True
        return False

class VoiceCallManager:
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.stream_in = None
        self.stream_out = None
        self.is_calling = False
        self.call_socket = None
        self.call_thread = None
    
    def start_call(self, host, port):
        self.call_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.call_socket.connect((host, port))
        self.is_calling = True
        
        # Start audio streams
        self.stream_in = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )
        
        self.stream_out = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            output=True,
            frames_per_buffer=self.CHUNK
        )
        
        # Start sending and receiving audio
        self.call_thread = threading.Thread(target=self._call_loop)
        self.call_thread.daemon = True
        self.call_thread.start()
    
    def accept_call(self, conn):
        self.call_socket = conn
        self.is_calling = True
        
        # Start audio streams
        self.stream_in = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )
        
        self.stream_out = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            output=True,
            frames_per_buffer=self.CHUNK
        )
        
        # Start sending and receiving audio
        self.call_thread = threading.Thread(target=self._call_loop)
        self.call_thread.daemon = True
        self.call_thread.start()
    
    def _call_loop(self):
        while self.is_calling:
            try:
                # Send audio
                data = self.stream_in.read(self.CHUNK)
                self.call_socket.sendall(data)
                
                # Receive audio
                data = self.call_socket.recv(self.CHUNK * 2)
                self.stream_out.write(data)
            except Exception as e:
                print(f"Call error: {e}")
                self.end_call()
    
    def end_call(self):
        self.is_calling = False
        
        if self.stream_in:
            self.stream_in.stop_stream()
            self.stream_in.close()
        
        if self.stream_out:
            self.stream_out.stop_stream()
            self.stream_out.close()
        
        if self.call_socket:
            self.call_socket.close()
        
        if self.call_thread and self.call_thread.is_alive():
            self.call_thread.join(timeout=1.0)
    
    def get_audio_devices(self):
        devices = []
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            devices.append({
                "index": i,
                "name": device_info.get('name', 'Unknown'),
                "max_input_channels": device_info.get('maxInputChannels', 0),
                "max_output_channels": device_info.get('maxOutputChannels', 0)
            })
        return devices

class WarsawXApp:
    def __init__(self):
        if not setup_directories():
            print("Failed to initialize file system")
            sys.exit(1)
            
        self.current_user = None
        self.language = "en"
        self.voice_manager = VoiceCallManager()
        self.load_session()
        self.select_language()
        self.ensure_admin()
        self.run()

    def load_session(self):
        session_files = glob.glob(os.path.join(PATHS["sessions"], "*.json"))
        if session_files:
            try:
                # Берем последнюю сессию
                session_file = max(session_files, key=os.path.getctime)
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                
                # Проверяем срок действия
                expires = datetime.fromisoformat(session_data["expires"])
                if datetime.now() < expires:
                    self.current_user = session_data["username"]
            except:
                pass

    def save_session(self):
        if self.current_user:
            session_id = SessionManager.create_session(self.current_user)
            # Можно сохранить session_id в файл для автоматического входа

    def t(self, key, *args):
        if self.language in MESSAGES and key in MESSAGES[self.language]:
            return MESSAGES[self.language][key].format(*args)
        return key

    def select_language(self):
        if os.path.exists(PATHS["language"]):
            with open(PATHS["language"], 'r') as f:
                lang = f.read().strip()
                if lang in CONFIG["languages"]:
                    self.language = lang
                    return
        
        self.clear_screen()
        print(self.t("select_language"))
        for i, (code, name) in enumerate(CONFIG["languages"].items(), 1):
            print(f"{i}. {name}")
        
        while True:
            try:
                choice = int(input(self.t("select_option")))
                if 1 <= choice <= len(CONFIG["languages"]):
                    lang_code = list(CONFIG["languages"].keys())[choice-1]
                    with open(PATHS["language"], 'w') as f:
                        f.write(lang_code)
                    self.language = lang_code
                    return
            except:
                print(self.t("invalid_choice"))

    def ensure_admin(self):
        admin_username = CONFIG["admin_username"]
        if not UserManager.is_username_taken(admin_username):
            # Запрашиваем пароль у пользователя при первом запуске
            print("Creating admin account...")
            password = getpass("Enter password for admin account: ")
            perm_code, forced_code = UserManager.create_user(admin_username, password)
            print(f"Admin account {admin_username} created!")
            print(f"Permanent code: {perm_code}")
            print(f"Forced code: {forced_code}")

    # ... [остальные методы без изменений] ...

    def profile_menu(self):
        while True:
            self.clear_screen()
            user = UserManager.get_user(self.current_user)
            
            print(f"\n{self.t('profile_settings')}: {self.current_user}")
            print(f"1. {self.t('bio')}: {user.get('bio', '')}")
            print(f"2. {self.t('view_profile')}")
            print(f"3. {self.t('call_audio_settings')}")
            print(f"0. {self.t('back')}")
            
            choice = input(self.t("select_option"))
            
            if choice == "1":
                new_bio = input(self.t("bio"))
                user["bio"] = new_bio
                UserManager.update_user(self.current_user, user)
                print("Bio updated!")
                time.sleep(1)
            elif choice == "2":
                self.view_profile(self.current_user)
            elif choice == "3":
                self.audio_settings()
            elif choice == "0":
                return
            else:
                print(self.t('invalid_choice'))
                time.sleep(1)

    def audio_settings(self):
        devices = self.voice_manager.get_audio_devices()
        
        self.clear_screen()
        print(f"\n{self.t('call_audio_settings')}")
        
        print("\nInput devices:")
        for i, device in enumerate(devices):
            if device["max_input_channels"] > 0:
                print(f"{i}. {device['name']}")
        
        print("\nOutput devices:")
        for i, device in enumerate(devices):
            if device["max_output_channels"] > 0:
                print(f"{i}. {device['name']}")
        
        input("\nPress Enter to continue...")

    # ... [остальные методы без изменений] ...

def launch_in_separate_terminal():
    if platform.system() == "Windows":
        subprocess.Popen(['start', 'cmd', '/c', 'python', os.path.abspath(__file__)], shell=True)
    elif platform.system() == "Linux":
        subprocess.Popen(['x-terminal-emulator', '-e', f'python3 {os.path.abspath(__file__)}'])
    elif platform.system() == "Darwin":
        subprocess.Popen(['open', '-a', 'Terminal', os.path.abspath(__file__)])

if __name__ == "__main__":
    # Для Linux используем другую базовую директорию
    if platform.system() == "Linux":
        BASE_DIR = os.path.join(os.path.expanduser('~/.config'), APP_NAME)
        PATHS = {key: os.path.join(BASE_DIR, path) for key, path in PATHS.items()}
        PATHS["app_exe"] = os.path.join(BASE_DIR, "warsawx")
    
    # Запуск в отдельном терминале
    if len(sys.argv) > 1 and sys.argv[1] == 'gui':
        launch_in_separate_terminal()
        sys.exit(0)
    
    # Обычный запуск приложения
    app = WarsawXApp()
