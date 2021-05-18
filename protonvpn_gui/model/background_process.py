import threading


class BackgroundProcess:
    def __init__(self):
        self.process = None

    @staticmethod
    def setup(target_method, *args, **kwargs):
        bg_process = BackgroundProcess()
        bg_process.process = threading.Thread(
            target=target_method, args=args, kwargs=kwargs
        )
        bg_process.process.daemon = True
        return bg_process

    def start(self):
        self.process.start()
