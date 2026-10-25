import os
import requests
import pandas as pd
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_fixed
import logging
from config import BASE_URL, ZAPSIGN_TOKEN

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

HEADERS = {
    "Authorization": f"Bearer {ZAPSIGN_TOKEN}",
    "Content-Type": "application/json"
}


# ---------------- API ---------------- #

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def get_docs_page(url):
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def get_doc_detail(token):
    url = f"{BASE_URL}/docs/{token}/"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()


# ---------------- EXTRACT ---------------- #

def extract():
    url = f"{BASE_URL}/docs/"
    page = 1

    rows = []

    while url:
        logging.info(f"Processando página {page}")

        data = get_docs_page(url)

        for doc in data.get("results", []):
            token = doc.get("token")
            logging.info(f"Processando documento {token}")

            try:
                detail = get_doc_detail(token)

                base = {
                    "token": detail.get("token"),
                    "name": detail.get("name"),
                    "status": detail.get("status"),
                    "created_at": detail.get("created_at"),
                    "folder_path": detail.get("folder_path"),
                }

                # Primeiro assinante (caso exista)
                signers = detail.get("signers") or []
                signer = signers[0] if signers else {}

                base.update({
                    "signer_name": signer.get("name"),
                    "signer_email": signer.get("email"),
                    "signer_phone": signer.get("phone"),
                    "signed_at": signer.get("signed_at"),
                    "geo_lat": signer.get("geo_latitude"),
                    "geo_lng": signer.get("geo_longitude"),
                })

                
                # Campos dinâmicos
                for answer in detail.get("answers") or []:
                    variable = answer.get("variable")
                    value = answer.get("value")

                    if variable and variable.strip():
                        col_name = variable.strip().lower()
                        base[col_name] = value
                    else:
                        # Preserva respostas cuja variável não foi identificada
                        if "resposta_sem_variavel" not in base:
                            base["resposta_sem_variavel"] = value
                        elif base["resposta_sem_variavel"] is None:
                            base["resposta_sem_variavel"] = value


                rows.append(base)

            except Exception as e:
                logging.exception(f"Erro ao processar documento {token}")

        url = data.get("next")
        page += 1

    logging.info(f"ETL finalizado. {len(rows)} documentos carregados.")

    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = extract()
    logging.info(df.head())