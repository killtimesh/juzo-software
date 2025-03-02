import customtkinter as ctk
from modules.mass_sender import TelegramMassSender
from modules.parser import TelegramParser
from modules.inviter import TelegramInviter
from modules.account_manager import AccountManager
from modules.account_warmer import TelegramAccountWarmer
from config.logger import Logger
import threading

class TelegramToolsApp:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Juzo software")
        self.window.geometry("800x600")
        self.window.resizable(False, False)
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.current_module = None
        self.logger = Logger()
        
        self.setup_ui()
            
    def setup_ui(self):
        main_container = ctk.CTkFrame(self.window, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=30, pady=20)
        
        header_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 30))
        
        logo_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        logo_frame.pack(side="left")
        
        ctk.CTkLabel(
            logo_frame,
            text="Juzo",
            font=("Arial", 32, "bold"),
            text_color="#1DA1F2"
        ).pack(side="left")
        
        ctk.CTkLabel(
            logo_frame,
            text="software",
            font=("Arial", 32, "bold")
        ).pack(side="left", padx=(5, 0))
        
        account_button = ctk.CTkButton(
            header_frame,
            text="⚙️ Управление аккаунтами",
            command=self.open_account_manager,
            width=200,
            height=32
        )
        account_button.pack(side="left", padx=20)
        
        ctk.CTkLabel(
            main_container,
            text="Выберите нужный инструмент:",
            font=("Arial", 16)
        ).pack(pady=(0, 20))
        
        cards_container = ctk.CTkFrame(main_container, fg_color="transparent")
        cards_container.pack(fill="both", expand=True, padx=20)
        
        functions = [
            {
                "name": "Массовая рассылка",
                "description": "Отправка сообщений через несколько аккаунтов",
                "command": self.open_mass_sender,
                "icon": "📨",
                "color": "#FF6B6B"
            },
            {
                "name": "Парсер участников",
                "description": "Сбор информации об участниках групп и чатов",
                "command": self.open_parser,
                "icon": "📊",
                "color": "#4ECDC4"
            },
            {
                "name": "Инвайтер",
                "description": "Автоматическое приглашение пользователей в группы",
                "command": self.open_inviter,
                "icon": "👥",
                "color": "#45B7D1"
            },
            {
                "name": "Прогрев аккаунтов",
                "description": "Автоматическая имитация активности в Telegram",
                "command": self.open_account_warmer,
                "icon": "🔥",
                "color": "#FFB347"
            }
        ]
        
        for i in range(2):
            cards_container.grid_rowconfigure(i, weight=1)
        for i in range(2):
            cards_container.grid_columnconfigure(i, weight=1)
            
        for i, func in enumerate(functions):
            row = i // 2
            col = i % 2
            
            card = ctk.CTkFrame(cards_container)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            content_frame = ctk.CTkFrame(card, fg_color="transparent")
            content_frame.pack(fill="both", expand=True, padx=15, pady=15)
            
            header_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            header_frame.pack(fill="x")
            
            icon = ctk.CTkLabel(
                header_frame,
                text=func["icon"],
                font=("Arial", 28)
            )
            icon.pack(side="left")
            
            name = ctk.CTkLabel(
                header_frame,
                text=func["name"],
                font=("Arial", 16, "bold")
            )
            name.pack(side="left", padx=10)
            
            description = ctk.CTkLabel(
                content_frame,
                text=func["description"],
                font=("Arial", 12),
                wraplength=200,
                justify="left"
            )
            description.pack(fill="x", pady=(10, 0))
            
            def on_enter(e, card=card, color=func["color"]):
                card.configure(fg_color=color)
                
            def on_leave(e, card=card):
                card.configure(fg_color=("gray86", "gray17"))
                
            def on_click(e, cmd=func["command"]):
                cmd()
                
            for widget in [card, content_frame, header_frame, icon, name, description]:
                widget.bind("<Enter>", on_enter)
                widget.bind("<Leave>", on_leave)
                widget.bind("<Button-1>", on_click)
        
        footer = ctk.CTkLabel(
            main_container,
            text="© 2024 Juzo software",
            font=("Arial", 12),
            text_color="gray"
        )
        footer.pack(pady=(20, 0))
    
    def open_module(self, ModuleClass):
        self.window.withdraw()
        self.current_module = ModuleClass()
        self.current_module.set_parent(self.window)
        self.current_module.run()
    
    def on_module_close(self):
        if self.current_module:
            self.current_module.window.destroy()
            self.current_module = None
        self.window.deiconify()
    
    def open_mass_sender(self):
        self.open_module(TelegramMassSender)
    
    def open_parser(self):
        self.open_module(TelegramParser)
    
    def open_inviter(self):
        self.open_module(TelegramInviter)
    
    def open_account_manager(self):
        self.open_module(AccountManager)
        
    def open_account_warmer(self):
        self.open_module(TelegramAccountWarmer)
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = TelegramToolsApp()
    app.run() 