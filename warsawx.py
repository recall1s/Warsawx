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
import socket
import urllib.parse

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
    "webrtc_server": "https://warsawx-webrtc-server.onrender.com"  # Пример сервера WebRTC
}

# Пути к файлам
PATHS = {
    "users": os.path.join(BASE_DIR, "Users"),
    "nicknames": os.path.join(BASE_DIR, "nicknames.txt"),
    "language": os.path.join(BASE_DIR, "language.txt"),
    "lockouts": os.path.join(BASE_DIR, "lockouts.json"),
    "sessions": os.path.join(BASE_DIR, "sessions.json"),
    "support": os.path.join(BASE_DIR, "support_chats"),
    "chats": os.path.join(BASE_DIR, "chats"),
    "master_key": os.path.join(BASE_DIR, "master.key"),
    "integrity": os.path.join(BASE_DIR, "integrity.sig")
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
        "enter_nickname": "Enter username (3-17 chars): ",
        "invalid_nickname": "Invalid username. Only A-Z, a-z, 0-9, -_ allowed",
        "admin_nickname": "Special characters allowed only for admin",
        "nickname_taken": "Username already taken",
        "set_password": "Set password: ",
        "perm_code": "Your permanent code (save this!): ",
        "forced_code": "Your forced code (save this!): ",
        "reg_success": "Registration successful!",
        "press_enter": "Press Enter to continue...",
        "login_title": "--- Login ---",
        "enter_password": "Password: ",
        "enter_perm_code": "Permanent code: ",
        "enter_forced_code": "Forced code: ",
        "welcome_user": "Welcome, {}!",
        "auth_failed": "Authentication failed",
        "login_failed": "Login failed",
        "main_menu": "--- Main Menu ---",
        "create_chat": "Create chat",
        "join_chat": "Join chat",
        "profile_settings": "Profile settings",
        "friends": "Friends",
        "logout": "Logout",
        "back": "Back",
        "chat_created": "Chat created! Code: {}",
        "enter_chat_code": "Enter chat code: ",
        "chat_not_found": "Chat not found",
        "chat_history": "--- Chat History ---",
        "type_message": "Type message (or /exit to leave): ",
        "message_sent": "Message sent",
        "admin_menu": "--- Admin Panel ---",
        "view_requests": "View support requests",
        "update_app": "Update application",
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
        "bio": "Bio: ",
        "edit_bio": "Edit bio",
        "current_bio": "Current bio: {}",
        "new_bio": "Enter new bio: ",
        "bio_updated": "Bio updated!",
        "chat_name": "Enter chat name: ",
        "chat_participants": "Enter participants (comma separated): ",
        "block_user": "Block user",
        "unblock_user": "Unblock user",
        "blocked_users": "Blocked users",
        "user_blocked": "User {} blocked",
        "user_unblocked": "User {} unblocked",
        "no_blocked_users": "No blocked users",
        "leave_chat": "Leave chat",
        "chat_left": "You left the chat",
        "web_call_link": "Web call link: {}"
    },
    "pl": {
        "welcome": "=== WarsawX ===",
        "select_language": "Wybierz język:",
        "register": "Rejestracja",
        "login": "Zaloguj",
        "exit": "Wyjdź",
        "select_option": "Wybierz opcję: ",
        "invalid_choice": "Nieprawidłowy wybór",
        "registration": "--- Rejestracja ---",
        "enter_nickname": "Wprowadź nazwę użytkownika (3-17 znaków): ",
        "invalid_nickname": "Nieprawidłowa nazwa. Tylko A-Z, a-z, 0-9, -_",
        "admin_nickname": "Znaki specjalne dozwolone tylko dla admina",
        "nickname_taken": "Nazwa użytkownika jest już zajęta",
        "set_password": "Ustaw hasło: ",
        "perm_code": "Twój stały kod (zapisz go!): ",
        "forced_code": "Twój kod awaryjny (zapisz go!): ",
        "reg_success": "Rejestracja zakończona sukcesem!",
        "press_enter": "Naciśnij Enter, aby kontynuować...",
        "login_title": "--- Logowanie ---",
        "enter_password": "Hasło: ",
        "enter_perm_code": "Stały kod: ",
        "enter_forced_code": "Kod awaryjny: ",
        "welcome_user": "Witaj, {}!",
        "auth_failed": "Uwierzytelnienie nie powiodło się",
        "login_failed": "Logowanie nie powiodło się",
        "main_menu": "--- Menu Główne ---",
        "create_chat": "Utwórz czat",
        "join_chat": "Dołącz do czatu",
        "profile_settings": "Ustawienia profilu",
        "friends": "Znajomi",
        "logout": "Wyloguj",
        "back": "Powrót",
        "chat_created": "Czat utworzony! Kod: {}",
        "enter_chat_code": "Wprowadź kod czatu: ",
        "chat_not_found": "Czat nie znaleziony",
        "chat_history": "--- Historia Czatu ---",
        "type_message": "Wpisz wiadomość (lub /exit, aby wyjść): ",
        "message_sent": "Wiadomość wysłana",
        "admin_menu": "--- Panel Administratora ---",
        "view_requests": "Zobacz zgłoszenia",
        "update_app": "Aktualizuj aplikację",
        "support_menu": "--- Wsparcie ---",
        "new_request": "Nowe zgłoszenie",
        "my_requests": "Moje zgłoszenia",
        "enter_message": "Wprowadź swoją wiadomość: ",
        "request_created": "Zgłoszenie utworzone (ID: {})",
        "view_profile": "Zobacz profil",
        "friends_menu": "--- Znajomi ---",
        "add_friend": "Dodaj znajomego",
        "friend_requests": "Prośby o dodanie",
        "my_friends": "Moi znajomi",
        "enter_friend_username": "Wprowadź nazwę znajomego: ",
        "friend_request_sent": "Prośba wysłana do {}",
        "no_friend_requests": "Brak próśb o dodanie",
        "incoming_requests": "Otrzymane prośby",
        "accept": "Zaakceptuj",
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
        "call_connected": "Połączenie z {} nawiązane",
        "call_ended": "Połączenie zakończone",
        "end_call": "Zakończ połączenie",
        "bio": "Bio: ",
        "edit_bio": "Edytuj bio",
        "current_bio": "Aktualne bio: {}",
        "new_bio": "Wprowadź nowe bio: ",
        "bio_updated": "Bio zaktualizowane!",
        "chat_name": "Wprowadź nazwę czatu: ",
        "chat_participants": "Wprowadź uczestników (oddziel przecinkami): ",
        "block_user": "Zablokuj użytkownika",
        "unblock_user": "Odblokuj użytkownika",
        "blocked_users": "Zablokowani użytkownicy",
        "user_blocked": "Użytkownik {} zablokowany",
        "user_unblocked": "Użytkownik {} odblokowany",
        "no_blocked_users": "Brak zablokowanych użytkowników",
        "leave_chat": "Opuść czat",
        "chat_left": "Opuściłeś czat",
        "web_call_link": "Link do rozmowy: {}"
    }
}

def setup_directories():
    try:
        os.makedirs(BASE_DIR, exist_ok=True)
        os.makedirs(PATHS["users"], exist_ok=True)
        os.makedirs(PATHS["support"], exist_ok=True)
        os.makedirs(PATHS["chats"], exist_ok=True)
        
        required_files = {
            PATHS["nicknames"]: "",
            PATHS["language"]: "en",
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
        # Разрешаем апостроф только для администратора
        if username == CONFIG["admin_username"]:
            return True
        
        if len(username) < CONFIG["min_username_len"] or len(username) > CONFIG["max_username_len"]:
            return False
        allowed = string.ascii_letters + string.digits + "_-"
        return all(c in allowed for c in username)

    @staticmethod
    def is_username_taken(username):
        if not os.path.exists(PATHS["nicknames"]) or os.path.getsize(PATHS["nicknames"]) == 0:
            return False
        with open(PATHS["nicknames"], 'r') as f:
            return username in f.read().split()

    @staticmethod
    def create_user(username, password):
        # Генерируем коды
        perm_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
        forced_code = ''.join(random.choices(string.digits, k=12))
        
        user_data = {
            "password": hashlib.sha256(password.encode()).hexdigest(),
            "perm_code": perm_code,
            "forced_code": forced_code,
            "created": datetime.now().isoformat(),
            "bio": "",
            "friends": [],
            "blocked": [],
            "friend_requests": [],
            "chats": {
                CONFIG["support_chat"]: {"created": datetime.now().isoformat()},
                CONFIG["favorites_chat"]: {"created": datetime.now().isoformat()}
            }
        }

        user_file = os.path.join(PATHS["users"], f"{username}.json")
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
        
        if forced_code:
            return user["forced_code"] == forced_code
        
        if perm_code:
            return user["perm_code"] == perm_code and user["password"] == hashlib.sha256(password.encode()).hexdigest()
        
        return user["password"] == hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def save_session(username):
        sessions = {}
        if os.path.exists(PATHS["sessions"]) and os.path.getsize(PATHS["sessions"]) > 0:
            with open(PATHS["sessions"], 'r') as f:
                sessions = json.load(f)
        
        sessions[username] = datetime.now().isoformat()
        
        with open(PATHS["sessions"], 'w') as f:
            json.dump(sessions, f)
    
    @staticmethod
    def get_sessions():
        if os.path.exists(PATHS["sessions"]) and os.path.getsize(PATHS["sessions"]) > 0:
            with open(PATHS["sessions"], 'r') as f:
                return json.load(f)
        return {}

class ChatManager:
    @staticmethod
    def create_chat(owner, name, participants):
        chat_id = str(uuid4())[:8]
        chat_file = os.path.join(PATHS["chats"], f"{chat_id}.json")
        
        chat_data = {
            "id": chat_id,
            "name": name,
            "owner": owner,
            "participants": participants,
            "messages": [],
            "created": datetime.now().isoformat(),
            "blocked": []
        }
        
        with open(chat_file, 'w') as f:
            json.dump(chat_data, f)
            
        # Добавляем чат каждому участнику
        for participant in participants:
            user = UserManager.get_user(participant)
            if user:
                user["chats"][chat_id] = {"name": name, "created": datetime.now().isoformat()}
                UserManager.update_user(participant, user)
        
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
            
        # Проверка блокировки
        if sender in chat.get("blocked", []):
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
    def block_user(chat_id, user_to_block, owner):
        chat = ChatManager.get_chat(chat_id)
        if not chat or chat["owner"] != owner:
            return False
            
        if user_to_block not in chat["blocked"]:
            chat["blocked"].append(user_to_block)
            
        with open(os.path.join(PATHS["chats"], f"{chat_id}.json"), 'w') as f:
            json.dump(chat, f)
            
        return True

    @staticmethod
    def unblock_user(chat_id, user_to_unblock, owner):
        chat = ChatManager.get_chat(chat_id)
        if not chat or chat["owner"] != owner:
            return False
            
        if user_to_unblock in chat["blocked"]:
            chat["blocked"].remove(user_to_unblock)
            
        with open(os.path.join(PATHS["chats"], f"{chat_id}.json"), 'w') as f:
            json.dump(chat, f)
            
        return True

    @staticmethod
    def leave_chat(chat_id, username):
        chat = ChatManager.get_chat(chat_id)
        if not chat or username not in chat["participants"]:
            return False
            
        chat["participants"].remove(username)
        
        # Обновляем данные чата
        with open(os.path.join(PATHS["chats"], f"{chat_id}.json"), 'w') as f:
            json.dump(chat, f)
            
        # Удаляем чат у пользователя
        user = UserManager.get_user(username)
        if user and chat_id in user["chats"]:
            del user["chats"][chat_id]
            UserManager.update_user(username, user)
            
        return True

class WebRTCManager:
    @staticmethod
    def create_call(caller, callee):
        try:
            # Создаем уникальный идентификатор для звонка
            call_id = str(uuid4())
            
            # Формируем ссылку для WebRTC звонка
            call_link = f"{CONFIG['webrtc_server']}/call?caller={urllib.parse.quote(caller)}&callee={urllib.parse.quote(callee)}&id={call_id}"
            
            return call_link
        except Exception as e:
            print(f"WebRTC error: {e}")
            return None

class WarsawXApp:
    def __init__(self):
        if not setup_directories():
            print("Failed to initialize file system")
            sys.exit(1)
            
        self.current_user = None
        self.language = "en"
        self.load_language()
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
        languages = list(CONFIG["languages"].items())
        
        for i, (code, name) in enumerate(languages, 1):
            print(f"{i}. {name}")
        
        while True:
            try:
                choice = int(input(self.t("select_option")))
                if 1 <= choice <= len(languages):
                    lang_code = languages[choice-1][0]
                    with open(PATHS["language"], 'w') as f:
                        f.write(lang_code)
                    self.language = lang_code
                    return
            except:
                print(self.t("invalid_choice"))

    def clear_screen(self):
        if platform.system() == "Windows":
            os.system('cls')
        else:
            os.system('clear')

    def run(self):
        # Проверка сохраненных сессий
        sessions = UserManager.get_sessions()
        if sessions:
            print(f"{self.t('welcome')}")
            print("Saved sessions:")
            usernames = list(sessions.keys())
            for i, username in enumerate(usernames, 1):
                print(f"{i}. {username}")
            
            print("0. New login")
            
            choice = input(self.t("select_option"))
            if choice.isdigit():
                index = int(choice)
                if 1 <= index <= len(usernames):
                    self.current_user = usernames[index-1]
                    print(self.t('welcome_user', self.current_user))
                    time.sleep(1)
                    self.main_menu()
                    return
                elif index == 0:
                    self.auth_menu()
                    return
        
        self.auth_menu()

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
            self.auth_menu()

    def login(self):
        self.clear_screen()
        print(f"\n{self.t('login_title')}")
        username = input("Username: ").strip()
        
        print("1. Login with password and permanent code")
        print("2. Login with forced code")
        choice = input(self.t("select_option"))
        
        if choice == "1":
            password = getpass(self.t("enter_password"))
            perm_code = input(self.t("enter_perm_code")).strip()
            
            if UserManager.authenticate(username, password, perm_code=perm_code):
                self.current_user = username
                UserManager.save_session(username)
                print(self.t('welcome_user', username))
                time.sleep(1)
                self.main_menu()
            else:
                print(self.t('auth_failed'))
                time.sleep(1)
                self.login()
        
        elif choice == "2":
            forced_code = input(self.t("enter_forced_code")).strip()
            
            if UserManager.authenticate(username, forced_code=forced_code):
                self.current_user = username
                UserManager.save_session(username)
                print(self.t('welcome_user', username))
                time.sleep(1)
                self.main_menu()
            else:
                print(self.t('auth_failed'))
                time.sleep(1)
                self.login()
        
        else:
            print(self.t('invalid_choice'))
            time.sleep(1)
            self.login()

    def register(self):
        self.clear_screen()
        print(f"\n{self.t('registration')}")
        while True:
            username = input(self.t("enter_nickname")).strip()
            
            if username == CONFIG["admin_username"]:
                break
                
            if not UserManager.validate_username(username):
                print(self.t('invalid_nickname'))
                continue
                
            if UserManager.is_username_taken(username):
                print(self.t('nickname_taken'))
            else:
                break
        
        password = getpass(self.t("set_password"))
        perm_code, forced_code = UserManager.create_user(username, password)
        
        print(f"\n{self.t('reg_success')}")
        print(f"{self.t('perm_code')}: {perm_code}")
        print(f"{self.t('forced_code')}: {forced_code}")
        
        self.current_user = username
        UserManager.save_session(username)
        
        input(self.t("press_enter"))
        self.main_menu()

    # Остальные методы (main_menu, create_chat, join_chat, friends_menu и т.д.) 
    # остаются аналогичными предыдущей версии, но с использованием self.t() для переводов

    def profile_menu(self):
        user = UserManager.get_user(self.current_user)
        if not user:
            print("User data not found")
            time.sleep(1)
            return
            
        while True:
            self.clear_screen()
            print(f"\n{self.t('profile_settings')}")
            print(f"1. {self.t('view_profile')}")
            print(f"2. {self.t('edit_bio')}")
            print(f"3. {self.t('blocked_users')}")
            print(f"0. {self.t('back')}")
            
            choice = input(self.t("select_option"))
            
            if choice == "1":
                self.view_profile(self.current_user)
            elif choice == "2":
                self.edit_bio()
            elif choice == "3":
                self.blocked_users_menu()
            elif choice == "0":
                return
            else:
                print(self.t('invalid_choice'))
                time.sleep(1)

    def edit_bio(self):
        user = UserManager.get_user(self.current_user)
        if not user:
            print("User data not found")
            time.sleep(1)
            return
            
        self.clear_screen()
        print(f"\n{self.t('current_bio', user.get('bio', ''))}")
        new_bio = input(self.t("new_bio"))
        
        user["bio"] = new_bio
        UserManager.update_user(self.current_user, user)
        
        print(self.t('bio_updated'))
        time.sleep(1)

    def blocked_users_menu(self):
        user = UserManager.get_user(self.current_user)
        if not user:
            print("User data not found")
            time.sleep(1)
            return
            
        blocked = user.get("blocked", [])
        
        if not blocked:
            print(self.t('no_blocked_users'))
            time.sleep(1)
            return
            
        self.clear_screen()
        print(f"\n{self.t('blocked_users')}")
        for i, username in enumerate(blocked, 1):
            print(f"{i}. {username}")
        
        print("\n1. Unblock user")
        print("0. Back")
        
        choice = input(self.t("select_option"))
        if choice == "1":
            unblock_index = input("Select user to unblock: ")
            if unblock_index.isdigit():
                index = int(unblock_index)
                if 1 <= index <= len(blocked):
                    user["blocked"].remove(blocked[index-1])
                    UserManager.update_user(self.current_user, user)
                    print(self.t('user_unblocked', blocked[index-1]))
                    time.sleep(1)
        elif choice == "0":
            return

    def start_voice_call(self):
        callee = input(self.t("enter_username_to_call")).strip()
        if not UserManager.get_user(callee):
            print("User not found")
            time.sleep(1)
            return
            
        # Создаем WebRTC звонок
        call_link = WebRTCManager.create_call(self.current_user, callee)
        
        if call_link:
            print(self.t('calling', callee))
            print(self.t('web_call_link', call_link))
            webbrowser.open(call_link)
            input(self.t("press_enter"))
        else:
            print("Failed to create call")
            time.sleep(1)

def create_launcher_script():
    if platform.system() == "Linux":
        script_path = os.path.expanduser("~/warsawx.sh")
        with open(script_path, 'w') as f:
            f.write("""#!/bin/bash
cd "$(dirname "$0")"
python3 warsawx.py
""")
        os.chmod(script_path, 0o755)
        return script_path
    return None

if __name__ == "__main__":
    # Для Linux используем другую базовую директорию
    if platform.system() == "Linux":
        BASE_DIR = os.path.join(os.path.expanduser('~/.config'), APP_NAME)
        PATHS = {key: os.path.join(BASE_DIR, path) for key, path in PATHS.items()}
    
    # Создаем скрипт запуска
    launcher = create_launcher_script()
    
    # Запуск приложения
    app = WarsawXApp()
