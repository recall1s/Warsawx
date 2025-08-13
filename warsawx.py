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
        "enter_nickname": "Enter username (3-17 chars, only A-Z, a-z, 0-9, -_): ",
        "invalid_nickname": "Invalid username. Use only letters, digits, - and _",
        "nickname_taken": "Username already taken",
        "set_password": "Set password: ",
        "reg_success": "Registration successful!",
        "press_enter": "Press Enter to continue...",
        "login_title": "--- Login ---",
        "enter_password": "Password: ",
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
        "end_call": "End call"
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
        "invalid_nickname": "Nieprawidłowa nazwa użytkownika. Używaj tylko liter, cyfr, - i _",
        "nickname_taken": "Nazwa użytkownika jest już zajęta",
        "set_password": "Ustaw hasło: ",
        "reg_success": "Rejestracja udana!",
        "press_enter": "Naciśnij Enter, aby kontynuować...",
        "login_title": "--- Logowanie ---",
        "enter_password": "Hasło: ",
        "welcome_user": "Witaj, {}!",
        "auth_failed": "Błąd uwierzytelniania",
        "login_failed": "Błąd logowania",
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
        "type_message": "Wpisz wiadomość (lub /exit aby wyjść): ",
        "message_sent": "Wiadomość wysłana",
        "admin_menu": "--- Panel administratora ---",
        "view_requests": "Zobacz prośby o wsparcie",
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
        "friend_requests": "Prośby o dodanie",
        "my_friends": "Moi znajomi",
        "enter_friend_username": "Wprowadź nazwę znajomego: ",
        "friend_request_sent": "Prośba o dodanie wysłana do {}",
        "no_friend_requests": "Brak próśb o dodanie",
        "incoming_requests": "Przychodzące prośby o dodanie",
        "accept": "Zaakceptuj",
        "reject": "Odrzuć",
        "friend_added": "{} dodany do znajomych",
        "friend_removed": "{} usunięty ze znajomych",
        "voice_call": "Rozmowa głosowa",
        "call_user": "Zadzwoń do użytkownika",
        "active_calls": "Aktywne rozmowy",
        "enter_username_to_call": "Wprowadź nazwę użytkownika: ",
        "calling": "Dzwonienie do {}...",
        "incoming_call": "Przychodzące połączenie od {}",
        "call_options": "1. Przyjmij\n2. Odrzuć\n3. Zobacz profil",
        "call_connected": "Połączenie z {} nawiązane",
        "call_ended": "Rozmowa zakończona",
        "end_call": "Zakończ rozmowę"
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
            
        # Специальное разрешение для администратора
        if username == "Recall's":
            return True
            
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
        user_file = os.path.join(PATHS["users"], f"{username}.json")
        
        user_data = {
            "password": hashlib.sha256(password.encode()).hexdigest(),
            "created": datetime.now().isoformat(),
            "friends": [],
            "blocked": [],
            "friend_requests": [],
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
        return user["password"] == hashlib.sha256(password.encode()).hexdigest()

class ChatManager:
    @staticmethod
    def create_chat(owner, participants):
        chat_id = str(uuid4())[:8]
        chat_file = os.path.join(PATHS["chats"], f"{chat_id}.json")
        
        chat_data = {
            "id": chat_id,
            "owner": owner,
            "participants": participants,
            "messages": [],
            "created": datetime.now().isoformat()
        }
        
        with open(chat_file, 'w') as f:
            json.dump(chat_data, f)
            
        # Добавляем чат каждому участнику
        for participant in participants:
            user = UserManager.get_user(participant)
            if user:
                user["chats"][chat_id] = {"created": datetime.now().isoformat()}
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
            
        chat["messages"].append({
            "sender": sender,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
        chat_file = os.path.join(PATHS["chats"], f"{chat_id}.json")
        with open(chat_file, 'w') as f:
            json.dump(chat, f)
            
        return True

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

class VoiceCallManager:
    active_calls = {}
    
    @staticmethod
    def start_call(caller, callee):
        call_id = str(uuid4())[:8]
        VoiceCallManager.active_calls[call_id] = {
            "caller": caller,
            "callee": callee,
            "status": "ringing",
            "start_time": datetime.now()
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
            del VoiceCallManager.active_calls[call_id]
            return True
        return False

class WarsawXApp:
    def __init__(self):
        if not setup_directories():
            print("Failed to initialize file system")
            sys.exit(1)
            
        self.current_user = None
        self.language = "en"
        self.load_language()
        self.ensure_admin()
        self.run()

    def t(self, key, *args):
        if self.language in MESSAGES and key in MESSAGES[self.language]:
            return MESSAGES[self.language][key].format(*args)
        return key

    def load_language(self):
        # Принудительно предлагаем выбор языка при первом запуске
        if not os.path.exists(PATHS["language"]):
            self.select_language()
            return
            
        if os.path.exists(PATHS["language"]):
            with open(PATHS["language"], 'r') as f:
                lang = f.read().strip()
                if lang in CONFIG["languages"]:
                    self.language = lang

    def select_language(self):
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
            # Генерируем случайный пароль для администратора
            password = hashlib.sha256(os.urandom(16)).hexdigest()[:12]
            UserManager.create_user(CONFIG["admin_username"], password)
            print(f"Admin account created! Username: {CONFIG['admin_username']}, Password: {password}")

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
        
        if UserManager.authenticate(username, password):
            self.current_user = username
            print(self.t('welcome_user', username))
            time.sleep(1)
        else:
            print(self.t('auth_failed'))
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
        UserManager.create_user(username, password)
        print(self.t('reg_success'))
        input(self.t("press_enter"))

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
                self.current_user = None
                return
            else:
                print(self.t('invalid_choice'))
                time.sleep(1)

    def create_chat(self):
        participants = [self.current_user]
        print(self.t("enter_friend_username"))
        while True:
            friend = input("> ").strip()
            if friend == "":
                break
            if UserManager.get_user(friend):
                participants.append(friend)
                print(f"{friend} added to chat")
            else:
                print(f"User {friend} not found")
        
        if len(participants) > 1:
            chat_id = ChatManager.create_chat(self.current_user, participants)
            print(self.t('chat_created', chat_id))
        else:
            print("Chat must have at least 2 participants")
        
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
            print(f"0. {self.t('back')}")
            
            choice = input(self.t("select_option"))
            
            if choice == "1":
                self.add_friend()
            elif choice == "2":
                self.friend_requests()
            elif choice == "3":
                self.my_friends()
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

    def view_profile(self, username):
        user = UserManager.get_user(username)
        if not user:
            print("User not found")
            time.sleep(1)
            return
            
        self.clear_screen()
        print(f"\n{self.t('view_profile')}: {username}")
        print(f"Registered: {user['created'][:10]}")
        print(f"Friends: {len(user.get('friends', []))}")
        
        if self.current_user == CONFIG["admin_username"]:
            print("\nAdmin options:")
            print("1. Send message")
            print("2. Block user")
            print("0. Back")
            
            choice = input(self.t("select_option"))
            if choice == "1":
                message = input("Message: ")
                # В реальной реализации здесь будет отправка сообщения
                print("Message sent")
                time.sleep(1)
            elif choice == "2":
                # Блокировка пользователя
                print("User blocked")
                time.sleep(1)
        else:
            input(self.t("press_enter"))

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
        ticket_id = SupportSystem.create_ticket(self.current_user, message)
        print(self.t('request_created', ticket_id))
        time.sleep(1)

    def view_my_tickets(self):
        tickets = SupportSystem.get_tickets()
        user_tickets = [t for t in tickets if t["user"] == self.current_user]
        
        if not user_tickets:
            print(self.t('no_requests'))
            time.sleep(1)
            return
            
        self.clear_screen()
        for ticket in user_tickets:
            print(f"\nID: {ticket['id']}")
            print(f"Status: {ticket['status']}")
            print(f"Message: {ticket['message']}")
            
            for resp in ticket["responses"]:
                print(f"\nResponse from {resp['from']}:")
                print(resp["message"])
        
        input(self.t("press_enter"))

    def voice_call_menu(self):
        while True:
            self.clear_screen()
            print(f"\n{self.t('voice_call')}")
            print(f"1. {self.t('call_user')}")
            print(f"2. {self.t('active_calls')}")
            print(f"0. {self.t('back')}")
            
            choice = input(self.t("select_option"))
            
            if choice == "1":
                self.start_voice_call()
            elif choice == "2":
                self.active_calls()
            elif choice == "0":
                return
            else:
                print(self.t('invalid_choice'))
                time.sleep(1)

    def start_voice_call(self):
        callee = input(self.t("enter_username_to_call")).strip()
        if not UserManager.get_user(callee):
            print("User not found")
            time.sleep(1)
            return
            
        call_id = VoiceCallManager.start_call(self.current_user, callee)
        print(self.t('calling', callee))
        
        # Симуляция звонка
        for i in range(20):
            call = VoiceCallManager.active_calls.get(call_id)
            if not call or call["status"] != "ringing":
                break
                
            print(f"Ringing... {i+1}")
            time.sleep(1)
        
        if call and call["status"] == "active":
            print(self.t('call_connected', callee))
            input(self.t("press_enter"))
        else:
            print(self.t('call_ended'))
            VoiceCallManager.end_call(call_id)
            time.sleep(1)

    def active_calls(self):
        # В реальной реализации здесь будет обработка входящих звонков
        print("Active calls feature is in development")
        time.sleep(1)

    def profile_menu(self):
        self.view_profile(self.current_user)

    def admin_menu(self):
        while True:
            self.clear_screen()
            print(f"\n{self.t('admin_menu')}")
            print(f"1. {self.t('view_requests')}")
            print(f"2. {self.t('update_app')}")
            print(f"0. {self.t('back')}")
            
            choice = input(self.t("select_option"))
            
            if choice == "1":
                self.admin_support_tickets()
            elif choice == "2":
                self.admin_update_app()
            elif choice == "0":
                return
            else:
                print(self.t('invalid_choice'))
                time.sleep(1)

    def admin_support_tickets(self):
        tickets = SupportSystem.get_tickets()
        
        if not tickets:
            print(self.t('no_requests'))
            time.sleep(1)
            return
            
        self.clear_screen()
        print(f"\n{self.t('verification_requests')}")
        for i, ticket in enumerate(tickets, 1):
            print(f"\n{i}. {ticket['user']}: {ticket['message']}")
            print(f"  1. {self.t('accept')}")
            print(f"  2. {self.t('reject')}")
            print(f"  3. {self.t('view_profile')}")
            
            action = input(self.t("select_option"))
            if action == "1":
                # Принять запрос
                SupportSystem.respond_to_ticket(ticket["id"], "Request approved", CONFIG["admin_username"])
                print("Request approved")
            elif action == "2":
                # Отклонить запрос
                SupportSystem.respond_to_ticket(ticket["id"], "Request rejected", CONFIG["admin_username"])
                print("Request rejected")
            elif action == "3":
                # Просмотр профиля
                self.view_profile(ticket["user"])
                
            time.sleep(1)

    def admin_update_app(self):
        print("Update feature is in development")
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
