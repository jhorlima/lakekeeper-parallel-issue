from setuptools import setup

setup(
    name="lakekeeper-ingestion",
    version="0.1.0",
    packages=["src"],
    install_requires=[
        "typer==0.16.0",
        "pyiceberg[pyarrow,s3fs]==0.9.1",
        "numpy>=2.2.6",
        "pandas>=2.2.3",
        "pyarrow>=17.0.0,<20.0.0",
        "requests>=2.32.3",
    ],
    entry_points={
        "console_scripts": [
            "lakekeeper-ingest=src.main:app",
        ],
    },
)
