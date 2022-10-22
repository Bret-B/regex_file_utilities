class Settings:
    modes = ['rename', 'delete', 'move', 'copy']
    file_modes = ['files', 'folders', 'both']

    def __init__(self):
        self.recursive = False
        self.skip_errors = False
        self.mode = Settings.modes[0]
        self.file_mode = Settings.file_modes[0]
