# 📊 Facebook Metrics Data Pipeline for The Vet CSR

This repository contains a ready-to-run Python pipeline for collecting Facebook page metrics for **The Vet CSR**:

- Facebook page: <https://www.facebook.com/thevetcsr/>
- Default page username: `thevetcsr`
- Default Graph API version: `v21.0`

The pipeline uses the Facebook Graph API to collect follower snapshots and recent post interaction metrics, then saves the data to CSV files for analysis in Python, Excel, Power BI, dashboards, or AI workflows. It now supports paginated extraction, retry-enabled HTTP requests, optional date windows, append/refresh modes, and a local sample-data run mode for validating the pipeline without live credentials.

## 📚 What the pipeline collects

The script performs these tasks:

- Resolves the The Vet CSR page by `PAGE_ID` or by the default username `thevetcsr`.
- Retrieves current page-level counts:
  - Followers
  - Fans/likes, when returned by the API
- Lists recent posts across paginated Graph API responses.
- Supports larger runs with `POST_LIMIT`, `PAGE_SIZE`, `SINCE`, and `UNTIL`.
- Extracts interaction metrics from each post:
  - Likes
  - Comments
  - Shares
- Saves the data to CSV files:
  - `facebook_followers.csv`
  - `facebook_posts.csv`

> Note: Facebook Graph API fields and permissions depend on your app review status, access token type, and page permissions. If Facebook does not return a field, the script leaves that value empty or uses `0` for post interaction counts.

## 🧰 Technologies Used

- Python 3.x
- `requests`
- `python-dotenv`
- Facebook Graph API (`v21.0` by default)

## 📁 Project files

```text
.
├── .env.example            # Environment variable template for The Vet CSR
├── .gitignore              # Keeps tokens, virtualenvs, and generated CSVs out of git
├── README.md               # Project documentation
├── extractDataFacebook.py  # Facebook metrics extraction script
├── requirements.txt        # Python dependencies
└── tests/                  # Unit tests for pagination and sample runs
```

## 📦 Installation and Usage

### 1. Clone this repository

```bash
git clone https://github.com/ehm435/extract-facebook-metrics.git
cd extract-facebook-metrics
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Prepare your `.env` file

Copy the example file:

```bash
cp .env.example .env
```

Then edit `.env` and add a valid Facebook Page access token:

```env
PAGE_ACCESS_TOKEN=YOUR_ACCESS_TOKEN
PAGE_USERNAME=thevetcsr
FACEBOOK_PAGE_URL=https://www.facebook.com/thevetcsr/
PAGE_ID=
GRAPH_API_VERSION=v21.0
POST_LIMIT=500
PAGE_SIZE=100
REQUEST_TIMEOUT=30
OUTPUT_DIR=.
SINCE=
UNTIL=
APPEND_POSTS=false
SAMPLE_DATA=false
```

`PAGE_ID` is optional. If you know the numeric page ID, add it to `.env`; otherwise, the script uses `PAGE_USERNAME=thevetcsr`.

### 5. Run the script

```bash
python extractDataFacebook.py
```

You can override runtime options without editing `.env`:

```bash
python extractDataFacebook.py --post-limit 1000 --page-size 100 --since 2026-01-01 --output-dir data
```

To validate the pipeline locally without Facebook credentials, run it with representative sample data:

```bash
python extractDataFacebook.py --sample-data --output-dir /tmp/thevetcsr_sample
```

## 💡 Sample Output

```text
Getting page follower count...

Page: The Vet CSR (1234567890)
Followers: 12345
Fans: 12000

Getting posts and metrics...

Post ID: 123_4567890
URL: https://www.facebook.com/123/posts/4567890
Created at: 2025-05-25T18:20:00+0000
Likes: 80
Comments: 15
Shares: 7
--------------------------------------------------

Saved follower snapshot to facebook_followers.csv
Saved 500 post rows to facebook_posts.csv
```

## 📄 Generated CSV files

### `facebook_followers.csv`

Follower snapshots are appended over time so you can track page growth historically.

Columns:

- `extracted_at`
- `page_id`
- `page_name`
- `page_url`
- `followers`
- `fans`

### `facebook_posts.csv`

Recent post metrics are refreshed on each run by default. Use `--append-posts` or `APPEND_POSTS=true` when you want to append every extraction run instead.

Columns:

- `extracted_at`
- `page_id`
- `page_name`
- `post_id`
- `created_time`
- `permalink_url`
- `message`
- `likes`
- `comments`
- `shares`

## 🚀 Possible Improvements

- Include additional metrics such as reach, impressions, reactions by type, or video views.
- Support multiple Facebook pages for comparisons.
- Schedule the script with cron, GitHub Actions, Airflow, or Prefect for recurring scaled runs.
- Export to Excel, JSON, a database, or cloud storage.
- Build a dashboard in Power BI, Looker Studio, Streamlit, or Dash.

---

## 🇪🇸 Versión en Español

# 📊 Data Pipeline para Métricas de Facebook de The Vet CSR

Este repositorio contiene un pipeline en Python listo para recolectar métricas de la página de Facebook de **The Vet CSR**:

- Página de Facebook: <https://www.facebook.com/thevetcsr/>
- Usuario predeterminado de la página: `thevetcsr`
- Versión predeterminada de Graph API: `v21.0`

El pipeline utiliza la Facebook Graph API para recolectar snapshots de seguidores y métricas de interacción de publicaciones recientes. Luego guarda los datos en archivos CSV para analizarlos con Python, Excel, Power BI, dashboards o flujos de trabajo con IA. Ahora soporta extracción paginada, reintentos HTTP, ventanas opcionales de fechas, modos de append/refresh y un modo local con datos de ejemplo para validar el flujo sin credenciales reales.

## 📚 Qué recolecta el pipeline

El script ejecuta estas tareas:

- Resuelve la página de The Vet CSR mediante `PAGE_ID` o el usuario predeterminado `thevetcsr`.
- Obtiene métricas actuales a nivel de página:
  - Seguidores
  - Fans/likes, cuando la API los devuelve
- Lista publicaciones recientes a través de respuestas paginadas de Graph API.
- Soporta ejecuciones más grandes con `POST_LIMIT`, `PAGE_SIZE`, `SINCE` y `UNTIL`.
- Extrae métricas de interacción de cada publicación:
  - Likes
  - Comentarios
  - Compartidos
- Guarda los datos en archivos CSV:
  - `facebook_followers.csv`
  - `facebook_posts.csv`

> Nota: los campos y permisos de Facebook Graph API dependen del estado de revisión de tu app, el tipo de token y los permisos de la página. Si Facebook no devuelve un campo, el script deja ese valor vacío o usa `0` para los conteos de interacción de publicaciones.

## 🧰 Tecnologías utilizadas

- Python 3.x
- `requests`
- `python-dotenv`
- Facebook Graph API (`v21.0` por defecto)

## 📁 Archivos del proyecto

```text
.
├── .env.example            # Plantilla de variables de entorno para The Vet CSR
├── .gitignore              # Evita subir tokens, entornos virtuales y CSV generados
├── README.md               # Documentación del proyecto
├── extractDataFacebook.py  # Script de extracción de métricas de Facebook
├── requirements.txt        # Dependencias de Python
└── tests/                  # Pruebas unitarias para paginación y ejecuciones de ejemplo
```

## 📦 Instalación y uso

### 1. Clona este repositorio

```bash
git clone https://github.com/ehm435/extract-facebook-metrics.git
cd extract-facebook-metrics
```

### 2. Crea y activa un entorno virtual

```bash
python -m venv .venv
source .venv/bin/activate
```

En Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Instala las dependencias

```bash
pip install -r requirements.txt
```

### 4. Prepara tu archivo `.env`

Copia el archivo de ejemplo:

```bash
cp .env.example .env
```

Después edita `.env` y agrega un token válido de Facebook Page:

```env
PAGE_ACCESS_TOKEN=YOUR_ACCESS_TOKEN
PAGE_USERNAME=thevetcsr
FACEBOOK_PAGE_URL=https://www.facebook.com/thevetcsr/
PAGE_ID=
GRAPH_API_VERSION=v21.0
POST_LIMIT=500
PAGE_SIZE=100
REQUEST_TIMEOUT=30
OUTPUT_DIR=.
SINCE=
UNTIL=
APPEND_POSTS=false
SAMPLE_DATA=false
```

`PAGE_ID` es opcional. Si conoces el ID numérico de la página, agrégalo en `.env`; de lo contrario, el script usa `PAGE_USERNAME=thevetcsr`.

### 5. Ejecuta el script

```bash
python extractDataFacebook.py
```

También puedes cambiar opciones sin editar `.env`:

```bash
python extractDataFacebook.py --post-limit 1000 --page-size 100 --since 2026-01-01 --output-dir data
```

Para validar el pipeline localmente sin credenciales de Facebook, ejecútalo con datos representativos de ejemplo:

```bash
python extractDataFacebook.py --sample-data --output-dir /tmp/thevetcsr_sample
```

## 💡 Ejemplo de salida

```text
Getting page follower count...

Page: The Vet CSR (1234567890)
Followers: 12345
Fans: 12000

Getting posts and metrics...

Post ID: 123_4567890
URL: https://www.facebook.com/123/posts/4567890
Created at: 2025-05-25T18:20:00+0000
Likes: 80
Comments: 15
Shares: 7
--------------------------------------------------

Saved follower snapshot to facebook_followers.csv
Saved 500 post rows to facebook_posts.csv
```

## 📄 Archivos CSV generados

### `facebook_followers.csv`

Los snapshots de seguidores se agregan con cada ejecución para analizar el crecimiento histórico de la página.

Columnas:

- `extracted_at`
- `page_id`
- `page_name`
- `page_url`
- `followers`
- `fans`

### `facebook_posts.csv`

Las métricas de publicaciones recientes se actualizan en cada ejecución de forma predeterminada. Usa `--append-posts` o `APPEND_POSTS=true` cuando quieras agregar cada ejecución al histórico.

Columnas:

- `extracted_at`
- `page_id`
- `page_name`
- `post_id`
- `created_time`
- `permalink_url`
- `message`
- `likes`
- `comments`
- `shares`

## 🚀 Posibles mejoras

- Incluir métricas adicionales como alcance, impresiones, reacciones por tipo o visualizaciones de video.
- Soportar varias páginas de Facebook para comparaciones.
- Programar el script con cron, GitHub Actions, Airflow o Prefect para ejecuciones recurrentes a escala.
- Exportar a Excel, JSON, una base de datos o almacenamiento en la nube.
- Crear un dashboard en Power BI, Looker Studio, Streamlit o Dash.
