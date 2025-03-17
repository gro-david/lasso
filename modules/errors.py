class ConfigError(Exception):
    def __init__(self, message):
        self.message = f"The config file is not valid. \n{message}"
        super().__init__(self.message)

class ShellError(ConfigError):
    def __init__(self):
        self.message = "The shell setting must exactly be either fish, zsh, bash or auto"
        super().__init__(self.message)
