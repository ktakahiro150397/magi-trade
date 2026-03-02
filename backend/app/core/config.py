from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # MySQL
    MYSQL_HOST: str = "db"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "magi"
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = "magi_trade"

    # Hyperliquid
    HL_WALLET_ADDRESS: str = ""
    HL_PRIVATE_KEY: str = ""

    # LLM API (direct API access)
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""

    # LLM backend selection
    # Supported: copilot_cli | claude_code_cli | codex_cli | gemini_cli | mock
    LLM_BACKEND: str = "mock"

    # GitHub Copilot CLI authentication (fine-grained PAT with "Copilot Requests" permission)
    GH_TOKEN: str = ""

    # LLM CLI subprocess timeout (seconds)
    LLM_TIMEOUT: float = 120.0

    # Trading parameters
    RISK_PERCENT: float = 1.0
    DEFAULT_LEVERAGE: int = 5
    MAX_HOLD_HOURS: int = 24

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
        )

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return (
            f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
        )


settings = Settings()
