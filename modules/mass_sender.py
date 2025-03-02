import os
import asyncio
import random
import json
from telethon import TelegramClient, types
import customtkinter as ctk
import threading
from telethon.errors import FloodWaitError, ChatWriteForbiddenError
from datetime import datetime
from PIL import Image

class TelegramMassSender:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Массовая рассылка")
        self.window.geometry("1200x800")
        
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self.thread.start()
        
        self.clients = {}
        self.selected_clients = set()  # Выбранные аккаунты
        self.message_file = None
        self.image_file = None
        self.chats_file = None
        self.forward_message = None
        self.parent_window = None  # Добавляем ссылку на родительское окно
        
        self.setup_ui()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _run_event_loop(self):
        """Запуск event loop в отдельном потоке"""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def setup_ui(self):
        # Основной контейнер
        main_container = ctk.CTkFrame(self.window)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Верхняя панель с кнопкой возврата
        top_panel = ctk.CTkFrame(main_container)
        top_panel.pack(fill="x", pady=(0, 10))
        
        # Кнопка возврата в главное меню
        back_button = ctk.CTkButton(
            top_panel,
            text="← Главное меню",
            command=self.return_to_main,
            width=150,
            height=32
        )
        back_button.pack(side="left")
        
        # Заголовок
        ctk.CTkLabel(
            top_panel,
            text="Массовая рассылка",
            font=("Arial", 24, "bold")
        ).pack(pady=10)
        
        # Левая панель - настройки
        settings_frame = ctk.CTkFrame(main_container)
        settings_frame.pack(side="left", fill="both", expand=True, padx=10)
        
        # Выбор режима рассылки
        mode_frame = ctk.CTkFrame(settings_frame)
        mode_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            mode_frame,
            text="Режим рассылки:",
            font=("Arial", 14, "bold")
        ).pack(pady=5)
        
        self.mode_var = ctk.StringVar(value="text")
        modes = [
            ("Обычный текст", "text"),
            ("Пересылка сообщения", "forward"),
            ("Текст из файла (HTML)", "file"),
            ("Текст + фото", "photo")
        ]
        
        for text, value in modes:
            ctk.CTkRadioButton(
                mode_frame,
                text=text,
                value=value,
                variable=self.mode_var,
                command=self.update_message_input
            ).pack(pady=2)
        
        # Выбор целевой аудитории
        target_frame = ctk.CTkFrame(settings_frame)
        target_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            target_frame,
            text="Куда отправлять:",
            font=("Arial", 14, "bold")
        ).pack(pady=5)
        
        self.target_var = ctk.StringVar(value="all_chats")
        targets = [
            ("Все чаты аккаунта", "all_chats"),
            ("Чаты из файла", "file_chats"),
            ("Папка с чатами", "folder_chats"),
            ("Личные сообщения", "direct_messages"),
            ("Контакты", "contacts")
        ]
        
        for text, value in targets:
            ctk.CTkRadioButton(
                target_frame,
                text=text,
                value=value,
                variable=self.target_var,
                command=self.update_target_input
            ).pack(pady=2)
        
        # Настройки задержек
        delay_frame = ctk.CTkFrame(settings_frame)
        delay_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            delay_frame,
            text="Задержки (сек):",
            font=("Arial", 14, "bold")
        ).pack(pady=5)
        
        # Минимальная задержка
        min_delay_frame = ctk.CTkFrame(delay_frame)
        min_delay_frame.pack(fill="x", pady=2)
        
        ctk.CTkLabel(
            min_delay_frame,
            text="Минимальная:"
        ).pack(side="left", padx=5)
        
        self.min_delay_var = ctk.StringVar(value="30")
        ctk.CTkEntry(
            min_delay_frame,
            textvariable=self.min_delay_var,
            width=70
        ).pack(side="right", padx=5)
        
        # Максимальная задержка
        max_delay_frame = ctk.CTkFrame(delay_frame)
        max_delay_frame.pack(fill="x", pady=2)
        
        ctk.CTkLabel(
            max_delay_frame,
            text="Максимальная:"
        ).pack(side="left", padx=5)
        
        self.max_delay_var = ctk.StringVar(value="60")
        ctk.CTkEntry(
            max_delay_frame,
            textvariable=self.max_delay_var,
            width=70
        ).pack(side="right", padx=5)
        
        # Правая панель - сообщение и аккаунты
        content_frame = ctk.CTkFrame(main_container)
        content_frame.pack(side="right", fill="both", expand=True, padx=10)
        
        # Контейнер для ввода сообщения
        self.message_container = ctk.CTkFrame(content_frame)
        self.message_container.pack(fill="both", expand=True, pady=10)
        
        # Изначально показываем поле для текста
        self.show_text_input()
        
        # Список аккаунтов
        accounts_frame = ctk.CTkFrame(content_frame)
        accounts_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            accounts_frame,
            text="Аккаунты:",
            font=("Arial", 14, "bold")
        ).pack(pady=5)
        
        self.accounts_container = ctk.CTkScrollableFrame(accounts_frame, height=150)
        self.accounts_container.pack(fill="x", pady=5)
        
        # Кнопка запуска
        self.start_button = ctk.CTkButton(
            content_frame,
            text="Начать рассылку",
            command=self.start_sending,
            font=("Arial", 14, "bold"),
            height=40
        )
        self.start_button.pack(pady=10)
        
        # Лог
        log_frame = ctk.CTkFrame(content_frame)
        log_frame.pack(fill="both", expand=True, pady=10)
        
        ctk.CTkLabel(
            log_frame,
            text="Лог:",
            font=("Arial", 14, "bold")
        ).pack(pady=5)
        
        self.log_text = ctk.CTkTextbox(log_frame, height=150)
        self.log_text.pack(fill="both", expand=True)
        
        # Инициализируем клиентов
        self.init_clients()

    def show_text_input(self):
        """Показать поле для обычного текста"""
        self.clear_message_container()
        
        ctk.CTkLabel(
            self.message_container,
            text="Текст сообщения:",
            font=("Arial", 14, "bold")
        ).pack(pady=5)
        
        self.message_text = ctk.CTkTextbox(self.message_container, height=200)
        self.message_text.pack(fill="both", expand=True, padx=10)

    def show_forward_input(self):
        """Показать поле для пересылки сообщения"""
        self.clear_message_container()
        
        ctk.CTkLabel(
            self.message_container,
            text="ID чата и сообщения для пересылки (формат: chat_id:message_id):",
            font=("Arial", 14, "bold")
        ).pack(pady=5)
        
        self.forward_entry = ctk.CTkEntry(self.message_container)
        self.forward_entry.pack(fill="x", padx=10, pady=5)

    def show_file_input(self):
        """Показать поле для загрузки файла с текстом"""
        self.clear_message_container()
        
        ctk.CTkLabel(
            self.message_container,
            text="Файл с текстом (HTML):",
            font=("Arial", 14, "bold")
        ).pack(pady=5)
        
        file_frame = ctk.CTkFrame(self.message_container)
        file_frame.pack(fill="x", padx=10, pady=5)
        
        self.file_label = ctk.CTkLabel(file_frame, text="Файл не выбран")
        self.file_label.pack(side="left", padx=5)
        
        ctk.CTkButton(
            file_frame,
            text="Выбрать файл",
            command=self.select_message_file
        ).pack(side="right", padx=5)

    def show_photo_input(self):
        """Показать поля для текста и фото"""
        self.clear_message_container()
        
        ctk.CTkLabel(
            self.message_container,
            text="Текст сообщения:",
            font=("Arial", 14, "bold")
        ).pack(pady=5)
        
        self.message_text = ctk.CTkTextbox(self.message_container, height=150)
        self.message_text.pack(fill="both", expand=True, padx=10)
        
        photo_frame = ctk.CTkFrame(self.message_container)
        photo_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            photo_frame,
            text="Фото:",
            font=("Arial", 14, "bold")
        ).pack(side="left", padx=5)
        
        self.photo_label = ctk.CTkLabel(photo_frame, text="Фото не выбрано")
        self.photo_label.pack(side="left", padx=5)
        
        ctk.CTkButton(
            photo_frame,
            text="Выбрать фото",
            command=self.select_photo
        ).pack(side="right", padx=5)

    def clear_message_container(self):
        """Очистка контейнера сообщения"""
        for widget in self.message_container.winfo_children():
            widget.destroy()

    def update_message_input(self):
        """Обновление полей ввода в зависимости от режима"""
        mode = self.mode_var.get()
        if mode == "text":
            self.show_text_input()
        elif mode == "forward":
            self.show_forward_input()
        elif mode == "file":
            self.show_file_input()
        elif mode == "photo":
            self.show_photo_input()

    def update_target_input(self):
        """Обновление полей для выбора целевой аудитории"""
        target = self.target_var.get()
        if target == "file_chats":
            self.select_chats_file()
        elif target == "folder_chats":
            self.select_chats_folder()

    def select_message_file(self):
        """Выбор файла с текстом сообщения"""
        file_path = ctk.filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt")]
        )
        if file_path:
            self.message_file = file_path
            self.file_label.configure(text=os.path.basename(file_path))

    def select_photo(self):
        """Выбор фото для рассылки"""
        file_path = ctk.filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        if file_path:
            self.image_file = file_path
            self.photo_label.configure(text=os.path.basename(file_path))

    def select_chats_file(self):
        """Выбор файла со списком чатов"""
        file_path = ctk.filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt")]
        )
        if file_path:
            self.chats_file = file_path

    def select_chats_folder(self):
        """Выбор папки с чатами"""
        folder_path = ctk.filedialog.askdirectory()
        if folder_path:
            self.chats_folder = folder_path

    def init_clients(self):
        """Инициализация клиентов"""
        if not os.path.exists('sessions'):
            os.makedirs('sessions')
            return
            
        session_files = [f for f in os.listdir('sessions') if f.endswith('.session')]
        
        for session_file in session_files:
            session_name = session_file[:-8]
            
            # Создаем чекбокс для каждого аккаунта
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
        """Переключение выбора аккаунта"""
        if var.get():
            self.selected_clients.add(session_name)
        else:
            self.selected_clients.discard(session_name)

    def log(self, message, level="info"):
        """Добавление сообщения в лог"""
        prefix = {
            "info": "ℹ️",
            "success": "✅",
            "error": "❌",
            "warning": "⚠️"
        }.get(level, "ℹ️")
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{timestamp}] {prefix} {message}\n")
        self.log_text.see("end")

    async def get_target_chats(self, client, target_type):
        """Получение списка целевых чатов"""
        chats = []
        
        if target_type == "all_chats":
            dialogs = await client.get_dialogs()
            chats = [d for d in dialogs if d.is_group or d.is_channel]
            
        elif target_type == "file_chats":
            if self.chats_file and os.path.exists(self.chats_file):
                with open(self.chats_file, 'r', encoding='utf-8') as f:
                    chat_links = f.read().splitlines()
                for link in chat_links:
                    try:
                        chat = await client.get_entity(link.strip())
                        chats.append(chat)
                    except Exception as e:
                        self.log(f"Ошибка при получении чата {link}: {str(e)}", "error")
                        
        elif target_type == "folder_chats":
            if hasattr(self, 'chats_folder') and os.path.exists(self.chats_folder):
                folders = await client.get_dialogs()
                folder_chats = [d for d in folders if d.folder_id == int(self.chats_folder)]
                chats.extend(folder_chats)
                
        elif target_type == "direct_messages":
            dialogs = await client.get_dialogs()
            chats = [d for d in dialogs if d.is_user]
            
        elif target_type == "contacts":
            contacts = await client.get_contacts()
            chats = [c for c in contacts]
            
        return chats

    async def prepare_message(self, client, mode):
        """Подготовка сообщения для отправки"""
        if mode == "text":
            return self.message_text.get("1.0", "end-1c")
            
        elif mode == "forward":
            try:
                chat_id, message_id = map(int, self.forward_entry.get().split(':'))
                message = await client.get_messages(chat_id, ids=message_id)
                return message
            except Exception as e:
                self.log(f"Ошибка при получении сообщения для пересылки: {str(e)}", "error")
                return None
                
        elif mode == "file":
            if self.message_file and os.path.exists(self.message_file):
                with open(self.message_file, 'r', encoding='utf-8') as f:
                    return f.read()
            return None
            
        elif mode == "photo":
            return {
                'text': self.message_text.get("1.0", "end-1c"),
                'photo': self.image_file
            }
            
        return None

    async def send_message(self, client, chat, message, mode):
        """Отправка сообщения"""
        try:
            if mode == "forward":
                await client.forward_messages(chat, message)
            elif mode == "photo":
                await client.send_file(
                    chat,
                    message['photo'],
                    caption=message['text'],
                    parse_mode='html'
                )
            else:
                await client.send_message(
                    chat,
                    message,
                    parse_mode='html'
                )
            return True
        except Exception as e:
            self.log(f"Ошибка при отправке: {str(e)}", "error")
            return False

    def start_sending(self):
        """Запуск рассылки"""
        mode = self.mode_var.get()
        target = self.target_var.get()
        
        try:
            min_delay = int(self.min_delay_var.get())
            max_delay = int(self.max_delay_var.get())
        except ValueError:
            self.log("Некорректные значения задержек", "error")
            return
            
        if not self.selected_clients:
            self.log("Выберите хотя бы один аккаунт", "error")
            return
            
        self.start_button.configure(state="disabled")
        
        # Запускаем рассылку
        asyncio.run_coroutine_threadsafe(
            self.send_messages(mode, target, min_delay, max_delay),
            self.loop
        )

    async def send_messages(self, mode, target, min_delay, max_delay):
        """Процесс рассылки"""
        try:
            for session_name in self.selected_clients:
                if session_name not in self.clients:
                    # Загружаем настройки прокси
                    proxy = None
                    try:
                        if os.path.exists('proxy_settings.json'):
                            with open('proxy_settings.json', 'r') as f:
                                proxy_settings = json.load(f)
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
                                elif os.path.exists('global_proxy.json'):
                                    with open('global_proxy.json', 'r') as f:
                                        global_proxy = json.load(f)
                                        if global_proxy['enabled'] and global_proxy['host'] and global_proxy['port']:
                                            proxy = {
                                                'proxy_type': global_proxy['type'],
                                                'addr': global_proxy['host'],
                                                'port': global_proxy['port'],
                                                'username': global_proxy['username'],
                                                'password': global_proxy['password']
                                            }
                    except:
                        pass
                        
                    client = TelegramClient(
                        os.path.join('sessions', f"{session_name}.session"),
                        '17349',
                        '344583e45741c457fe1862106095a5eb',
                        proxy=proxy
                    )
                    await client.connect()
                    if not await client.is_user_authorized():
                        self.log(f"Аккаунт {session_name} не авторизован", "error")
                        continue
                    self.clients[session_name] = client
                    
                client = self.clients[session_name]
                self.log(f"Начало рассылки через {session_name}")
                
                # Получаем сообщение
                message = await self.prepare_message(client, mode)
                if message is None:
                    self.log(f"Не удалось подготовить сообщение для {session_name}", "error")
                    continue
                    
                # Получаем целевые чаты
                chats = await self.get_target_chats(client, target)
                if not chats:
                    self.log(f"Нет доступных чатов для {session_name}", "warning")
                    continue
                    
                self.log(f"Начало рассылки через {session_name} ({len(chats)} чатов)")
                
                # Отправляем сообщения
                for i, chat in enumerate(chats, 1):
                    try:
                        name = getattr(chat, 'title', None) or getattr(chat, 'first_name', None) or "Неизвестный чат"
                        self.log(f"[{session_name}] Отправка в {name} ({i}/{len(chats)})")
                        
                        success = await self.send_message(client, chat, message, mode)
                        if success:
                            self.log(f"[{session_name}] Успешно отправлено в {name}", "success")
                        
                        # Случайная задержка
                        delay = random.uniform(min_delay, max_delay)
                        await asyncio.sleep(delay)
                    
                    except FloodWaitError as e:
                        wait_time = e.seconds + random.uniform(10, 30)
                        self.log(f"[{session_name}] Флуд-лимит, ожидание {wait_time} сек", "warning")
                        await asyncio.sleep(wait_time)
                    
                    except Exception as e:
                        self.log(f"[{session_name}] Ошибка при отправке в {name}: {str(e)}", "error")
                        await asyncio.sleep(random.uniform(min_delay, max_delay))
                    
                self.log(f"Рассылка через {session_name} завершена", "success")
            
        except Exception as e:
            self.log(f"Критическая ошибка: {str(e)}", "error")
            
        finally:
            self.start_button.configure(state="normal")

    def run(self):
        self.window.mainloop()

    def set_parent(self, parent_window):
        """Установка ссылки на родительское окно"""
        self.parent_window = parent_window

    def return_to_main(self):
        """Возврат в главное меню"""
        if self.parent_window:
            # Отключаем клиентов
            for client in self.clients.values():
                try:
                    future = asyncio.run_coroutine_threadsafe(
                        client.disconnect(),
                        self.loop
                    )
                    future.result()
                except:
                    pass
            
            # Останавливаем event loop
            self.loop.call_soon_threadsafe(self.loop.stop)
            
            # Показываем главное окно и закрываем текущее
            self.parent_window.deiconify()
            self.window.destroy()

    def on_closing(self):
        """Обработчик закрытия окна"""
        if self.parent_window:
            # Если есть родительское окно, возвращаемся в главное меню
            self.return_to_main()
        else:
            # Если родительского окна нет, закрываем приложение
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

if __name__ == "__main__":
    app = TelegramMassSender()
    app.run() 