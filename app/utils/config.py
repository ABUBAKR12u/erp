from pydantic_settings import BaseSettings , SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env" , extra="ignore")

    DB_USERNAME : str
    DB_PASS : str
    DB_NAME :str
    SECRET_KEY : str
    ALGORITHM : str




settings = Settings()