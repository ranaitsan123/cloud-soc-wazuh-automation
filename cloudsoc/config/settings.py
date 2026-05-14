"""Settings and configuration management"""

import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv


class AWSConfig(BaseModel):
    """AWS configuration"""
    access_key_id: str = Field(default="")
    secret_access_key: str = Field(default="")
    region: str = Field(default="eu-north-1")
    profile: Optional[str] = Field(default=None)

    class Config:
        """Pydantic config"""
        extra = "allow"


class TerraformConfig(BaseModel):
    """Terraform configuration"""
    dir: Path = Field(default=Path("terraform"))
    auto_approve: bool = Field(default=False)
    var_files: list = Field(default_factory=list)

    class Config:
        """Pydantic config"""
        extra = "allow"


class ProjectConfig(BaseModel):
    """Project configuration"""
    name: str = Field(default="cloud-soc")
    tag: str = Field(default="cloud-soc")
    environment: str = Field(default="dev")
    aws: AWSConfig = Field(default_factory=AWSConfig)
    terraform: TerraformConfig = Field(default_factory=TerraformConfig)

    class Config:
        """Pydantic config"""
        extra = "allow"


class Settings(BaseModel):
    """Global settings"""
    project: ProjectConfig = Field(default_factory=ProjectConfig)
    log_level: str = Field(default="INFO")
    debug: bool = Field(default=False)

    class Config:
        """Pydantic config"""
        extra = "allow"


def load_settings() -> Settings:
    """
    Load settings from environment variables and .env file.

    Returns:
        Settings instance
    """
    # Load .env file if it exists
    env_file = Path(".env")
    if env_file.exists():
        load_dotenv(env_file)

    # Extract AWS credentials and config from environment
    aws_config = AWSConfig(
        access_key_id=os.getenv("AWS_ACCESS_KEY_ID", ""),
        secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", ""),
        region=os.getenv("AWS_DEFAULT_REGION", "eu-north-1"),
        profile=os.getenv("AWS_PROFILE", None),
    )

    # Extract project config
    project_config = ProjectConfig(
        name=os.getenv("PROJECT_NAME", "cloud-soc"),
        tag=os.getenv("PROJECT_TAG", "cloud-soc"),
        environment=os.getenv("ENVIRONMENT", "dev"),
        aws=aws_config,
        terraform=TerraformConfig(
            dir=Path(os.getenv("TERRAFORM_DIR", "terraform"))
        )
    )

    # Create settings instance
    settings = Settings(
        project=project_config,
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        debug=os.getenv("DEBUG", "false").lower() == "true",
    )

    return settings


# Global settings instance
settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create global settings instance"""
    global settings
    if settings is None:
        settings = load_settings()
    return settings
