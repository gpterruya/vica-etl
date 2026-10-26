import os
import sys
from pathlib import Path

# Valores falsos: os testes nunca chamam a API ZapSign nem o Cloud Storage.
# Atribuição direta para que um .env local com valores reais não seja usado.
os.environ["BASE_URL"] = "https://zapsign.invalid/api/v1"
os.environ["ZAPSIGN_TOKEN"] = "token-de-teste"
os.environ["BUCKET_NAME"] = "bucket-de-teste"
os.environ["OUTPUT_FILE"] = "saida-de-teste.csv"

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
