import os
import asyncio
import random
from telethon import TelegramClient, functions, types
import customtkinter as ctk
import threading
from datetime import datetime
import json

class TelegramAccountWarmer:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Прогрев аккаунтов")
        self.window.geometry("900x700")
        
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self.thread.start()
        
        self.clients = {}
        self.selected_clients = set()
        self.parent_window = None
        self.warming_active = False
        
        self.setup_ui()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def _run_event_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
        
    def setup_ui(self):
        # Верхняя панель с кнопкой возврата
        top_panel = ctk.CTkFrame(self.window)
        top_panel.pack(fill="x", padx=20, pady=10)
        
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
            text="Прогрев аккаунтов",
            font=("Arial", 24, "bold")
        ).pack(pady=10)
        
        # Основной контейнер
        main_container = ctk.CTkFrame(self.window)
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Левая панель - настройки
        settings_frame = ctk.CTkFrame(main_container)
        settings_frame.pack(side="left", fill="both", padx=10, pady=10, expand=True)
        
        # Выбор режима прогрева
        mode_frame = ctk.CTkFrame(settings_frame)
        mode_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            mode_frame,
            text="Режим прогрева:",
            font=("Arial", 14, "bold")
        ).pack(pady=5)
        
        self.mode_var = ctk.StringVar(value="safe")
        
        ctk.CTkRadioButton(
            mode_frame,
            text="Безопасный режим",
            value="safe",
            variable=self.mode_var
        ).pack(pady=2)
        
        ctk.CTkLabel(
            mode_frame,
            text="• Просмотр каналов\n• Чтение сообщений\n• Минимальная активность",
            font=("Arial", 12),
            justify="left"
        ).pack(pady=2, padx=20)
        
        ctk.CTkRadioButton(
            mode_frame,
            text="Полный режим",
            value="full",
            variable=self.mode_var
        ).pack(pady=2)
        
        ctk.CTkLabel(
            mode_frame,
            text="• Все действия безопасного режима\n• Отправка сообщений\n• Реакции на посты\n• Подписка на каналы",
            font=("Arial", 12),
            justify="left"
        ).pack(pady=2, padx=20)
        
        # Настройки задержек
        delay_frame = ctk.CTkFrame(settings_frame)
        delay_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            delay_frame,
            text="Задержки между действиями (сек):",
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
        
        self.max_delay_var = ctk.StringVar(value="120")
        ctk.CTkEntry(
            max_delay_frame,
            textvariable=self.max_delay_var,
            width=70
        ).pack(side="right", padx=5)
        
        # Правая панель - аккаунты и лог
        right_panel = ctk.CTkFrame(main_container)
        right_panel.pack(side="right", fill="both", padx=10, pady=10, expand=True)
        
        # Список аккаунтов
        accounts_frame = ctk.CTkFrame(right_panel)
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
            right_panel,
            text="Начать прогрев",
            command=self.toggle_warming,
            font=("Arial", 14, "bold"),
            height=40
        )
        self.start_button.pack(pady=10)
        
        # Лог
        log_frame = ctk.CTkFrame(right_panel)
        log_frame.pack(fill="both", expand=True, pady=10)
        
        ctk.CTkLabel(
            log_frame,
            text="Лог действий:",
            font=("Arial", 14, "bold")
        ).pack(pady=5)
        
        self.log_text = ctk.CTkTextbox(log_frame)
        self.log_text.pack(fill="both", expand=True)
        
        # Инициализируем клиентов
        self.init_clients()
        
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
        
    def toggle_warming(self):
        """Переключение процесса прогрева"""
        if not self.warming_active:
            try:
                min_delay = int(self.min_delay_var.get())
                max_delay = int(self.max_delay_var.get())
            except ValueError:
                self.log("Некорректные значения задержек", "error")
                return
                
            if not self.selected_clients:
                self.log("Выберите хотя бы один аккаунт", "error")
                return
                
            self.warming_active = True
            self.start_button.configure(text="Остановить прогрев", fg_color="red")
            
            # Запускаем прогрев
            asyncio.run_coroutine_threadsafe(
                self.warm_accounts(
                    self.mode_var.get(),
                    min_delay,
                    max_delay
                ),
                self.loop
            )
        else:
            self.warming_active = False
            self.start_button.configure(text="Начать прогрев", fg_color=["#3a7ebf", "#1f538d"])
            
    async def warm_accounts(self, mode, min_delay, max_delay):
        """Процесс прогрева аккаунтов"""
        try:
            for session_name in self.selected_clients:
                if not self.warming_active:
                    break
                    
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
                self.log(f"Начало прогрева аккаунта {session_name}")
                
                while self.warming_active:
                    try:
                        # Получаем диалоги
                        dialogs = await client.get_dialogs()
                        channels = [d for d in dialogs if d.is_channel]
                        
                        if not channels:
                            self.log(f"Нет доступных каналов для {session_name}", "warning")
                            break
                            
                        # Случайный канал
                        channel = random.choice(channels)
                        
                        # Читаем сообщения
                        messages = await client.get_messages(channel, limit=10)
                        for msg in messages:
                            if not self.warming_active:
                                break
                                
                            # Имитируем чтение
                            await client.send_read_acknowledge(channel, max_id=msg.id)
                            self.log(f"[{session_name}] Просмотрено сообщение в {channel.title}")
                            
                            if mode == "full":
                                # Добавляем реакцию с небольшой вероятностью
                                if random.random() < 0.3:
                                    try:
                                        await client(functions.messages.SendReactionRequest(
                                            peer=channel,
                                            msg_id=msg.id,
                                            reaction=[types.ReactionEmoji(emoticon="👍")]
                                        ))
                                        self.log(f"[{session_name}] Добавлена реакция в {channel.title}")
                                    except:
                                        pass
                                        
                            await asyncio.sleep(random.uniform(min_delay/2, max_delay/2))
                            
                        if mode == "full":
                            # Поиск новых каналов
                            try:
                                results = await client(functions.contacts.SearchRequest(
                                    q=random.choice(["news", "crypto", "tech", "music"]),
                                    limit=5
                                ))
                                
                                for chat in results.chats:
                                    if not self.warming_active:
                                        break
                                        
                                    if random.random() < 0.2:  # 20% шанс подписки
                                        try:
                                            await client(functions.channels.JoinChannelRequest(chat))
                                            self.log(f"[{session_name}] Подписка на канал {chat.title}")
                                            await asyncio.sleep(random.uniform(min_delay, max_delay))
                                        except:
                                            pass
                            except:
                                pass
                                
                        # Задержка между циклами
                        await asyncio.sleep(random.uniform(min_delay*2, max_delay*2))
                        
                    except Exception as e:
                        self.log(f"[{session_name}] Ошибка: {str(e)}", "error")
                        await asyncio.sleep(random.uniform(min_delay, max_delay))
                        
        except Exception as e:
            self.log(f"Критическая ошибка: {str(e)}", "error")
            
        finally:
            self.warming_active = False
            self.start_button.configure(text="Начать прогрев", fg_color=["#3a7ebf", "#1f538d"])
            
    def run(self):
        self.window.mainloop()
        
    def set_parent(self, parent_window):
        """Установка ссылки на родительское окно"""
        self.parent_window = parent_window
        
    def return_to_main(self):
        """Возврат в главное меню"""
        self.warming_active = False
        
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
        self.warming_active = False
        
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

if __name__ == "__main__":
    app = TelegramAccountWarmer()
    app.run() 