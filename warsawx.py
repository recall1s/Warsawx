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
import getpass
import wave
import socket

# Конфигурация
APP_NAME = "warsawx"
BASE_DIR = os.path.join(os.getenv('APPDATA', os.path.expanduser('~/.config')), APP_NAME)
CONFIG = {
    "app_title": "WarsawX",
    "admin_username": "Recall's",  # Специальное имя с апострофом
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
        "pl": "Polski",  # Польский язык
        "sr": "Српски",
        "uk": "Українська",
        "ar": "العربية",
        "de": "Deutsch",
        "nl": "Nederlands",
        "el": "Ελληνικά"
    },
    "default_language": "pl"  # Польский по умолчанию
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
    "voice_chats": os.path.join(BASE_DIR, "voice_chats"),
    "sessions": os.path.join(BASE_DIR, "sessions.json"),
    "app_exe": os.path.join(BASE_DIR, "warsawx")
}

# Системные сообщения на разных языках
MESSAGES = {
    "en": {
        # ... (как в предыдущей версии) ...
    },
    "pl": {
        "welcome": "=== WarsawX ===",
        "select_language": "Proszę wybrać język:",
        "register": "Rejestracja",
        "login": "Zaloguj się",
        "exit": "Wyjdź",
        "select_option": "Wybierz opcję: ",
        "invalid_choice": "Nieprawidłowy wybór",
        "registration": "--- Rejestracja ---",
        "enter_nickname": "Wprowadź nazwę użytkownika (3-17 znaków, tylko A-Z, a-z, 0-9, -_): ",
        "invalid_nickname": "Nieprawidłowa nazwa użytkownika. Używaj tylko liter, cyfr, - i _",
        "nickname_taken": "Nazwa użytkownika jest już zajęta",
        "set_password": "Ustaw hasło: ",
        "reg_success": "Rejestracja zakończona sukcesem!",
        "press_enter": "Naciśnij Enter, aby kontynuować...",
        "login_title": "--- Logowanie ---",
        "enter_password": "Hasło: ",
        "welcome_user": "Witaj, {}!",
        "auth_failed": "Uwierzytelnienie nie powiodło się",
        "login_failed": "Logowanie nie powiodło się",
        "main_menu": "--- Menu główne ---",
        "create_chat": "Utwórz czat",
        "join_chat": "Dołącz do czatu",
        "profile_settings": "Ustawienia profilu",
        "friends": "Znajomi",
        "logout": "Wyloguj się",
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
        "view_profile": "Wyświetl profil",
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
        "friend_added": "{} dodany do znajomych",
        "friend_removed": "{} usunięty ze znajomych",
        "voice_call": "Rozmowa głosowa",
        "call_user": "Zadzwoń do użytkownika",
        "active_calls": "Aktywne rozmowy",
        "enter_username_to_call": "Wprowadź nazwę użytkownika: ",
        "calling": "Dzwonienie do {}...",
        "incoming_call": "Przychodzące połączenie od {}",
        "call_options": "1. Przyjmij\n2. Odrzuć\n3. Wyświetl profil",
        "call_connected": "Połączenie z {} nawiązane",
        "call_ended": "Połączenie zakończone",
        "end_call": "Zakończ połączenie",
        "chat_name_prompt": "Podaj nazwę czatu: ",
        "chat_owner_options": "Opcje właściciela czatu",
        "add_participant": "Dodaj uczestnika",
        "remove_participant": "Usuń uczestnika",
        "leave_chat": "Opuść czat",
        "block_user": "Zablokuj użytkownika",
        "unblock_user": "Odblokuj użytkownika",
        "bio_prompt": "Wprowadź swoje BIO: ",
        "perm_code": "Twój stały kod: {}",
        "forced_code": "Twój kod wymuszony: {}",
        "audio_settings": "Ustawienia audio",
        "input_device": "Urządzenie wejściowe",
        "output_device": "Urządzenie wyjściowe",
        "select_device": "Wybierz urządzenie:",
        "device_settings_saved": "Ustawienia urządzenia zapisane"
    }
}

def setup_directories():
    try:
        os.makedirs(BASE_DIR, exist_ok=True)
        os.makedirs(PATHS["users"], exist_ok=True)
        os.makedirs(PATHS["support"], exist_ok=True)
        os.makedirs(PATHS["chats"], exist_ok=True)
        os.makedirs(PATHS["voice_chats"], exist_ok=True)
        
        required_files = {
            PATHS["nicknames"]: "",
            PATHS["language"]: CONFIG["default_language"],
            PATHS["lockouts"]: {},
            PATHS["sessions"]: {},
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

class UserManager:
    @staticmethod
    def validate_username(username):
        if len(username) < CONFIG["min_username_len"] or len(username) > CONFIG["max_username_len"]:
            return False
        
        # Разрешаем апостроф только для администратора
        allowed = string.ascii_letters + string.digits + "_-"
        if username == CONFIG["admin_username"]:
            allowed += "'"
        
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
        
        # Генерируем коды
        perm_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
        forced_code = ''.join(random.choices(string.digits, k=12))
        
        user_data = {
            "password": hashlib.sha256(password.encode()).hexdigest(),
            "created": datetime.now().isoformat(),
            "friends": [],
            "blocked": [],
            "friend_requests": [],
            "chats": {
                CONFIG["support_chat"]: {"created": datetime.now().isoformat()},
                CONFIG["favorites_chat"]: {"created": datetime.now().isoformat()}
            },
            "perm_code": perm_code,
            "forced_code": forced_code,
            "bio": "",
            "audio_settings": {
                "input_device": -1,
                "output_device": -1
            }
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
    def authenticate(username, password):
        user = UserManager.get_user(username)
        if not user:
            return False
        return user["password"] == hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def save_session(username):
        sessions = {}
        if os.path.exists(PATHS["sessions"]):
            with open(PATHS["sessions"], 'r') as f:
                sessions = json.load(f)
        
        sessions[username] = datetime.now().isoformat()
        
        with open(PATHS["sessions"], 'w') as f:
            json.dump(sessions, f)
    
    @staticmethod
    def get_sessions():
        if os.path.exists(PATHS["sessions"]):
            with open(PATHS["sessions"], 'r') as f:
                return json.load(f)
        return {}

class ChatManager:
    @staticmethod
    def create_chat(owner, name):
        chat_id = str(uuid4())[:8]
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
            user["chats"][chat_id] = {"name": name, "created": datetime.now().isoformat()}
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
    def update_chat(chat_id, data):
        chat_file = os.path.join(PATHS["chats"], f"{chat_id}.json")
        with open(chat_file, 'w') as f:
            json.dump(data, f)

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
        
        ChatManager.update_chat(chat_id, chat)
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
                user["chats"][chat_id] = {"name": chat["name"], "created": datetime.now().isoformat()}
                UserManager.update_user(username, user)
            
            ChatManager.update_chat(chat_id, chat)
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
            
            ChatManager.update_chat(chat_id, chat)
            return True
        return False
    
    @staticmethod
    def user_join(chat_id, username):
        chat = ChatManager.get_chat(chat_id)
        if not chat:
            return False
            
        if username not in chat["active_users"]:
            chat["active_users"].append(username)
            ChatManager.update_chat(chat_id, chat)
            return True
        return False
    
    @staticmethod
    def user_leave(chat_id, username):
        chat = ChatManager.get_chat(chat_id)
        if not chat:
            return False
            
        if username in chat["active_users"]:
            chat["active_users"].remove(username)
            ChatManager.update_chat(chat_id, chat)
            return True
        return False

class VoiceCallManager:
    active_calls = {}
    
    @staticmethod
    def start_call(caller, callee):
        call_id = str(uuid4())[:8]
        VoiceCallManager.active_calls[call_id] = {
            "caller": caller,
            "callee": callee,
            "status": "ringing",
            "start_time": datetime.now(),
            "audio_thread": None,
            "stop_event": threading.Event()
        }
        return call_id
    
    @staticmethod
    def accept_call(call_id):
        if call_id in VoiceCallManager.active_calls:
            VoiceCallManager.active_calls[call_id]["status"] = "active"
            return True
        return False
    
    @staticmethod
    def end_call(call_id):
        if call_id in VoiceCallManager.active_calls:
            if "stop_event" in VoiceCallManager.active_calls[call_id]:
                VoiceCallManager.active_calls[call_id]["stop_event"].set()
            
            if "audio_thread" in VoiceCallManager.active_calls[call_id]:
                VoiceCallManager.active_calls[call_id]["audio_thread"].join(timeout=1.0)
            
            del VoiceCallManager.active_calls[call_id]
            return True
        return False
    
    @staticmethod
    def start_audio_stream(call_id, user, input_device, output_device):
        call = VoiceCallManager.active_calls.get(call_id)
        if not call or call["status"] != "active":
            return
            
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        
        audio = pyaudio.PyAudio()
        
        # Устройство ввода
        stream_in = audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
            input_device_index=input_device
        )
        
        # Устройство вывода
        stream_out = audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            output=True,
            frames_per_buffer=CHUNK,
            output_device_index=output_device
        )
        
        while not call["stop_event"].is_set():
            try:
                data = stream_in.read(CHUNK)
                stream_out.write(data)
            except Exception as e:
                print(f"Audio error: {e}")
                break
        
        stream_in.stop_stream()
        stream_in.close()
        stream_out.stop_stream()
        stream_out.close()
        audio.terminate()

class WarsawXApp:
    def __init__(self):
        if not setup_directories():
            print("Failed to initialize file system")
            sys.exit(1)
            
        self.current_user = None
        self.language = CONFIG["default_language"]
        self.load_language()
        self.ensure_admin()
        self.restore_session()
        self.audio = pyaudio.PyAudio()
        self.run()

    def t(self, key, *args):
        if self.language in MESSAGES and key in MESSAGES[self.language]:
            return MESSAGES[self.language][key].format(*args)
        return key

    def load_language(self):
        if os.path.exists(PATHS["language"]):
            with open(PATHS["language"], 'r') as f:
                lang = f.read().strip()
                if lang in CONFIG["languages"]:
                    self.language = lang
        else:
            self.select_language()

    def select_language(self):
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
        if not UserManager.is_username_taken(CONFIG["admin_username"]):
            # Запросим пароль у пользователя для администратора
            print(f"Creating admin account: {CONFIG['admin_username']}")
            password = getpass(self.t("set_password"))
            perm_code, forced_code = UserManager.create_user(CONFIG["admin_username"], password)
            print(self.t("perm_code", perm_code))
            print(self.t("forced_code", forced_code))

    def restore_session(self):
        sessions = UserManager.get_sessions()
        for username, login_time in sessions.items():
            if (datetime.now() - datetime.fromisoformat(login_time)) < timedelta(days=7):
                self.current_user = username
                print(self.t('welcome_user', username))
                time.sleep(1)
                break

    def clear_screen(self):
        if platform.system() == "Windows":
            os.system('cls')
        else:
            os.system('clear')

    def run(self):
        self.clear_screen()
        while True:
            if not self.current_user:
                self.auth_menu()
            else:
                if self.current_user == CONFIG["admin_username"]:
                    self.admin_menu()
                else:
                    self.main_menu()

    # ... (остальные методы с учетом всех ваших требований) ...

    def create_chat(self):
        chat_name = input(self.t("chat_name_prompt"))
        chat_id = ChatManager.create_chat(self.current_user, chat_name)
        print(self.t('chat_created', chat_id))
        
        # Добавляем участников
        while True:
            friend = input(self.t("enter_friend_username") + " (enter to finish): ")
            if not friend:
                break
                
            if UserManager.get_user(friend):
                if ChatManager.add_participant(chat_id, friend):
                    print(f"{friend} added to chat")
                else:
                    print(f"Failed to add {friend}")
            else:
                print(f"User {friend} not found")
        
        input(self.t("press_enter"))

    def join_chat(self):
        chat_id = input(self.t("enter_chat_code")).strip()
        chat = ChatManager.get_chat(chat_id)
        
        if not chat:
            print(self.t('chat_not_found'))
            time.sleep(1)
            return
        
        if self.current_user not in chat["participants"]:
            print("You are not a participant of this chat")
            time.sleep(1)
            return
        
        # Отмечаем пользователя как активного
        ChatManager.user_join(chat_id, self.current_user)
            
        print(f"\n{self.t('chat_history')}")
        print(f"Chat: {chat['name']} (ID: {chat_id})")
        print(f"Active users: {', '.join(chat['active_users'])}")
        
        for msg in chat["messages"]:
            timestamp = datetime.fromisoformat(msg['timestamp']).strftime('%Y-%m-%d %H:%M')
            print(f"[{timestamp}] {msg['sender']}: {msg['message']}")
        
        print("\n")
        while True:
            message = input(self.t("type_message"))
            if message.lower() == "/exit":
                break
            if ChatManager.add_message(chat_id, self.current_user, message):
                print(self.t('message_sent'))
        
        # Отмечаем выход пользователя
        ChatManager.user_leave(chat_id, self.current_user)

    def voice_call_menu(self):
        # ... (реализация голосовых звонков) ...
        pass

    def audio_settings_menu(self):
        user = UserManager.get_user(self.current_user)
        if not user:
            return
            
        print("\n" + self.t("audio_settings"))
        
        # Список устройств ввода
        print("\n" + self.t("input_device"))
        for i in range(self.audio.get_device_count()):
            dev = self.audio.get_device_info_by_index(i)
            if dev['maxInputChannels'] > 0:
                print(f"{i}. {dev['name']}")
        
        choice = input(self.t("select_device") + ": ")
        if choice.isdigit():
            user["audio_settings"]["input_device"] = int(choice)
        
        # Список устройств вывода
        print("\n" + self.t("output_device"))
        for i in range(self.audio.get_device_count()):
            dev = self.audio.get_device_info_by_index(i)
            if dev['maxOutputChannels'] > 0:
                print(f"{i}. {dev['name']}")
        
        choice = input(self.t("select_device") + ": ")
        if choice.isdigit():
            user["audio_settings"]["output_device"] = int(choice)
        
        UserManager.update_user(self.current_user, user)
        print(self.t("device_settings_saved"))
        time.sleep(1)

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
