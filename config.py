# # config.py

from pydantic import SecretStr, StrictStr
from pydantic_settings import BaseSettings
# from dotenv import find_dotenv, load_dotenv

# if not find_dotenv():  # searches for .env
#     exit("Переменные окружения не загружены, так как отсутствует файл .env")
# else:
#     load_dotenv()  # reads it and defines the environmental variables atp


class AppSettings(BaseSettings):
    site_api: SecretStr  # Automatically gets value from SITE_API env variable
    host_api: StrictStr  # Automatically gets value from HOST_API env variable
    bot_token: SecretStr

    class Config:
        env_file = '.env'  # Specifies that environment variables should be loaded from .env
        env_file_encoding = 'utf-8'
        extra = "ignore"  # This tells Pydantic to ignore any extra fields in the .env file
