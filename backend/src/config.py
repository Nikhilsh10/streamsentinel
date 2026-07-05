from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    KAFKA_BOOTSTRAP: str = "localhost:9092"
    FUSION_THRESHOLD: float = 0.65
    IF_WEIGHT: float = 0.6
    AE_WEIGHT: float = 0.4
    DB_PATH: str = "data/anomalies.db"
    
    class Config:
        env_file = ".env"

settings = Settings()
