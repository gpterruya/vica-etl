import os

from dotenv import load_dotenv


load_dotenv()


def required_env(name: str) -> str:
    value = os.getenv(name)

    if not value or not value.strip():
        raise RuntimeError(
            f"Variável de ambiente obrigatória não configurada: {name}"
        )

    return value.strip()


BASE_URL = required_env("BASE_URL")
ZAPSIGN_TOKEN = required_env("ZAPSIGN_TOKEN")
BUCKET_NAME = required_env("BUCKET_NAME")
OUTPUT_FILE = required_env("OUTPUT_FILE")