import os


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    DB_NAME = os.getenv('DATABASE')
    WEATHER_API_ID = os.getenv('WEATHER_API_ID')
    URL_COUNTRY_CODES_JSON = os.getenv('URL_COUNTRY_CODES_JSON')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
}
