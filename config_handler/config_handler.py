import os


class ConfigHandler:
    _instance = None
    local_dev = 0

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ConfigHandler, cls).__new__(cls)
            try:
                cls.local_dev = os.getenv('LOCAL_DEV')
                print(f'config_handler Created. local_dev: {cls.local_dev}')
            except Exception as e:
                print(f'config_handler Error: {e}')

        return cls._instance

    def is_local_dev(self):
        return self.local_dev == '1'
