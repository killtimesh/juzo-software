import os
import json
import asyncio
import threading
from telethon import TelegramClient
import customtkinter as ctk
from tkinter import messagebox
import shutil

class AccountManager:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Управление аккаунтами")
        self.window.geometry("900x700")
        
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self.thread.start()
        
        self.clients = {}
        self.parent_window = None
        
        self.load_proxy_settings()
        self.setup_ui()
        
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def _run_event_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
        
    def load_proxy_settings(self):
        self.proxy_settings = {}
        try:
            if os.path.exists('proxy_settings.json'):
                with open('proxy_settings.json', 'r') as f:
                    self.proxy_settings = json.load(f)
        except:
            pass
            
    def save_proxy_settings(self):
        try:
            with open('proxy_settings.json', 'w') as f:
                json.dump(self.proxy_settings, f, indent=4)
        except:
            pass
            
    def load_global_proxy(self):
        try:
            if os.path.exists('global_proxy.json'):
                with open('global_proxy.json', 'r') as f:
                    settings = json.load(f)
                    self.global_proxy_var.set(settings.get('enabled', False))
                    self.global_proxy_type.set(settings.get('type', 'socks5'))
                    self.global_proxy_host.set(settings.get('host', ''))
                    self.global_proxy_port.set(settings.get('port', ''))
                    self.global_proxy_username.set(settings.get('username', ''))
                    self.global_proxy_password.set(settings.get('password', ''))
        except:
            pass
            
    def save_global_proxy(self):
        try:
            settings = {
                'enabled': self.global_proxy_var.get(),
                'type': self.global_proxy_type.get(),
                'host': self.global_proxy_host.get(),
                'port': self.global_proxy_port.get(),
                'username': self.global_proxy_username.get(),
                'password': self.global_proxy_password.get()
            }
            with open('global_proxy.json', 'w') as f:
                json.dump(settings, f, indent=4)
        except:
            pass
            
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
            text="Управление аккаунтами",
            font=("Arial", 24, "bold")
        ).pack(pady=10)
        
        main_container = ctk.CTkFrame(self.window)
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        left_panel = ctk.CTkFrame(main_container)
        left_panel.pack(side="left", fill="both", padx=10, pady=10, expand=True)
        
        accounts_frame = ctk.CTkFrame(left_panel)
        accounts_frame.pack(fill="both", expand=True)
        
        header_frame = ctk.CTkFrame(accounts_frame)
        header_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            header_frame,
            text="Аккаунты:",
            font=("Arial", 16, "bold")
        ).pack(side="left")
        
        add_button = ctk.CTkButton(
            header_frame,
            text="➕ Добавить аккаунт",
            command=self.show_add_account,
            width=150
        )
        add_button.pack(side="right")
        
        self.accounts_container = ctk.CTkScrollableFrame(accounts_frame)
        self.accounts_container.pack(fill="both", expand=True, pady=10)
        
        right_panel = ctk.CTkFrame(main_container)
        right_panel.pack(side="right", fill="both", padx=10, pady=10, expand=True)
        
        proxy_frame = ctk.CTkFrame(right_panel)
        proxy_frame.pack(fill="x", pady=10)
        
        proxy_header = ctk.CTkFrame(proxy_frame)
        proxy_header.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            proxy_header,
            text="Общие настройки прокси:",
            font=("Arial", 16, "bold")
        ).pack(side="left")
        
        self.global_proxy_var = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(
            proxy_header,
            text="Включить",
            variable=self.global_proxy_var,
            command=self.toggle_global_proxy
        ).pack(side="right")
        
        proxy_settings = ctk.CTkFrame(proxy_frame)
        proxy_settings.pack(fill="x", pady=5)
        
        type_frame = ctk.CTkFrame(proxy_settings)
        type_frame.pack(fill="x", pady=2)
        
        ctk.CTkLabel(
            type_frame,
            text="Тип:"
        ).pack(side="left", padx=5)
        
        self.global_proxy_type = ctk.StringVar(value="socks5")
        type_menu = ctk.CTkOptionMenu(
            type_frame,
            values=["socks5", "http", "https"],
            variable=self.global_proxy_type
        )
        type_menu.pack(side="right", padx=5)
        
        host_frame = ctk.CTkFrame(proxy_settings)
        host_frame.pack(fill="x", pady=2)
        
        ctk.CTkLabel(
            host_frame,
            text="Хост:"
        ).pack(side="left", padx=5)
        
        self.global_proxy_host = ctk.StringVar()
        host_entry = ctk.CTkEntry(
            host_frame,
            textvariable=self.global_proxy_host
        )
        host_entry.pack(side="right", padx=5)
        
        port_frame = ctk.CTkFrame(proxy_settings)
        port_frame.pack(fill="x", pady=2)
        
        ctk.CTkLabel(
            port_frame,
            text="Порт:"
        ).pack(side="left", padx=5)
        
        self.global_proxy_port = ctk.StringVar()
        port_entry = ctk.CTkEntry(
            port_frame,
            textvariable=self.global_proxy_port,
            width=100
        )
        port_entry.pack(side="right", padx=5)
        
        auth_frame = ctk.CTkFrame(proxy_settings)
        auth_frame.pack(fill="x", pady=2)
        
        ctk.CTkLabel(
            auth_frame,
            text="Авторизация:"
        ).pack(side="left", padx=5)
        
        auth_inputs = ctk.CTkFrame(auth_frame)
        auth_inputs.pack(side="right", padx=5)
        
        self.global_proxy_username = ctk.StringVar()
        username_entry = ctk.CTkEntry(
            auth_inputs,
            textvariable=self.global_proxy_username,
            placeholder_text="Логин",
            width=100
        )
        username_entry.pack(side="left", padx=2)
        
        self.global_proxy_password = ctk.StringVar()
        password_entry = ctk.CTkEntry(
            auth_inputs,
            textvariable=self.global_proxy_password,
            placeholder_text="Пароль",
            show="•",
            width=100
        )
        password_entry.pack(side="right", padx=2)
        
        save_button = ctk.CTkButton(
            proxy_settings,
            text="Сохранить",
            command=self.save_global_proxy_settings
        )
        save_button.pack(pady=10)
        
        self.load_global_proxy()
        self.refresh_accounts()
        
    def refresh_accounts(self):
        for widget in self.accounts_container.winfo_children():
            widget.destroy()
            
        if not os.path.exists('sessions'):
            os.makedirs('sessions')
            return
            
        session_files = [f for f in os.listdir('sessions') if f.endswith('.session')]
        
        if not session_files:
            ctk.CTkLabel(
                self.accounts_container,
                text="Нет добавленных аккаунтов",
                font=("Arial", 12)
            ).pack(pady=20)
            return
            
        for session_file in session_files:
            session_name = session_file[:-8]
            
            future = asyncio.run_coroutine_threadsafe(
                self.check_account(session_file),
                self.loop
            )
            
            try:
                me = future.result()
                if me:
                    self.create_account_frame(session_name, me)
            except Exception as e:
                print(f"Error checking account {session_name}: {str(e)}")
                
    async def check_account(self, session_file):
        session_name = session_file[:-8]
        session_path = os.path.join('sessions', session_file)
        
        proxy = None
        if session_name in self.proxy_settings:
            config = self.proxy_settings[session_name]
            if config.get('host') and config.get('port'):
                proxy = {
                    'proxy_type': config.get('type', 'socks5'),
                    'addr': config['host'],
                    'port': config['port'],
                    'username': config.get('username'),
                    'password': config.get('password')
                }
                
        try:
            client = TelegramClient(
                session_path,
                '17349',
                '344583e45741c457fe1862106095a5eb',
                proxy=proxy
            )
            
            await client.connect()
            
            if await client.is_user_authorized():
                me = await client.get_me()
                self.clients[session_name] = client
                return me
            else:
                await client.disconnect()
                return None
                
        except Exception as e:
            print(f"Error connecting to {session_name}: {str(e)}")
            return None
            
    def create_account_frame(self, session_name, me):
        frame = ctk.CTkFrame(self.accounts_container)
        frame.pack(fill="x", pady=5)
        
        info_frame = ctk.CTkFrame(frame)
        info_frame.pack(side="left", padx=10, pady=5)
        
        name = me.first_name
        if me.last_name:
            name += f" {me.last_name}"
            
        ctk.CTkLabel(
            info_frame,
            text=name,
            font=("Arial", 14, "bold")
        ).pack(side="top")
        
        if me.phone:
            ctk.CTkLabel(
                info_frame,
                text=f"+{me.phone}",
                font=("Arial", 12)
            ).pack(side="bottom")
            
        buttons_frame = ctk.CTkFrame(frame)
        buttons_frame.pack(side="right", padx=10)
        
        def show_info():
            self.show_account_info(session_name)
            
        def delete_acc():
            self.delete_account(session_name)
            
        ctk.CTkButton(
            buttons_frame,
            text="ℹ️",
            width=30,
            command=show_info
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            buttons_frame,
            text="❌",
            width=30,
            fg_color="red",
            command=delete_acc
        ).pack(side="right", padx=2)
        
    def show_account_info(self, session_name):
        info_window = ctk.CTkToplevel(self.window)
        info_window.title(f"Информация об аккаунте {session_name}")
        info_window.geometry("400x500")
        info_window.resizable(False, False)
        
        info_window.transient(self.window)
        info_window.grab_set()
        
        info_window.update_idletasks()
        width = info_window.winfo_width()
        height = info_window.winfo_height()
        x = (info_window.winfo_screenwidth() // 2) - (width // 2)
        y = (info_window.winfo_screenheight() // 2) - (height // 2)
        info_window.geometry(f"{width}x{height}+{x}+{y}")
        
        main_frame = ctk.CTkFrame(info_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            main_frame,
            text=f"Аккаунт: {session_name}",
            font=("Arial", 16, "bold")
        ).pack(pady=10)
        
        proxy_frame = ctk.CTkFrame(main_frame)
        proxy_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            proxy_frame,
            text="Настройки прокси:",
            font=("Arial", 14, "bold")
        ).pack(pady=5)
        
        settings_frame = ctk.CTkFrame(proxy_frame)
        settings_frame.pack(fill="x", pady=5)
        
        type_frame = ctk.CTkFrame(settings_frame)
        type_frame.pack(fill="x", pady=2)
        
        ctk.CTkLabel(
            type_frame,
            text="Тип:"
        ).pack(side="left", padx=5)
        
        proxy_type = ctk.StringVar(value="socks5")
        if session_name in self.proxy_settings:
            proxy_type.set(self.proxy_settings[session_name].get('type', 'socks5'))
            
        type_menu = ctk.CTkOptionMenu(
            type_frame,
            values=["socks5", "http", "https"],
            variable=proxy_type
        )
        type_menu.pack(side="right", padx=5)
        
        host_frame = ctk.CTkFrame(settings_frame)
        host_frame.pack(fill="x", pady=2)
        
        ctk.CTkLabel(
            host_frame,
            text="Хост:"
        ).pack(side="left", padx=5)
        
        proxy_host = ctk.StringVar()
        if session_name in self.proxy_settings:
            proxy_host.set(self.proxy_settings[session_name].get('host', ''))
            
        host_entry = ctk.CTkEntry(
            host_frame,
            textvariable=proxy_host
        )
        host_entry.pack(side="right", padx=5)
        
        port_frame = ctk.CTkFrame(settings_frame)
        port_frame.pack(fill="x", pady=2)
        
        ctk.CTkLabel(
            port_frame,
            text="Порт:"
        ).pack(side="left", padx=5)
        
        proxy_port = ctk.StringVar()
        if session_name in self.proxy_settings:
            proxy_port.set(self.proxy_settings[session_name].get('port', ''))
            
        port_entry = ctk.CTkEntry(
            port_frame,
            textvariable=proxy_port,
            width=100
        )
        port_entry.pack(side="right", padx=5)
        
        auth_frame = ctk.CTkFrame(settings_frame)
        auth_frame.pack(fill="x", pady=2)
        
        ctk.CTkLabel(
            auth_frame,
            text="Авторизация:"
        ).pack(side="left", padx=5)
        
        auth_inputs = ctk.CTkFrame(auth_frame)
        auth_inputs.pack(side="right", padx=5)
        
        proxy_username = ctk.StringVar()
        if session_name in self.proxy_settings:
            proxy_username.set(self.proxy_settings[session_name].get('username', ''))
            
        username_entry = ctk.CTkEntry(
            auth_inputs,
            textvariable=proxy_username,
            placeholder_text="Логин",
            width=100
        )
        username_entry.pack(side="left", padx=2)
        
        proxy_password = ctk.StringVar()
        if session_name in self.proxy_settings:
            proxy_password.set(self.proxy_settings[session_name].get('password', ''))
            
        password_entry = ctk.CTkEntry(
            auth_inputs,
            textvariable=proxy_password,
            placeholder_text="Пароль",
            show="•",
            width=100
        )
        password_entry.pack(side="right", padx=2)
        
        def save_proxy():
            if proxy_host.get() and proxy_port.get():
                self.proxy_settings[session_name] = {
                    'type': proxy_type.get(),
                    'host': proxy_host.get(),
                    'port': proxy_port.get(),
                    'username': proxy_username.get(),
                    'password': proxy_password.get()
                }
                self.save_proxy_settings()
                self.show_success("Настройки прокси сохранены")
                info_window.destroy()
                self.refresh_accounts()
            else:
                self.show_error("Ошибка", "Введите хост и порт прокси")
                
        save_button = ctk.CTkButton(
            settings_frame,
            text="Сохранить",
            command=save_proxy
        )
        save_button.pack(pady=10)
        
    def delete_account(self, session_name):
        dialog = ctk.CTkToplevel(self.window)
        dialog.title("Подтверждение")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        
        dialog.transient(self.window)
        dialog.grab_set()
        
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        frame = ctk.CTkFrame(dialog)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            frame,
            text="Удаление аккаунта",
            font=("Arial", 16, "bold")
        ).pack(pady=10)
        
        ctk.CTkLabel(
            frame,
            text=f"Вы действительно хотите удалить аккаунт {session_name}?",
            font=("Arial", 12)
        ).pack(pady=10)
        
        buttons_frame = ctk.CTkFrame(frame)
        buttons_frame.pack(pady=10)
        
        ctk.CTkButton(
            buttons_frame,
            text="Отмена",
            command=dialog.destroy,
            width=100
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            buttons_frame,
            text="Удалить",
            command=lambda: self.confirm_delete(dialog, session_name),
            fg_color="red",
            width=100
        ).pack(side="right", padx=5)
        
    def confirm_delete(self, dialog, session_name):
        try:
            if session_name in self.clients:
                client = self.clients[session_name]
                future = asyncio.run_coroutine_threadsafe(
                    client.disconnect(),
                    self.loop
                )
                future.result()
                del self.clients[session_name]
                
            session_file = os.path.join('sessions', f"{session_name}.session")
            if os.path.exists(session_file):
                os.remove(session_file)
                
            if session_name in self.proxy_settings:
                del self.proxy_settings[session_name]
                self.save_proxy_settings()
                
            dialog.destroy()
            self.refresh_accounts()
            self.show_success("Аккаунт успешно удален")
            
        except Exception as e:
            self.show_error("Ошибка", f"Не удалось удалить аккаунт: {str(e)}")
            dialog.destroy()
            
    def show_add_account(self):
        dialog = ctk.CTkToplevel(self.window)
        dialog.title("Добавление аккаунта")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        
        dialog.transient(self.window)
        dialog.grab_set()
        
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        frame = ctk.CTkFrame(dialog)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            frame,
            text="Добавление аккаунта",
            font=("Arial", 16, "bold")
        ).pack(pady=10)
        
        file_frame = ctk.CTkFrame(frame)
        file_frame.pack(fill="x", pady=10)
        
        file_var = ctk.StringVar()
        file_entry = ctk.CTkEntry(
            file_frame,
            textvariable=file_var,
            width=200
        )
        file_entry.pack(side="left", padx=5)
        
        def select_file():
            file_path = ctk.filedialog.askopenfilename(
                title="Выберите файл сессии",
                filetypes=[("Session files", "*.session")]
            )
            if file_path:
                file_var.set(file_path)
                
        select_button = ctk.CTkButton(
            file_frame,
            text="Выбрать файл",
            command=select_file,
            width=100
        )
        select_button.pack(side="right", padx=5)
        
        def add_account():
            file_path = file_var.get()
            if not file_path or not os.path.exists(file_path):
                self.show_error("Ошибка", "Выберите файл сессии")
                return
                
            try:
                if not os.path.exists('sessions'):
                    os.makedirs('sessions')
                    
                shutil.copy2(file_path, 'sessions')
                dialog.destroy()
                self.refresh_accounts()
                self.show_success("Аккаунт успешно добавлен")
                
            except Exception as e:
                self.show_error("Ошибка", f"Не удалось добавить аккаунт: {str(e)}")
                
        add_button = ctk.CTkButton(
            frame,
            text="Добавить",
            command=add_account,
            width=200
        )
        add_button.pack(pady=10)
        
    def show_error(self, title: str, message: str):
        dialog = messagebox.showerror(title, message)
        
        try:
            self.window.lift()
        except:
            pass
            
        return dialog
        
    def run(self):
        self.window.mainloop()
        
    async def close_clients(self):
        for client in self.clients.values():
            try:
                await client.disconnect()
            except:
                pass
                
    def set_parent(self, parent_window):
        self.parent_window = parent_window
        
    def on_closing(self):
        if self.parent_window:
            future = asyncio.run_coroutine_threadsafe(
                self.close_clients(),
                self.loop
            )
            try:
                future.result(timeout=5)
            except:
                pass
                
            self.loop.call_soon_threadsafe(self.loop.stop)
            
            self.parent_window.deiconify()
            self.window.destroy()
        else:
            future = asyncio.run_coroutine_threadsafe(
                self.close_clients(),
                self.loop
            )
            try:
                future.result(timeout=5)
            except:
                pass
            self.loop.call_soon_threadsafe(self.loop.stop)
            self.window.destroy()
            
    def toggle_global_proxy(self):
        enabled = self.global_proxy_var.get()
        for widget in self.window.winfo_children():
            if isinstance(widget, ctk.CTkEntry):
                widget.configure(state="normal" if enabled else "disabled")
                
    def save_global_proxy_settings(self):
        if self.global_proxy_var.get():
            if not self.global_proxy_host.get() or not self.global_proxy_port.get():
                self.show_error("Ошибка", "Введите хост и порт прокси")
                return
                
        self.save_global_proxy()
        self.show_success("Настройки прокси сохранены")
        
    def show_success(self, message):
        dialog = messagebox.showinfo("Успех", message)
        
        try:
            self.window.lift()
        except:
            pass
            
        return dialog 