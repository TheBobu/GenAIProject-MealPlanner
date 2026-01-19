from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    groq_api_key: str 
    google_api_key: str 
    mistral_api_key: str
    uv_link_mode:str
    serper_api_key:str
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
