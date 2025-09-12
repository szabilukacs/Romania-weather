from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import subprocess

# --- Default arguments ---
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# --- Python callables ---
def run_main_py():
    subprocess.run(["python", "/opt/airflow/scripts/main.py"], check=True)

def run_current_data_py():
    subprocess.run(["python", "/opt/airflow/scripts/current_data.py"], check=True)

# --- DAG definition ---
with DAG(
    dag_id="weather_pipeline",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule="@daily",  # Airflow 3.x
    catchup=False,
    tags=["weather"]
) as dag:

    task_main = PythonOperator(
        task_id="run_main",
        python_callable=run_main_py,
    )

    task_current = PythonOperator(
        task_id="run_current_data",
        python_callable=run_current_data_py,
    )

    # --- Dependencies ---
    task_main >> task_current
