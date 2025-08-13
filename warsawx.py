import os
import json
import random
import string
import hashlib
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
import socket
import sounddevice as sd
import numpy as np
import wave
import tempfile

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
    },
    "permanent_code_length": 3,
    "forced_code_length": 12,
    "chat_code_length": 6
}

# Пути к файлам
PATHS = {
    "users": os.path.join(BASE_DIR, "Users"),
    "nicknames": os.path.join(BASE_DIR, "nicknames.txt"),
    "language": os.path.join(BASE_DIR, "language.txt"),
    "lockouts": os.path.join(BASE_DIR, "lockouts.json"),
    "support": os.path.join(BASE_DIR, "support_chats"),
    "chats": os.path.join(BASE_DIR, "chats"),
    "sessions": os.path.join(BASE_DIR, "sessions"),
    "app_exe": os.path.join(BASE_DIR, "warsawx")
}

# Системные сообщения на разных языках
MESSAGES = {
    "en": {
        "welcome": "=== WarsawX ===",
        "select_language": "Please select your language:",
        "register": "Register",
        "login": "Login",
        "exit": "Exit",
        "select_option": "Select an option: ",
        "invalid_choice": "Invalid choice",
        "registration": "--- Registration ---",
        "enter_nickname": "Enter username (3-17 chars, only A-Z, a-z, 0-9, '-_): ",
        "invalid_nickname": "Invalid username. Use only letters, digits, ' - and _",
        "nickname_taken": "Username already taken",
        "set_password": "Set password: ",
        "reg_success": "Registration successful!",
        "press_enter": "Press Enter to continue...",
        "login_title": "--- Login ---",
        "enter_password": "Password: ",
        "enter_permanent_code": "Permanent code: ",
        "enter_forced_code": "Forced code: ",
        "welcome_user": "Welcome, {}!",
        "auth_failed": "Authentication failed",
        "login_failed": "Login failed",
        "main_menu": "--- Main Menu ---",
        "create_chat": "Create chat",
        "join_chat": "Join chat",
        "profile_settings": "Profile settings",
        "friends": "Friends",
        "support": "Support",
        "logout": "Logout",
        "back": "Back",
        "chat_created": "Chat created! Share this code: {}",
        "enter_chat_code": "Enter chat code: ",
        "chat_not_found": "Chat not found",
        "chat_history": "--- Chat History ---",
        "type_message": "Type message (or /exit to leave): ",
        "message_sent": "Message sent",
        "admin_menu": "--- Admin Panel ---",
        "view_requests": "View support requests",
        "update_app": "Update application",
        "verification_requests": "--- Verification Requests ---",
        "no_requests": "No pending requests",
        "support_menu": "--- Support ---",
        "new_request": "New request",
        "my_requests": "My requests",
        "enter_message": "Enter your message: ",
        "request_created": "Request created (ID: {})",
        "view_profile": "View profile",
        "friends_menu": "--- Friends ---",
        "add_friend": "Add friend",
        "friend_requests": "Friend requests",
        "my_friends": "My friends",
        "enter_friend_username": "Enter friend's username: ",
        "friend_request_sent": "Friend request sent to {}",
        "no_friend_requests": "No friend requests",
        "incoming_requests": "Incoming friend requests",
        "accept": "Accept",
        "reject": "Reject",
        "friend_added": "{} added to friends",
        "friend_removed": "{} removed from friends",
        "voice_call": "Voice call",
        "call_user": "Call user",
        "active_calls": "Active calls",
        "enter_username_to_call": "Enter username to call: ",
        "calling": "Calling {}...",
        "incoming_call": "Incoming call from {}",
        "call_options": "1. Accept\n2. Decline\n3. View profile",
        "call_connected": "Call connected with {}",
        "call_ended": "Call ended",
        "end_call": "End call",
        "bio": "Bio",
        "enter_bio": "Enter your bio: ",
        "bio_updated": "Bio updated",
        "permanent_code": "Permanent code: {}",
        "forced_code": "Forced code: {}",
        "chat_name": "Chat name: ",
        "chat_participants": "Participants: ",
        "chat_owner": "Owner: {}",
        "chat_settings": "Chat settings",
        "add_participant": "Add participant",
        "remove_participant": "Remove participant",
        "leave_chat": "Leave chat",
        "block_user": "Block user",
        "unblock_user": "Unblock user",
        "user_blocked": "User {} blocked",
        "user_unblocked": "User {} unblocked",
        "blocked_users": "Blocked users",
        "select_audio_device": "Select audio device:",
        "audio_input": "Input device: {}",
        "audio_output": "Output device: {}",
        "audio_settings": "Audio settings"
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
        "enter_nickname": "Wprowadź nazwę użytkownika (3-17 znaków, tylko A-Z, a-z, 0-9, '-_): ",
        "invalid_nickname": "Nieprawidłowa nazwa użytkownika. Używaj tylko liter, cyfr, ' - i _",
        "nickname_taken": "Nazwa użytkownika jest już zajęta",
        "set_password": "Ustaw hasło: ",
        "reg_success": "Rejestracja zakończona sukcesem!",
        "press_enter": "Naciśnij Enter, aby kontynuować...",
        "login_title": "--- Logowanie ---",
        "enter_password": "Hasło: ",
        "enter_permanent_code": "Kod stały: ",
        "enter_forced_code": "Kod wymuszony: ",
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
        "back": "Powrót",
        "chat_created": "Czat utworzony! Udostępnij ten kod: {}",
        "enter_chat_code": "Wprowadź kod czatu: ",
        "chat_not_found": "Czat nie znaleziony",
        "chat_history": "--- Historia czatu ---",
        "type_message": "Wpisz wiadomość (lub /exit, aby wyjść): ",
        "message_sent": "Wiadomość wysłana",
        "admin_menu": "--- Panel administratora ---",
        "view_requests": "Wyświetl żądania wsparcia",
        "update_app": "Aktualizuj aplikację",
        "verification_requests": "--- Żądania weryfikacji ---",
        "no_requests": "Brak oczekujących żądań",
        "support_menu": "--- Wsparcie ---",
        "new_request": "Nowe żądanie",
        "my_requests": "Moje żądania",
        "enter_message": "Wprowadź swoją wiadomość: ",
        "request_created": "Żądanie utworzone (ID: {})",
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
        "friend_added": "{} dodany do znajomych",
        "friend_removed": "{} usunięty ze znajomych",
        "voice_call": "Rozmowa głosowa",
        "call_user": "Zadzwoń do użytkownika",
        "active_calls": "Aktywne połączenia",
        "enter_username_to_call": "Wprowadź nazwę użytkownika: ",
        "calling": "Dzwonię do {}...",
        "incoming_call": "Przychodzące połączenie od {}",
        "call_options": "1. Przyjmij\n2. Odrzuć\n3. Zobacz profil",
        "call_connected": "Połączenie z {} ustanowione",
        "call_ended": "Połączenie zakończone",
        "end_call": "Zakończ połączenie",
        "bio": "Biogram",
        "enter_bio": "Wprowadź swój biogram: ",
        "bio_updated": "Biogram zaktualizowany",
        "permanent_code": "Kod stały: {}",
        "forced_code": "Kod wymuszony: {}",
        "chat_name": "Nazwa czatu: ",
        "chat_participants": "Uczestnicy: ",
        "chat_owner": "Właściciel: {}",
        "chat_settings": "Ustawienia czatu",
        "add_participant": "Dodaj uczestnika",
        "remove_participant": "Usuń uczestnika",
        "leave_chat": "Opuść czat",
        "block_user": "Zablokuj użytkownika",
        "unblock_user": "Odblokuj użytkownika",
        "user_blocked": "Użytkownik {} zablokowany",
        "user_unblocked": "Użytkownik {} odblokowany",
        "blocked_users": "Zablokowani użytkownicy",
        "select_audio_device": "Wybierz urządzenie audio:",
        "audio_input": "Urządzenie wejściowe: {}",
        "audio_output": "Urządzenie wyjściowe: {}",
        "audio_settings": "Ustawienia audio"
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
        }
        
        for file_path, default_content in required_files.items():
            if not os.path.exists(file_path):
                if isinstance(default_content, (dict, list)):
                    with open(file_path, 'w') as f:
                        json.dump(default_content, f)
                else:
                    with open(file_path, 'w') as f:
                        f.write(str(default_content))
        
        return True
    except Exception as e:
        print(f"Setup error: {e}")
        return False

class CryptoManager:
    @staticmethod
    def generate_key():
        return get_random_bytes(32)

    @staticmethod
    def encrypt(data, key):
        iv = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        ct = cipher.encrypt(pad(data.encode(), AES.block_size))
        return base64.b64encode(iv + ct).decode()

    @staticmethod
    def decrypt(enc_data, key):
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
        # Генерация кодов
        perm_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=CONFIG["permanent_code_length"]))
        forced_code = ''.join(random.choices(string.digits, k=CONFIG["forced_code_length"]))
        
        user_file = os.path.join(PATHS["users"], f"{username}.json")
        
        user_data = {
            "password": hashlib.sha256(password.encode()).hexdigest(),
            "permanent_code": perm_code,
            "forced_code": forced_code,
            "created": datetime.now().isoformat(),
            "friends": [],
            "blocked": [],
            "friend_requests": [],
            "bio": "",
            "chats": {
                CONFIG["support_chat"]: {"created": datetime.now().isoformat()},
                CONFIG["favorites_chat"]: {"created": datetime.now().isoformat()}
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
    def authenticate(username, password, perm_code=None, forced_code=None):
        user = UserManager.get_user(username)
        if not user:
            return False
        
        # Проверка пароля
        if user["password"] != hashlib.sha256(password.encode()).hexdigest():
            return False
            
        # Проверка кодов
        if perm_code and user.get("permanent_code") != perm_code:
            return False
            
        if forced_code and user.get("forced_code") != forced_code:
            return False
            
        return True

class ChatManager:
    @staticmethod
    def create_chat(owner, chat_name):
        chat_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=CONFIG["chat_code_length"]))
        chat_file = os.path.join(PATHS["chats"], f"{chat_id}.json")
        
        chat_data = {
            "id": chat_id,
            "name": chat_name,
            "owner": owner,
            "participants": [owner],
            "messages": [],
            "created": datetime.now().isoformat()
        }
        
        with open(chat_file, 'w') as f:
            json.dump(chat_data, f)
            
        # Добавляем чат владельцу
        user = UserManager.get_user(owner)
        if user:
            user["chats"][chat_id] = {"name": chat_name, "created": datetime.now().isoformat()}
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
            
        if username in chat["participants"]:
            return True
            
        chat["participants"].append(username)
        
        # Добавляем чат пользователю
        user = UserManager.get_user(username)
        if user:
            user["chats"][chat_id] = {"name": chat["name"], "created": datetime.now().isoformat()}
            UserManager.update_user(username, user)
        
        chat_file = os.path.join(PATHS["chats"], f"{chat_id}.json")
        with open(chat_file, 'w') as f:
            json.dump(chat, f)
            
        return True

class VoiceCallManager:
    def __init__(self):
        self.active_calls = {}
        self.audio_devices = {
            "input": sd.default.device[0],
            "output": sd.default.device[1]
        }
    
    def start_call(self, caller, callee):
        call_id = str(uuid4())[:8]
        self.active_calls[call_id] = {
            "caller": caller,
            "callee": callee,
            "status": "ringing",
            "start_time": datetime.now(),
            "audio": {
                "input": self.audio_devices["input"],
                "output": self.audio_devices["output"]
            }
        }
        return call_id
    
    def accept_call(self, call_id):
        if call_id in self.active_calls:
            self.active_calls[call_id]["status"] = "active"
            return True
        return False
    
    def end_call(self, call_id):
        if call_id in self.active_calls:
            del self.active_calls[call_id]
            return True
        return False
    
    def set_audio_device(self, device_type, device_id):
        if device_type in ["input", "output"]:
            self.audio_devices[device_type] = device_id
            return True
        return False
    
    def list_audio_devices(self):
        devices = sd.query_devices()
        return [
            {"id": i, "name": d["name"], "max_input": d["max_input_channels"], "max_output": d["max_output_channels"]}
            for i, d in enumerate(devices)
        ]
    
    def record_audio(self, duration=5, sample_rate=44100):
        print("Recording...")
        recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, device=self.audio_devices["input"])
        sd.wait()
        return recording, sample_rate
    
    def play_audio(self, audio_data, sample_rate):
        print("Playing...")
        sd.play(audio_data, samplerate=sample_rate, device=self.audio_devices["output"])
        sd.wait()
    
    def save_audio(self, audio_data, sample_rate, filename):
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes((audio_data * 32767).astype(np.int16))
    
    def load_audio(self, filename):
        with wave.open(filename, 'rb') as wf:
            sample_rate = wf.getframerate()
            frames = wf.readframes(wf.getnframes())
            audio_data = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32767
        return audio_data, sample_rate

class SessionManager:
    @staticmethod
    def save_session(username, token):
        session_file = os.path.join(PATHS["sessions"], f"{username}.session")
        with open(session_file, 'w') as f:
            json.dump({
                "username": username,
                "token": token,
                "expires": (datetime.now() + timedelta(days=30)).isoformat()
            }, f)
    
    @staticmethod
    def get_session():
        session_files = glob.glob(os.path.join(PATHS["sessions"], "*.session"))
        if not session_files:
            return None
            
        # Берем последнюю сессию
        latest_file = max(session_files, key=os.path.getmtime)
        with open(latest_file, 'r') as f:
            session = json.load(f)
            
        # Проверяем срок действия
        if datetime.fromisoformat(session["expires"]) < datetime.now():
            os.remove(latest_file)
            return None
            
        return session
    
    @staticmethod
    def clear_sessions(username=None):
        if username:
            session_file = os.path.join(PATHS["sessions"], f"{username}.session")
            if os.path.exists(session_file):
                os.remove(session_file)
        else:
            for file in glob.glob(os.path.join(PATHS["sessions"], "*.session")):
                os.remove(file)

class WarsawXApp:
    def __init__(self):
        if not setup_directories():
            print("Failed to initialize file system")
            sys.exit(1)
            
        self.current_user = None
        self.voice_manager = VoiceCallManager()
        self.load_language()
        self.ensure_admin()
        
        # Проверка сохраненной сессии
        session = SessionManager.get_session()
        if session:
            self.current_user = session["username"]
            print(f"Welcome back, {self.current_user}!")
        
        self.run()

    def t(self, key, *args):
        lang = "en"
        if hasattr(self, 'language'):
            lang = self.language
        if lang in MESSAGES and key in MESSAGES[lang]:
            return MESSAGES[lang][key].format(*args)
        return key

    def load_language(self):
        if os.path.exists(PATHS["language"]):
            with open(PATHS["language"], 'r') as f:
                lang = f.read().strip()
                if lang in CONFIG["languages"]:
                    self.language = lang
                    return
        self.select_language()

    def select_language(self):
        print("Please select your language:")
        for i, (code, name) in enumerate(CONFIG["languages"].items(), 1):
            print(f"{i}. {name}")
        
        while True:
            try:
                choice = int(input("Enter choice: "))
                if 1 <= choice <= len(CONFIG["languages"]):
                    lang_code = list(CONFIG["languages"].keys())[choice-1]
                    with open(PATHS["language"], 'w') as f:
                        f.write(lang_code)
                    self.language = lang_code
                    return
            except:
                print("Invalid choice")

    def ensure_admin(self):
        if not UserManager.is_username_taken(CONFIG["admin_username"]):
            print(f"Creating admin account: {CONFIG['admin_username']}")
            password = getpass("Set admin password: ")
            perm_code, forced_code = UserManager.create_user(CONFIG["admin_username"], password)
            print(f"Permanent code: {perm_code}")
            print(f"Forced code: {forced_code} (SAVE THIS!)")

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

    def auth_menu(self):
        self.clear_screen()
        print(f"\n{self.t('welcome')}")
        print(f"1. {self.t('login')}")
        print(f"2. {self.t('register')}")
        print(f"3. {self.t('exit')}")
        
        choice = input(self.t("select_option"))
        
        if choice == "1":
            self.login()
        elif choice == "2":
            self.register()
        elif choice == "3":
            sys.exit()
        else:
            print(self.t('invalid_choice'))
            time.sleep(1)

    def login(self):
        self.clear_screen()
        print(f"\n{self.t('login_title')}")
        username = input("Username: ").strip()
        password = getpass(self.t("enter_password"))
        perm_code = input(self.t("enter_permanent_code")).strip()
        
        if UserManager.authenticate(username, password, perm_code):
            self.current_user = username
            print(self.t('welcome_user', username))
            
            # Сохраняем сессию
            token = hashlib.sha256(os.urandom(32)).hexdigest()
            SessionManager.save_session(username, token)
            
            time.sleep(1)
        else:
            print(self.t('auth_failed'))
            forced_code = input(self.t("enter_forced_code")).strip()
            if UserManager.authenticate(username, None, None, forced_code):
                self.current_user = username
                print(self.t('welcome_user', username))
                
                # Сохраняем сессию
                token = hashlib.sha256(os.urandom(32)).hexdigest()
                SessionManager.save_session(username, token)
                
                time.sleep(1)
            else:
                print(self.t('login_failed'))
                time.sleep(1)

    def register(self):
        self.clear_screen()
        print(f"\n{self.t('registration')}")
        while True:
            username = input(self.t("enter_nickname")).strip()
            if not UserManager.validate_username(username):
                print(self.t('invalid_nickname'))
                continue
                
            if UserManager.is_username_taken(username):
                print(self.t('nickname_taken'))
            else:
                break
        
        password = getpass(self.t("set_password"))
        perm_code, forced_code = UserManager.create_user(username, password)
        
        print(self.t('reg_success'))
        print(self.t('permanent_code', perm_code))
        print(self.t('forced_code', forced_code))
        input(self.t("press_enter"))
        
        # Автоматический вход
        self.current_user = username
        token = hashlib.sha256(os.urandom(32)).hexdigest()
        SessionManager.save_session(username, token)

    def main_menu(self):
        while True:
            self.clear_screen()
            print(f"\n{self.t('main_menu')}")
            print(f"1. {self.t('create_chat')}")
            print(f"2. {self.t('join_chat')}")
            print(f"3. {self.t('friends')}")
            print(f"4. {self.t('support')}")
            print(f"5. {self.t('profile_settings')}")
            print(f"6. {self.t('voice_call')}")
            print(f"0. {self.t('logout')}")
            
            choice = input(self.t("select_option"))
            
            if choice == "1":
                self.create_chat()
            elif choice == "2":
                self.join_chat()
            elif choice == "3":
                self.friends_menu()
            elif choice == "4":
                self.support_menu()
            elif choice == "5":
                self.profile_menu()
            elif choice == "6":
                self.voice_call_menu()
            elif choice == "0":
                SessionManager.clear_sessions(self.current_user)
                self.current_user = None
                return
            else:
                print(self.t('invalid_choice'))
                time.sleep(1)

    def create_chat(self):
        chat_name = input(self.t("chat_name")).strip()
        if not chat_name:
            chat_name = f"Chat-{datetime.now().strftime('%Y%m%d')}"
        
        chat_id = ChatManager.create_chat(self.current_user, chat_name)
        print(self.t('chat_created', chat_id))
        input(self.t("press_enter"))

    def join_chat(self):
        chat_id = input(self.t("enter_chat_code")).strip().upper()
        chat = ChatManager.get_chat(chat_id)
        
        if not chat:
            print(self.t('chat_not_found'))
            time.sleep(1)
            return
        
        # Добавляем пользователя в чат
        if ChatManager.add_participant(chat_id, self.current_user):
            print(f"Joined chat: {chat['name']}")
        else:
            print("Failed to join chat")
            time.sleep(1)
            return
            
        print(f"\n{self.t('chat_history')}")
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

    def friends_menu(self):
        while True:
            self.clear_screen()
            print(f"\n{self.t('friends_menu')}")
            print(f"1. {self.t('add_friend')}")
            print(f"2. {self.t('friend_requests')}")
            print(f"3. {self.t('my_friends')}")
            print(f"4. {self.t('blocked_users')}")
            print(f"0. {self.t('back')}")
            
            choice = input(self.t("select_option"))
            
            if choice == "1":
                self.add_friend()
            elif choice == "2":
                self.friend_requests()
            elif choice == "3":
                self.my_friends()
            elif choice == "4":
                self.blocked_users()
            elif choice == "0":
                return
            else:
                print(self.t('invalid_choice'))
                time.sleep(1)

    def add_friend(self):
        friend = input(self.t("enter_friend_username")).strip()
        if not UserManager.get_user(friend):
            print(f"User {friend} not found")
            time.sleep(1)
            return
            
        user = UserManager.get_user(self.current_user)
        if friend in user["friends"]:
            print(f"{friend} is already your friend")
            time.sleep(1)
            return
            
        friend_user = UserManager.get_user(friend)
        if self.current_user in friend_user.get("friend_requests", []):
            print(f"Request already sent to {friend}")
            time.sleep(1)
            return
            
        friend_user["friend_requests"].append(self.current_user)
        UserManager.update_user(friend, friend_user)
        print(self.t('friend_request_sent', friend))
        time.sleep(1)

    def friend_requests(self):
        user = UserManager.get_user(self.current_user)
        requests = user.get("friend_requests", [])
        
        if not requests:
            print(self.t('no_friend_requests'))
            time.sleep(1)
            return
            
        self.clear_screen()
        print(f"\n{self.t('incoming_requests')}")
        for i, friend in enumerate(requests, 1):
            print(f"{i}. {friend}")
            print(f"  1. {self.t('accept')}")
            print(f"  2. {self.t('reject')}")
            print(f"  3. {self.t('view_profile')}")
            
            action = input(self.t("select_option"))
            if action == "1":
                # Принять запрос
                if friend not in user["friends"]:
                    user["friends"].append(friend)
                if self.current_user not in UserManager.get_user(friend)["friends"]:
                    friend_user = UserManager.get_user(friend)
                    friend_user["friends"].append(self.current_user)
                    UserManager.update_user(friend, friend_user)
                
                user["friend_requests"].remove(friend)
                UserManager.update_user(self.current_user, user)
                print(self.t('friend_added', friend))
                
            elif action == "2":
                # Отклонить запрос
                user["friend_requests"].remove(friend)
                UserManager.update_user(self.current_user, user)
                print(self.t('friend_removed', friend))
                
            elif action == "3":
                # Просмотр профиля
                self.view_profile(friend)
                
            time.sleep(1)

    def my_friends(self):
        user = UserManager.get_user(self.current_user)
        friends = user.get("friends", [])
        
        if not friends:
            print(self.t('no_friend_requests'))
            time.sleep(1)
            return
            
        self.clear_screen()
        print(f"\n{self.t('my_friends')}")
        for i, friend in enumerate(friends, 1):
            print(f"{i}. {friend}")
        
        print("\nSelect friend to view profile or 0 to back")
        choice = input(self.t("select_option"))
        if choice.isdigit():
            index = int(choice)
            if 1 <= index <= len(friends):
                self.view_profile(friends[index-1])
            elif index == 0:
                return

    def blocked_users(self):
        user = UserManager.get_user(self.current_user)
        blocked = user.get("blocked", [])
        
        if not blocked:
            print("No blocked users")
            time.sleep(1)
            return
            
        self.clear_screen()
        print(f"\n{self.t('blocked_users')}")
        for i, username in enumerate(blocked, 1):
            print(f"{i}. {username}")
            print(f"  1. {self.t('unblock_user')}")
            print(f"  2. {self.t('view_profile')}")
            
            action = input(self.t("select_option"))
            if action == "1":
                # Разблокировать
                if username in user["blocked"]:
                    user["blocked"].remove(username)
                    UserManager.update_user(self.current_user, user)
                    print(self.t('user_unblocked', username))
            elif action == "2":
                # Просмотр профиля
                self.view_profile(username)
                
            time.sleep(1)

    def view_profile(self, username):
        user = UserManager.get_user(username)
        if not user:
            print("User not found")
            time.sleep(1)
            return
            
        self.clear_screen()
        print(f"\nProfile: {username}")
        print(f"Registered: {user['created'][:10]}")
        print(f"Bio: {user.get('bio', 'No bio')}")
        print(f"Friends: {len(user.get('friends', []))}")
        
        current_user_data = UserManager.get_user(self.current_user)
        is_blocked = username in current_user_data.get("blocked", [])
        
        if self.current_user == username:
            # Собственный профиль
            print("\n1. Edit bio")
            print("0. Back")
            
            choice = input(self.t("select_option"))
            if choice == "1":
                new_bio = input(self.t("enter_bio"))
                user["bio"] = new_bio
                UserManager.update_user(username, user)
                print(self.t('bio_updated'))
                time.sleep(1)
        else:
            # Чужой профиль
            print("\n1. Send message")
            if is_blocked:
                print(f"2. {self.t('unblock_user')}")
            else:
                print(f"2. {self.t('block_user')}")
            print("3. Start voice call")
            print("0. Back")
            
            choice = input(self.t("select_option"))
            if choice == "1":
                # Отправить сообщение
                print("Message feature coming soon")
                time.sleep(1)
            elif choice == "2":
                # Блокировка/разблокировка
                if is_blocked:
                    current_user_data["blocked"].remove(username)
                    UserManager.update_user(self.current_user, current_user_data)
                    print(self.t('user_unblocked', username))
                else:
                    if username not in current_user_data["blocked"]:
                        current_user_data["blocked"].append(username)
                        UserManager.update_user(self.current_user, current_user_data)
                        print(self.t('user_blocked', username))
                time.sleep(1)
            elif choice == "3":
                # Голосовой звонок
                self.start_voice_call(username)

    def support_menu(self):
        while True:
            self.clear_screen()
            print(f"\n{self.t('support_menu')}")
            print(f"1. {self.t('new_request')}")
            print(f"2. {self.t('my_requests')}")
            print(f"0. {self.t('back')}")
            
            choice = input(self.t("select_option"))
            
            if choice == "1":
                self.create_support_ticket()
            elif choice == "2":
                self.view_my_tickets()
            elif choice == "0":
                return
            else:
                print(self.t('invalid_choice'))
                time.sleep(1)

    def create_support_ticket(self):
        message = input(self.t("enter_message"))
        # В реальной реализации здесь будет создание тикета
        print(self.t('request_created', "T123456"))
        time.sleep(1)

    def view_my_tickets(self):
        print("Support tickets coming soon")
        time.sleep(1)

    def voice_call_menu(self):
        while True:
            self.clear_screen()
            print(f"\n{self.t('voice_call')}")
            print(f"1. {self.t('call_user')}")
            print(f"2. {self.t('audio_settings')}")
            print(f"0. {self.t('back')}")
            
            choice = input(self.t("select_option"))
            
            if choice == "1":
                self.start_voice_call()
            elif choice == "2":
                self.audio_settings()
            elif choice == "0":
                return
            else:
                print(self.t('invalid_choice'))
                time.sleep(1)

    def start_voice_call(self, username=None):
        if not username:
            username = input(self.t("enter_username_to_call")).strip()
        
        if not UserManager.get_user(username):
            print("User not found")
            time.sleep(1)
            return
            
        print(self.t('calling', username))
        
        # Симуляция звонка - в реальной реализации будет установка соединения
        for i in range(5):
            print(f"Ringing... {i+1}")
            time.sleep(1)
        
        # Принятие звонка
        print(self.t('call_connected', username))
        print("Voice call started. Press Enter to end call.")
        
        # Запись и воспроизведение аудио
        try:
            # Запись 5 секунд аудио
            audio, sample_rate = self.voice_manager.record_audio(duration=5)
            
            # Сохраняем во временный файл
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
                self.voice_manager.save_audio(audio, sample_rate, tmpfile.name)
                print("Audio saved for transmission")
            
            # Воспроизводим записанное аудио
            self.voice_manager.play_audio(audio, sample_rate)
        except Exception as e:
            print(f"Audio error: {e}")
        
        input()
        print(self.t('call_ended'))
        time.sleep(1)

    def audio_settings(self):
        devices = self.voice_manager.list_audio_devices()
        
        self.clear_screen()
        print(f"\n{self.t('select_audio_device')}")
        
        # Входные устройства
        print("\nInput devices:")
        for device in devices:
            if device["max_input"] > 0:
                print(f"{device['id']}. {device['name']}")
        
        choice = input("Select input device ID: ")
        if choice.isdigit():
            device_id = int(choice)
            if any(d["id"] == device_id and d["max_input"] > 0 for d in devices):
                self.voice_manager.set_audio_device("input", device_id)
                print(self.t('audio_input', devices[device_id]["name"]))
        
        # Выходные устройства
        print("\nOutput devices:")
        for device in devices:
            if device["max_output"] > 0:
                print(f"{device['id']}. {device['name']}")
        
        choice = input("Select output device ID: ")
        if choice.isdigit():
            device_id = int(choice)
            if any(d["id"] == device_id and d["max_output"] > 0 for d in devices):
                self.voice_manager.set_audio_device("output", device_id)
                print(self.t('audio_output', devices[device_id]["name"]))
        
        time.sleep(1)

    def profile_menu(self):
        self.view_profile(self.current_user)

    def admin_menu(self):
        print("Admin panel coming soon")
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
