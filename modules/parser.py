import os
import asyncio
import csv
from datetime import datetime
from telethon import TelegramClient
import customtkinter as ctk
import threading
import json

class TelegramParser:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Парсер участников")
        self.window.geometry("900x700")
        
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self.thread.start()
        
        self.clients = {}
        self.parent_window = None
        self.setup_ui()
        
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def _run_event_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
        
    def setup_ui(self):
        top_panel = ctk.CTkFrame(self.window)
        top_panel.pack(fill="x", padx=20, pady=10)
        
        back_button = ctk.CTkButton(
            top_panel,
            text="← Главное меню",
            command=self.return_to_main,
            width=150,
            height=32
        )
        back_button.pack(side="left")
        
        ctk.CTkLabel(
            top_panel,
            text="Парсер участников из сообщений",
            font=("Arial", 24, "bold")
        ).pack(pady=10)
        
        main_container = ctk.CTkFrame(self.window)
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        input_frame = ctk.CTkFrame(main_container)
        input_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            input_frame,
            text="Ссылки на группы (каждая с новой строки):",
            font=("Arial", 14, "bold")
        ).pack(pady=5)
        
        self.groups_text = ctk.CTkTextbox(input_frame, height=150)
        self.groups_text.pack(fill="x", padx=20, pady=5)
        
        settings_frame = ctk.CTkFrame(main_container)
        settings_frame.pack(fill="x", pady=10)
        
        limit_frame = ctk.CTkFrame(settings_frame)
        limit_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(
            limit_frame,
            text="Количество сообщений для парсинга с группы:",
            font=("Arial", 12)
        ).pack(side="left", padx=5)
        
        self.limit_var = ctk.StringVar(value="1000")
        limit_entry = ctk.CTkEntry(
            limit_frame,
            textvariable=self.limit_var,
            width=100
        )
        limit_entry.pack(side="right", padx=5)
        
        self.start_button = ctk.CTkButton(
            main_container,
            text="Начать парсинг",
            command=self.start_parsing,
            font=("Arial", 14, "bold"),
            height=40
        )
        self.start_button.pack(pady=10)
        
        log_frame = ctk.CTkFrame(main_container)
        log_frame.pack(fill="both", expand=True, pady=10)
        
        ctk.CTkLabel(
            log_frame,
            text="Лог парсинга:",
            font=("Arial", 14, "bold")
        ).pack(pady=5)
        
        self.log_text = ctk.CTkTextbox(log_frame)
        self.log_text.pack(fill="both", expand=True, padx=10, pady=5)
        
    def start_parsing(self):
        groups = self.groups_text.get("1.0", "end-1c").split("\n")
        groups = [g.strip() for g in groups if g.strip()]
        
        if not groups:
            self.log("Введите хотя бы одну ссылку на группу", "error")
            return
            
        try:
            limit = int(self.limit_var.get())
            if limit <= 0:
                raise ValueError()
        except ValueError:
            self.log("Введите корректное количество сообщений", "error")
            return
            
        self.start_button.configure(state="disabled")
        
        asyncio.run_coroutine_threadsafe(
            self.parse_groups(groups, limit),
            self.loop
        )
        
    async def parse_groups(self, groups, limit):
        try:
            if not self.clients:
                await self.init_clients()
                
            if not self.clients:
                self.log("Нет доступных аккаунтов", "error")
                self.start_button.configure(state="normal")
                return
                
            if not os.path.exists('results'):
                os.makedirs('results')
                
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"results/parsed_users_{timestamp}.csv"
            
            total_parsed = 0
            all_usernames = set()
            
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Group', 'Username'])
                
                for group in groups:
                    try:
                        self.log(f"Парсинг группы {group}...")
                        
                        if not group.startswith(('https://t.me/', 't.me/', '@')):
                            self.log(f"Неверный формат ссылки: {group}. Используйте формат t.me/username или @username", "error")
                            continue
                            
                        client = list(self.clients.values())[0]['client']
                        
                        users = await self.get_users_from_messages(client, group, limit)
                        
                        if users:
                            group_usernames = set()
                            
                            for username in users:
                                if username not in all_usernames:
                                    all_usernames.add(username)
                                    group_usernames.add(username)
                                    writer.writerow([group, username])
                                    
                            total_parsed += len(group_usernames)
                            self.log(f"Найдено {len(group_usernames)} уникальных пользователей в {group}", "success")
                        else:
                            self.log(f"Не удалось получить пользователей из группы {group}", "warning")
                            
                        await asyncio.sleep(3)
                        
                    except Exception as e:
                        self.log(f"Ошибка при парсинге {group}: {str(e)}", "error")
                        continue
                        
            if total_parsed > 0:
                self.log(f"Парсинг завершен! Всего найдено {total_parsed} уникальных пользователей")
                self.log(f"Результаты сохранены в файл: {filename}", "success")
            else:
                self.log("Парсинг завершен, но не удалось получить ни одного пользователя", "warning")
                
        except Exception as e:
            self.log(f"Критическая ошибка: {str(e)}", "error")
            
        finally:
            self.start_button.configure(state="normal")
            
    async def get_users_from_messages(self, client, group, limit):
        usernames = set()
        
        try:
            entity = await client.get_entity(group)
            
            async for message in client.iter_messages(entity, limit=limit):
                if message.sender_id:
                    try:
                        user = await client.get_entity(message.sender_id)
                        
                        if not getattr(user, 'bot', False) and getattr(user, 'username', None):
                            usernames.add(user.username)
                            
                            if len(usernames) % 50 == 0:
                                self.log(f"Найдено {len(usernames)} уникальных пользователей...", "info")
                                
                    except Exception:
                        continue
                        
                await asyncio.sleep(0.1)
                
        except Exception as e:
            self.log(f"Ошибка при получении сообщений из группы {group}: {str(e)}", "error")
            
        return usernames
        
    async def init_clients(self):
        if not os.path.exists('sessions'):
            self.log("Папка sessions не найдена", "error")
            return
            
        session_files = [f for f in os.listdir('sessions') if f.endswith('.session')]
        
        if not session_files:
            self.log("Сессии не найдены", "error")
            return
            
        proxy_settings = {}
        try:
            if os.path.exists('proxy_settings.json'):
                with open('proxy_settings.json', 'r') as f:
                    proxy_settings = json.load(f)
        except:
            self.log("Не удалось загрузить настройки прокси", "warning")
            
        for session_file in session_files:
            try:
                session_name = session_file[:-8]
                session_path = os.path.join('sessions', session_file)
                
                proxy = None
                if session_name in proxy_settings:
                    config = proxy_settings[session_name]
                    if config.get('host') and config.get('port'):
                        proxy = {
                            'proxy_type': config.get('type', 'socks5'),
                            'addr': config['host'],
                            'port': config['port'],
                            'username': config.get('username'),
                            'password': config.get('password')
                        }
                        self.log(f"Используем прокси {config['host']}:{config['port']} для {session_name}")
                        
                client = TelegramClient(
                    session_path,
                    '17349',
                    '344583e45741c457fe1862106095a5eb',
                    system_version="4.16.30-vxCUSTOM",
                    device_model="Desktop",
                    proxy=proxy
                )
                
                await client.connect()
                
                if await client.is_user_authorized():
                    self.clients[session_name] = {
                        'client': client,
                        'requests': 0
                    }
                    self.log(f"Подключен аккаунт: {session_name}", "success")
                else:
                    self.log(f"Аккаунт {session_name} не авторизован", "error")
                    
            except Exception as e:
                self.log(f"Ошибка при инициализации {session_name}: {str(e)}", "error")
                
    def run(self):
        self.window.mainloop()
        
    def set_parent(self, parent_window):
        self.parent_window = parent_window
        
    def return_to_main(self):
        if self.parent_window:
            for client in self.clients.values():
                try:
                    future = asyncio.run_coroutine_threadsafe(
                        client.disconnect(),
                        self.loop
                    )
                    future.result()
                except:
                    pass
                    
            self.loop.call_soon_threadsafe(self.loop.stop)
            
            self.parent_window.deiconify()
            self.window.destroy()
            
    def on_closing(self):
        if self.parent_window:
            self.return_to_main()
        else:
            for client in self.clients.values():
                try:
                    future = asyncio.run_coroutine_threadsafe(
                        client.disconnect(),
                        self.loop
                    )
                    future.result()
                except:
                    pass
            self.loop.call_soon_threadsafe(self.loop.stop)
            self.window.destroy()
            
    def log(self, message, level="info"):
        prefix = {
            "info": "ℹ️",
            "success": "✅",
            "error": "❌",
            "warning": "⚠️"
        }.get(level, "ℹ️")
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{timestamp}] {prefix} {message}\n")
        self.log_text.see("end")
        self.window.update() 