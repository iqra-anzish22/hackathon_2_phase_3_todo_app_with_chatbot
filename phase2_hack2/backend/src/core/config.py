"""
Configuration management for the application.
Loads environment variables and provides settings.
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # JWT Configuration (REQUIRED)
    BETTER_AUTH_SECRET: str

    # Database Configuration (REQUIRED)
    DATABASE_URL: str

    # CORS Configuration (REQUIRED)
    CORS_ORIGINS: str

    # Application Settings (OPTIONAL with defaults)
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS_ORIGINS string to list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Initialize settings
try:
    settings = Settings()
except Exception as e:
    print("\n" + "="*80)
    print("[ERROR] CONFIGURATION ERROR: Failed to load environment variables")
    print("="*80)
    print(f"\nError: {str(e)}")
    print("\n[INFO] Make sure you have a .env file in the backend/ directory")
    print("[INFO] Required variables: BETTER_AUTH_SECRET, DATABASE_URL, CORS_ORIGINS")
    print("="*80 + "\n")
    raise
