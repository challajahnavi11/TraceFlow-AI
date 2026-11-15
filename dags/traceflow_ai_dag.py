
from datetime import datetime, timezone

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator


with DAG(
    dag_id="traceflow_ai_pipeline",
    description="TraceFlow AI - Automated data quality investigation pipeline",
    start_date=datetime(2026, 11, 13, tzinfo=timezone.utc),
    schedule=None,
    catchup=False,
    tags=["traceflow-ai", "data-quality"],
) as dag:

    generate_orders = BashOperator(
        task_id="generate_orders",
        bash_command="python /opt/airflow/src/pipeline/generate_data.py",
    )

    create_test_data = BashOperator(
        task_id="create_test_data",
        bash_command="python /opt/airflow/src/pipeline/create_test_failures.py",
    )

    run_quality_checks = BashOperator(
        task_id="run_quality_checks",
        bash_command=(
            "python /opt/airflow/src/quality/check_orders.py "
            "/opt/airflow/data/processed/orders_test.csv"
        ),
    )

    generate_orders >> create_test_data >> run_quality_checks
