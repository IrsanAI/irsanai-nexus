from pathlib import Path
from tempfile import gettempdir

from pydantic import Field
from pydantic_settings import SettingsConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    app_name: str = 'irsanai-nexus-repo'
    app_version: str = '0.1.0'
    debug: bool = False
    work_dir: Path = Field(default_factory=lambda: Path(gettempdir()) / 'irsanai-nexus-work')
    reports_dir: Path = Path('./reports_output')
    db_path: Path = Path('./repo_intel.db')
    host: str = '0.0.0.0'
    port: int = 8000
    openai_api_key: str = ''
    anthropic_api_key: str = ''


settings = Settings()
