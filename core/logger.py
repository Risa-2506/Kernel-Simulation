import datetime

class Logger:
    logs = []

    @staticmethod
    def log(message: str, category: str = "default"):
        """
        Logs a message with a timestamp and category.
        Categories: default, success, waiting, scheduling, termination, error
        """
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        Logger.logs.append({
            "timestamp": timestamp,
            "message": message,
            "category": category
        })

    @staticmethod
    def get_logs():
        return Logger.logs

    @staticmethod
    def clear_logs():
        Logger.logs = []
