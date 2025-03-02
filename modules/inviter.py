import os
import asyncio
import csv
from datetime import datetime
import random
from telethon import TelegramClient, errors
import customtkinter as ctk
import threading
import json
from tkinter import messagebox

class TelegramInviter:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Инвайтер")
        self.window.geometry("900x700")
        
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self.thread.start()
        
        self.clients = {}
        self.selected_clients = set()
        self.parent_window = None
        
        self.setup_ui()
        self.init_clients()
        
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
            text="Инвайтер",
            font=("Arial", 24, "bold")
        ).pack(pady=10)
        
        main_container = ctk.CTkFrame(self.window)
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        left_panel = ctk.CTkFrame(main_container)
        left_panel.pack(side="left", fill="both", padx=10, pady=10, expand=True)
        
        input_frame = ctk.CTkFrame(left_panel)
        input_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            input_frame,
            text="Файл с пользователями:",
            font=("Arial", 14, "bold")
        ).pack(pady=5)
        
        file_frame = ctk.CTkFrame(input_frame)
        file_frame.pack(fill="x", padx=20, pady=5)
        
        self.file_var = ctk.StringVar()
        file_entry = ctk.CTkEntry(
            file_frame,
            textvariable=self.file_var,
            width=250
        )
        file_entry.pack(side="left", padx=(0, 10))
        
        select_button = ctk.CTkButton(
            file_frame,
            text="Выбрать файл",
            command=self.select_file,
            width=100
        )
        select_button.pack(side="right")
        
        target_frame = ctk.CTkFrame(left_panel)
        target_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            target_frame,
            text="Целевая группа:",
            font=("Arial", 14, "bold")
        ).pack(pady=5)
        
        self.target_var = ctk.StringVar()
        ctk.CTkEntry(
            target_frame,
            textvariable=self.target_var,
            placeholder_text="Введите ссылку на группу",
            width=350
        ).pack(padx=20, pady=5)
        
        delay_frame = ctk.CTkFrame(left_panel)
        delay_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            delay_frame,
            text="Задержка между инвайтами (сек):",
            font=("Arial", 14, "bold")
        ).pack(pady=5)
        
        self.delay_var = ctk.StringVar(value="60")
        ctk.CTkEntry(
            delay_frame,
            textvariable=self.delay_var,
            width=100
        ).pack(padx=20, pady=5)
        
        limit_frame = ctk.CTkFrame(left_panel)
        limit_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            limit_frame,
            text="Лимит приглашений на аккаунт:",
            font=("Arial", 14, "bold")
        ).pack(pady=5)
        
        self.limit_var = ctk.StringVar(value="35")
        ctk.CTkEntry(
            limit_frame,
            textvariable=self.limit_var,
            width=100
        ).pack(padx=20, pady=5)
        
        self.start_button = ctk.CTkButton(
            left_panel,
            text="Начать инвайтинг",
            command=self.start_inviting,
            font=("Arial", 14, "bold"),
            height=40
        )
        self.start_button.pack(pady=10)
        
        right_panel = ctk.CTkFrame(main_container)
        right_panel.pack(side="right", fill="both", padx=10, pady=10, expand=True)
        
        accounts_frame = ctk.CTkFrame(right_panel)
        accounts_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            accounts_frame,
            text="Аккаунты:",
            font=("Arial", 14, "bold")
        ).pack(pady=5)
        
        self.accounts_container = ctk.CTkScrollableFrame(accounts_frame, height=150)
        self.accounts_container.pack(fill="x", pady=5)
        
        log_frame = ctk.CTkFrame(right_panel)
        log_frame.pack(fill="both", expand=True, pady=10)
        
        ctk.CTkLabel(
            log_frame,
            text="Лог инвайтинга:",
            font=("Arial", 14, "bold")
        ).pack(pady=5)
        
        self.log_text = ctk.CTkTextbox(log_frame)
        self.log_text.pack(fill="both", expand=True)
        
    def select_file(self):
        file_path = ctk.filedialog.askopenfilename(
            title="Выберите файл с пользователями",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt")]
        )
        if file_path:
            self.file_var.set(file_path)
            
    def init_clients(self):
        if not os.path.exists('sessions'):
            os.makedirs('sessions')
            return
            
        session_files = [f for f in os.listdir('sessions') if f.endswith('.session')]
        
        for session_file in session_files:
            session_name = session_file[:-8]
            
            account_frame = ctk.CTkFrame(self.accounts_container)
            account_frame.pack(fill="x", pady=2)
            
            var = ctk.BooleanVar(value=True)
            checkbox = ctk.CTkCheckBox(
                account_frame,
                text=session_name,
                variable=var,
                command=lambda n=session_name, v=var: self.toggle_account(n, v)
            )
            checkbox.pack(side="left", padx=5)
            
            self.selected_clients.add(session_name)
            
    def toggle_account(self, session_name, var):
        if var.get():
            self.selected_clients.add(session_name)
        else:
            self.selected_clients.discard(session_name)
            
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
        
    def start_inviting(self):
        file_path = self.file_var.get()
        target = self.target_var.get()
        
        if not file_path or not os.path.exists(file_path):
            self.log("Выберите файл с пользователями", "error")
            return
            
        if not target:
            self.log("Введите ссылку на целевую группу", "error")
            return
            
        try:
            delay = int(self.delay_var.get())
            limit = int(self.limit_var.get())
            if delay < 0 or limit < 0:
                raise ValueError()
        except ValueError:
            self.log("Введите корректные значения задержки и лимита", "error")
            return
            
        if not self.selected_clients:
            self.log("Выберите хотя бы один аккаунт", "error")
            return
            
        self.start_button.configure(state="disabled")
        
        asyncio.run_coroutine_threadsafe(
            self.invite_users(target, delay, limit),
            self.loop
        )
        
    async def invite_users(self, target_group, delay, limit):
        try:
            await self.init_telegram_clients()
            
            if not self.clients:
                self.log("Нет доступных аккаунтов", "error")
                self.start_button.configure(state="normal")
                return
                
            users = []
            file_path = self.file_var.get()
            
            if file_path.endswith('.csv'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    next(reader)
                    for row in reader:
                        if row and row[1]:
                            users.append(row[1])
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    users = [line.strip() for line in f if line.strip()]
                    
            if not users:
                self.log("Файл не содержит пользователей", "error")
                self.start_button.configure(state="normal")
                return
                
            self.log(f"Загружено {len(users)} пользователей")
            
            random.shuffle(users)
            
            for session_name, client_data in self.clients.items():
                if session_name not in self.selected_clients:
                    continue
                    
                client = client_data['client']
                
                try:
                    target = await client.get_entity(target_group)
                    
                    if not hasattr(target, 'admin_rights'):
                        self.log(f"[{session_name}] Нет прав администратора в группе", "error")
                        continue
                        
                    admin_rights = target.admin_rights
                    if not admin_rights or not admin_rights.invite_users:
                        self.log(f"[{session_name}] Нет прав на приглашение пользователей", "error")
                        continue
                        
                    await self.process_users(client, users[:limit], target, admin_rights, delay)
                    users = users[limit:]
                    
                    if not users:
                        self.log("Все пользователи обработаны", "success")
                        break
                        
                except Exception as e:
                    self.log(f"[{session_name}] Ошибка: {str(e)}", "error")
                    continue
                    
        except Exception as e:
            self.log(f"Критическая ошибка: {str(e)}", "error")
            
        finally:
            self.start_button.configure(state="normal")
            
    async def process_users(self, client, users, target, admin_rights, delay):
        session_name = next(name for name, data in self.clients.items() if data['client'] == client)
        invited = 0
        
        for username in users:
            if not username:
                continue
                
            try:
                user = await client.get_entity(username)
                
                try:
                    await client.edit_admin(target, user, admin_rights)
                    invited += 1
                    self.log(f"[{session_name}] Пользователь {username} успешно приглашен", "success")
                except errors.UserAlreadyParticipantError:
                    self.log(f"[{session_name}] Пользователь {username} уже в группе", "warning")
                except errors.UserPrivacyRestrictedError:
                    self.log(f"[{session_name}] Пользователь {username} запретил приглашения", "warning")
                except errors.UserNotMutualContactError:
                    self.log(f"[{session_name}] Пользователь {username} не является взаимным контактом", "warning")
                except Exception as e:
                    self.log(f"[{session_name}] Ошибка при приглашении {username}: {str(e)}", "error")
                    
                await asyncio.sleep(delay + random.uniform(-5, 5))
                
            except Exception as e:
                self.log(f"[{session_name}] Не удалось найти пользователя {username}: {str(e)}", "error")
                continue
                
        self.log(f"[{session_name}] Приглашено {invited} пользователей")
        
    async def init_telegram_clients(self):
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
                        client['client'].disconnect(),
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
                        client['client'].disconnect(),
                        self.loop
                    )
                    future.result()
                except:
                    pass
            self.loop.call_soon_threadsafe(self.loop.stop)
            self.window.destroy() 