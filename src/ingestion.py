import os
import pandas as pd
import pyarrow as pa
from pyiceberg.catalog.rest import RestCatalog
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from contextlib import contextmanager


def get_catalog():
    catalog_url = os.getenv(
        "CATALOG_URL",
        "http://localhost:8181/catalog",
    )
    warehouse = os.getenv("WAREHOUSE", "demo")
    catalog_name = os.getenv("CATALOG_NAME", "my_catalog")
    catalog_token = os.getenv("CATALOG_TOKEN", "dummy")

    return RestCatalog(
        name=catalog_name,
        warehouse=warehouse,
        uri=catalog_url,
        token=catalog_token,
    )


def initialize_table(
    catalog,
    namespace: str,
    table_name: str,
    df: pd.DataFrame,
) -> bool:
    try:
        try:
            catalog.create_namespace(namespace)
        except Exception:
            pass

        table_identifier = (namespace, table_name)

        try:
            table = catalog.load_table(table_identifier)
            return table
        except Exception:
            pa_df = pa.Table.from_pandas(df)

            try:
                catalog.drop_table(table_identifier)
            except Exception:
                pass

            table = catalog.create_table(
                identifier=table_identifier,
                schema=pa_df.schema,
            )
            return table

    except Exception as e:
        print(f"Error initializing table: {e}")
        return None


@contextmanager
def http_request_monitor():
    original_request = requests.Session.request

    def monitored_request(self, method, url, **kwargs):
        print(f"HTTP {method.upper()} to {url}")
        try:
            response = original_request(self, method, url, **kwargs)
            print(f"Response: {response.status_code}")

            if 400 <= response.status_code < 600:
                print(
                    f"Error {response.status_code}: {response.text[:200]}",
                )

            return response
        except Exception as e:
            print(f"Request exception: {e}")
            raise

    requests.Session.request = monitored_request

    try:
        yield
    finally:
        requests.Session.request = original_request


def ingest_chunk(
    chunk_id: int,
    chunk_df: pd.DataFrame,
    catalog,
    namespace: str,
    table_name: str,
) -> bool:
    with http_request_monitor():
        try:
            table_identifier = (namespace, table_name)
            table = catalog.load_table(table_identifier)

            arrow_table = pa.Table.from_pandas(chunk_df)
            table.append(arrow_table)

            return True

        except Exception as e:
            print(f"Error ingesting chunk {chunk_id}: {e}")
            return False


def ingest_data(
    file_path: str,
    workers: int = 2,
    chunk_size: int = 10000,
):
    namespace = os.getenv("NAMESPACE", "default")
    table_name = os.getenv("TABLE_NAME", "sample_table")

    catalog = get_catalog()

    df = pd.read_csv(file_path)
    print(f"Loaded {len(df)} rows from {file_path}")

    table = initialize_table(catalog, namespace, table_name, df)

    if table is None:
        print("Failed to initialize table")
        return False

    print(f"Table {namespace}.{table_name} initialized")

    chunks = [df[i : i + chunk_size] for i in range(0, len(df), chunk_size)]
    print(f"Split data into {len(chunks)} chunks of {chunk_size} rows each")

    successful_chunks = 0
    failed_chunks = 0

    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_chunk = {
            executor.submit(
                ingest_chunk,
                i,
                chunk,
                catalog,
                namespace,
                table_name,
            ): i
            for i, chunk in enumerate(chunks)
        }

        for future in as_completed(future_to_chunk):
            chunk_id = future_to_chunk[future]
            try:
                result = future.result()
                if result:
                    successful_chunks += 1
                    print(f"✓ Chunk {chunk_id + 1} ingested")
                else:
                    failed_chunks += 1
                    print(f"✗ Chunk {chunk_id + 1} failed")
            except Exception as e:
                failed_chunks += 1
                print(f"✗ Chunk {chunk_id + 1} failed: {e}")

    print("\nIngestion Summary:")
    print(f"✓ Successful chunks: {successful_chunks}")
    print(f"✗ Failed chunks: {failed_chunks}")

    return failed_chunks == 0
