import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

class Logger:
    def __init__(self):
        self.log_dir = "logs"
        os.makedirs(self.log_dir, exist_ok=True)
        
        self.logger = logging.getLogger('TelegramTools')
        self.logger.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler = RotatingFileHandler(
            os.path.join(self.log_dir, 'app.log'),
            maxBytes=5*1024*1024,
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.error_logger = logging.getLogger('TelegramTools.errors')
        self.error_logger.setLevel(logging.ERROR)
        
        error_handler = RotatingFileHandler(
            os.path.join(self.log_dir, 'errors.log'),
            maxBytes=5*1024*1024,
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self.error_logger.addHandler(error_handler)
        
    def log_error(self, error, context=None):
        error_msg = f"Error: {str(error)}"
        if context:
            error_msg = f"{error_msg} | Context: {context}"
        self.error_logger.error(error_msg)
        
    def log_info(self, message):
        self.logger.info(message)
        
    def log_warning(self, message):
        self.logger.warning(message)
        
    def log_debug(self, message):
        self.logger.debug(message)
        
    def get_recent_errors(self, count=10):
        errors = []
        try:
            with open(os.path.join(self.log_dir, 'errors.log'), 'r') as f:
                lines = f.readlines()
                return lines[-count:]
        except:
            return []
            
    def clear_logs(self):
        try:
            for filename in os.listdir(self.log_dir):
                filepath = os.path.join(self.log_dir, filename)
                if os.path.isfile(filepath):
                    file_time = datetime.fromtimestamp(os.path.getctime(filepath))
                    if (datetime.now() - file_time).days > 30:
                        os.remove(filepath)
        except Exception as e:
            self.log_error(f"Error clearing logs: {str(e)}")
            
    def export_logs(self, start_date=None, end_date=None):
        try:
            export_file = os.path.join(
                self.log_dir,
                f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            )
            
            with open(os.path.join(self.log_dir, 'app.log'), 'r') as source:
                with open(export_file, 'w') as target:
                    for line in source:
                        try:
                            log_date = datetime.strptime(line[:19], '%Y-%m-%d %H:%M:%S')
                            if start_date and log_date < start_date:
                                continue
                            if end_date and log_date > end_date:
                                continue
                            target.write(line)
                        except:
                            continue
                            
            return export_file
            
        except Exception as e:
            self.log_error(f"Error exporting logs: {str(e)}")
            return None 