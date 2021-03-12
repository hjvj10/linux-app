import threading


class BackgroundProcess:
    def __init__(self):
        self.process = None

    @staticmethod
    def setup_no_params(target_method):
        bg_process = BackgroundProcess()
        bg_process.process = threading.Thread(
            target=target_method,
        )
        bg_process.process.daemon = True
        return bg_process

    @staticmethod
    def setup_with_args(target_method, args):
        bg_process = BackgroundProcess()
        bg_process.process = threading.Thread(
            target=target_method, args=args
        )
        bg_process.process.daemon = True
        return bg_process

    def start(self):
        self.process.start()
