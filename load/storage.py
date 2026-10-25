
import logging
import tempfile
from datetime import datetime, timezone

from google.cloud import storage

from config import BUCKET_NAME, OUTPUT_FILE


def upload_csv(df) -> dict:
    """
    Gera um CSV em memória e envia para o Cloud Storage.
    """

    if not BUCKET_NAME:
        raise ValueError("BUCKET_NAME não configurado.")

    if not OUTPUT_FILE:
        raise ValueError("OUTPUT_FILE não configurado.")

    if df is None:
        raise ValueError("DataFrame não informado.")

    logging.info(
        "Gerando CSV em memória. Linhas: %s | Colunas: %s",
        len(df),
        len(df.columns),
    )

    import io

    csv_buffer = io.StringIO()

    df.to_csv(
        csv_buffer,
        index=False,
        sep=",",
        date_format="%Y-%m-%d",
    )

    # Adiciona BOM para melhorar a compatibilidade com Excel.
    csv_content = "\ufeff" + csv_buffer.getvalue()

    logging.info("Conectando ao Cloud Storage...")

    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(OUTPUT_FILE)

    logging.info(
        "Enviando gs://%s/%s...",
        BUCKET_NAME,
        OUTPUT_FILE,
    )

    blob.upload_from_string(
        csv_content,
        content_type="text/csv; charset=utf-8",
    )

    logging.info("Upload concluído: gs://%s/%s", BUCKET_NAME, OUTPUT_FILE)

    return {
        "bucket": BUCKET_NAME,
        "file": OUTPUT_FILE,
        "uri": f"gs://{BUCKET_NAME}/{OUTPUT_FILE}",
        "rows": len(df),
    }


def upload_raw_jsonl(df) -> dict:
    """
    Salva os dados brutos em JSON Lines usando arquivo temporário
    e serialização em blocos para reduzir o consumo de memória.
    Cada execução gera um arquivo independente.
    """

    if not BUCKET_NAME:
        raise ValueError("BUCKET_NAME não configurado.")

    if df is None:
        raise ValueError("DataFrame bruto não informado.")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    raw_file = f"backups/zapsign_raw_{timestamp}.jsonl"

    logging.info(
        "Gerando backup bruto em blocos. Linhas: %s | Colunas: %s",
        len(df),
        len(df.columns),
    )

    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(raw_file)

    rows_per_chunk = 500

    
    with tempfile.TemporaryDirectory() as temp_dir:
        import os

        temp_path = os.path.join(temp_dir, "backup.jsonl")

        with open(temp_path, "w", encoding="utf-8", newline="") as temp_file:
            for start in range(0, len(df), rows_per_chunk):
                end = min(start + rows_per_chunk, len(df))
                chunk = df.iloc[start:end]

                jsonl_chunk = chunk.to_json(
                    orient="records",
                    lines=True,
                    force_ascii=False,
                    date_format="iso",
                )

                temp_file.write(jsonl_chunk)
                if jsonl_chunk and not jsonl_chunk.endswith("\n"):
                    temp_file.write("\n")

                logging.info(
                    "Backup bruto serializado: %s/%s linhas",
                    end,
                    len(df),
                )

        logging.info(
            "Enviando backup bruto para gs://%s/%s...",
            BUCKET_NAME,
            raw_file,
        )

        blob.upload_from_filename(
            temp_path,
            content_type="application/x-ndjson; charset=utf-8",
        )


    logging.info(
        "Backup bruto salvo: gs://%s/%s",
        BUCKET_NAME,
        raw_file,
    )

    return {
        "bucket": BUCKET_NAME,
        "file": raw_file,
        "uri": f"gs://{BUCKET_NAME}/{raw_file}",
        "rows": len(df),
    }
