import requests
import datetime
import boto3
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def download_pages(event, context):
    """
    Descarga 10 páginas de Mitula y sube .html al bucket
    'dlandingcasas-mitula'.Al final, crea un archivo 'ready.txt' para disparar
    la Lambda que genera el
    CSV.
    """
    s3 = boto3.client("s3")
    bucket_html = "dlandingcasas-mitula"  # Ajusta con tu bucket

    today = datetime.datetime.now().strftime('%Y-%m-%d')
    base_url = (
        "https://casas.mitula.com.co/find?"
        "operationType=sell&propertyType=apartment"
        "&geoId=mitula-CO-poblacion-0000014156"
        "&text=Bogot%C3%A1%2C++%28Cundinamarca%29"
    )

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/98.0.4758.102 Safari/537.36"
        ),
        "Accept-Language": "es-ES,es;q=0.9",
    }
    session = requests.Session()
    session.headers.update(headers)

    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    for page in range(1, 11):
        url = f"{base_url}&page={page}"
        response = session.get(url, timeout=10)

        if response.status_code == 200:
            page_html = response.text
            s3_key = f"{today}/{today}-{page}.html"
            s3.put_object(
                Bucket=bucket_html,
                Key=s3_key,
                Body=page_html,
                ContentType="text/html"
            )
            print(f"[INFO] Página {page} guardada: {s3_key}")
        else:
            print(
                f"[WARN] Página {page} status_code: "
                f"{response.status_code}"
            )

    # Crear 'ready.txt' para disparar la Lambda de CSV
    # (Contenido opcional, con un simple mensaje)
    ready_content = (
        f"Archivos .html creados el {today}. "
        "Procesar CSV."
    )
    s3.put_object(
        Bucket=bucket_html,
        Key="ready.txt",
        Body=ready_content.encode("utf-8"),
        ContentType="text/plain"
    )
    print("[INFO] 'ready.txt' creado para disparar la generación de CSV.")

    return {
        "status": "success",
        "message": (
            f"Se descargaron 10 páginas en {bucket_html} y se creó "
            "'ready.txt'."
        )
    }
