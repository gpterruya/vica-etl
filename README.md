# vica-etl

ETL que extrai os documentos de adoção da **ZapSign**, normaliza os dados e publica um CSV no Cloud Storage, usado como fonte do dashboard da Vi.Ca no Looker Studio.

```
ZapSign API ──► extract ──► backup bruto (JSONL) ──► transform ──► CSV publicado
                                gs://vica-dashboard/backups/          gs://vica-dashboard/adocoes-teste.csv
```

## Como funciona

| Etapa | Código | O que faz |
|---|---|---|
| Extração | `extract/zapsign.py` | Pagina `GET /docs/` e busca o detalhe de cada documento (`GET /docs/{token}/`), com 3 tentativas por chamada. Cada resposta de formulário (`answers`) vira uma coluna, com o nome da variável em minúsculas. Respostas sem variável (nula, vazia ou só espaços) vão para `resposta_sem_variavel`. |
| Backup bruto | `load/storage.py` → `upload_raw_jsonl` | Salva o DataFrame extraído em `gs://vica-dashboard/backups/zapsign_raw_<timestamp>.jsonl`, um arquivo por execução. |
| Transformação | `transform/pipeline.py` | Normaliza data de nascimento, idade, estado, cidade, bairro, data de criação, espécie, raça, porte e faixa etária (`transform/transformations/`). |
| Publicação | `load/storage.py` → `upload_csv` | Grava o CSV (UTF-8 com BOM, separador `,`, datas `AAAA-MM-DD`) em `gs://vica-dashboard/adocoes-teste.csv`, sobrescrevendo o anterior. |

Uma execução completa leva cerca de **2h20** (cerca de 16,5 mil documentos).

## Infraestrutura (GCP)

Projeto `petin-418419`, região `southamerica-east1`.

| Recurso | Nome | Observação |
|---|---|---|
| Cloud Run Job | `etl-zapsign-job` | Roda `python main.py`. Tempo limite de 4h, sem novas tentativas. Imagem referenciada por digest. |
| Imagens | `southamerica-east1-docker.pkg.dev/petin-418419/cloud-run-source-deploy/etl-zapsign-job:<versão>` | Versão em produção: `v7`. |
| Cloud Scheduler | `etl-zapsign-diario` | Todo dia às 3h (`America/Sao_Paulo`), conta `etl-scheduler@petin-418419.iam.gserviceaccount.com` (só tem `roles/run.invoker` neste Job). |
| Cloud Storage | `gs://vica-dashboard` | CSV publicado e backups brutos. |
| Secret Manager | `zapsign-token` | Token da API ZapSign, exposto ao Job como `ZAPSIGN_TOKEN`. |
| Cloud Monitoring | `monitoring/*.json` | Alertas por e-mail: execução do Job falhou; agendamento não conseguiu disparar o Job. |

## Configuração

Variáveis de ambiente obrigatórias (`config.py`), lidas também de um `.env` local:

| Variável | Produção |
|---|---|
| `BASE_URL` | `https://api.zapsign.com.br/api/v1` |
| `ZAPSIGN_TOKEN` | secret `zapsign-token` |
| `BUCKET_NAME` | `vica-dashboard` |
| `OUTPUT_FILE` | `adocoes-teste.csv` |

## Dados pessoais

O CSV e os backups contêm dados de adotantes (CPF, RG, e-mail, telefone, endereço).

- **Nunca** coloque CSV, JSONL, PDF ou tarballs no repositório ou na imagem. `.gitignore`, `.gcloudignore` e `.dockerignore` já excluem esses arquivos; antes de um build, confira com `gcloud meta list-files-for-upload`.
- Em testes, imprima só contagens e nomes de colunas, nunca valores ou tokens.
- No Looker Studio, remova da fonte de dados os campos pessoais que o painel não usa e compartilhe o relatório só com quem precisa.
- Os backups brutos em `gs://vica-dashboard/backups/zapsign_raw_*` (um por execução, cerca de 106 MB cada) são apagados após 30 dias pela regra de ciclo de vida em `gcs/lifecycle-vica-dashboard.json`. Com o soft delete do bucket, ainda podem ser recuperados por mais 7 dias. A regra substitui toda a configuração de ciclo de vida do bucket; para alterá-la, edite o arquivo e aplique:
  ```bash
  gcloud storage buckets update gs://vica-dashboard --lifecycle-file=gcs/lifecycle-vica-dashboard.json
  ```

## Rodar e testar localmente

> **Atenção:** `python main.py` executa o ETL **real**: consulta a API ZapSign e sobrescreve o CSV publicado. Não rode localmente com as variáveis de produção.

Para testar transformações sem rede, use a imagem com `--network none` e chame só `transform`:

```bash
docker run --rm --network none --entrypoint python <imagem> -c "import pandas as pd; from transform.pipeline import transform; print(transform(pd.DataFrame([{'nome do animal': 'Rex'}])))"
```

## Publicar uma nova versão

1. Confira o que vai ser enviado (só código):
   ```bash
   gcloud meta list-files-for-upload
   ```
2. Build com uma tag nova:
   ```bash
   gcloud builds submit --project=petin-418419 --tag=southamerica-east1-docker.pkg.dev/petin-418419/cloud-run-source-deploy/etl-zapsign-job:vN
   ```
3. Verifique a imagem sem executar o ETL (sem dados em `/app`):
   ```bash
   docker run --rm --network none --entrypoint ls southamerica-east1-docker.pkg.dev/petin-418419/cloud-run-source-deploy/etl-zapsign-job:vN -la /app
   ```
4. Anote o digest e aponte o Job para ele:
   ```bash
   gcloud artifacts docker images describe southamerica-east1-docker.pkg.dev/petin-418419/cloud-run-source-deploy/etl-zapsign-job:vN --format="value(image_summary.digest)"
   ```
   ```bash
   gcloud run jobs update etl-zapsign-job --region=southamerica-east1 --project=petin-418419 --image=southamerica-east1-docker.pkg.dev/petin-418419/cloud-run-source-deploy/etl-zapsign-job@sha256:<digest>
   ```
5. Se a mudança puder alterar o CSV, guarde uma cópia do CSV publicado antes da próxima execução e compare depois (linhas, colunas e valores por `token`).

**Rollback:** repita o passo 4 com o digest da versão anterior.

### Dependências fixadas

`requirements.txt` (pip freeze completo) e a imagem base do `Dockerfile` (tag + digest) estão fixados para que um build novo não mude o CSV sem aviso. Para atualizar, altere as versões, faça o build e compare o CSV gerado com o atual antes de apontar o Job para a imagem nova.

## Operação

Executar manualmente (cerca de 2h20, sobrescreve o CSV):

```bash
gcloud run jobs execute etl-zapsign-job --region=southamerica-east1 --project=petin-418419 --wait
```

Ver as últimas execuções:

```bash
gcloud run jobs executions list --job=etl-zapsign-job --region=southamerica-east1 --project=petin-418419 --limit=5
```

Pausar ou retomar o agendamento:

```bash
gcloud scheduler jobs pause etl-zapsign-diario --location=southamerica-east1 --project=petin-418419
```

```bash
gcloud scheduler jobs resume etl-zapsign-diario --location=southamerica-east1 --project=petin-418419
```

Testar o alerta de falha (falha em segundos, sem chamar a API nem gravar o CSV):

```bash
gcloud run jobs execute etl-zapsign-job --region=southamerica-east1 --project=petin-418419 --args="-c,raise SystemExit(1)"
```

## Particularidades do CSV

- **Colunas dinâmicas:** as colunas vêm das variáveis dos modelos da ZapSign. Criar, renomear ou apagar uma variável num modelo adiciona ou remove colunas; no Looker Studio, use **Atualizar campos** na fonte de dados.
- **`resposta_sem_variavel`:** guarda a primeira resposta sem variável de cada documento. Mistura respostas de perguntas diferentes.
- **Idade e faixa etária** são calculadas com a data da execução, então mudam de um dia para o outro mesmo sem dados novos.
- **Documentos com erro:** se o detalhe de um documento falhar depois das 3 tentativas, ele é registrado no log e fica fora do CSV daquela execução. A execução continua e termina com sucesso, então isso **não** dispara o alerta de falha.
- **Token repetido:** a listagem da API pode trazer o mesmo documento duas vezes; não trate `token` como chave única sem verificar.
