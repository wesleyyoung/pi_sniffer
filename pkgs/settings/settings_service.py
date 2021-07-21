refresh_data_rate = 'refresh_data_rate'
refresh_screen_rate = 'refresh_screen_rate'


class SettingsService:

    def __init__(self):
        self.settings = dict()
        self.set_defaults()

    def set_defaults(self):
        self.set_data_rate(10)
        self.set_refresh_rate(1500)

    def set_setting(self, key, value):
        self.settings[key] = value

    def get_setting(self, key):
        return self.settings[key]

    def set_data_rate(self, rate):
        self.set_setting(refresh_data_rate, rate)

    def get_data_rate(self):
        return self.get_setting(refresh_data_rate)

    def set_refresh_rate(self, rate):
        self.set_setting(refresh_screen_rate, rate)

    def get_refresh_rate(self):
        return self.get_setting(refresh_screen_rate)
