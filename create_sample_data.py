import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)
n_rows = 50000

data = {
    "id": range(1, n_rows + 1),
    "name": [f"user_{i}" for i in range(1, n_rows + 1)],
    "age": np.random.randint(18, 80, n_rows),
    "salary": np.random.normal(50000, 15000, n_rows).round(2),
    "department": np.random.choice(
        ["Engineering", "Sales", "Marketing", "HR"],
        n_rows,
    ),
    "is_active": np.random.choice([True, False], n_rows, p=[0.8, 0.2]),
    "created_at": [
        datetime.now() - timedelta(days=np.random.randint(0, 365))
        for _ in range(n_rows)
    ],
}

df = pd.DataFrame(data)
df.to_csv("sample_data.csv", index=False)

print(f"Created sample_data.csv with {len(df)} rows")
print(df.head())
print(f"\nData types:\n{df.dtypes}")
