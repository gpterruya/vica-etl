import logging

import functions_framework

from extract.zapsign import extract
from transform.pipeline import transform
from load.storage import upload_csv, upload_raw_jsonl


def run() -> dict:
    """
    Executa o fluxo completo do ETL.
    """

    logging.info("Iniciando extração dos dados...")

    df = extract()
    if df is None:
        raise ValueError("A extração não retornou um DataFrame.")

    logging.info("Extração concluída. Linhas extraídas: %s", len(df))

    logging.info("Salvando backup bruto no Cloud Storage...")
    raw_backup_result = upload_raw_jsonl(df)
    logging.info("Backup bruto concluído: %s", raw_backup_result["uri"])

    logging.info("Iniciando transformação...")
    df = transform(df)

    if df is None:
        raise ValueError("A transformação não retornou um DataFrame.")

    logging.info(
        "Transformação concluída. Linhas finais: %s",
        len(df),
    )

    upload_result = upload_csv(df)

    return {
        "rows_processed": len(df),
        "raw_backup": raw_backup_result,
        "upload": upload_result,
    }


@functions_framework.http
def vica_etl(request):
    """
    Entry point HTTP chamado pelo Cloud Scheduler.
    """

    if request.method != "POST":
        return {
            "success": False,
            "message": "Método não permitido. Utilize POST.",
        }, 405

    try:
        logging.info("Iniciando VICA ETL.")

        result = run()

        logging.info("VICA ETL finalizado com sucesso.")

        return {
            "success": True,
            "message": "ETL executado com sucesso.",
            "result": result,
        }, 200

    except Exception:
        logging.exception("Erro durante a execução do VICA ETL.")

        return {
            "success": False,
            "message": "Erro durante a execução do ETL.",
        }, 500


if __name__ == "__main__":
    result = run()
    print(result)