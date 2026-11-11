"""Build data/onet_tasks.csv from the O*NET 31.0 Task Statements file (CC BY 4.0).

Run once while preparing:  python tools/build_onet.py path/to/task_statements.csv
Source: https://www.onetcenter.org/dl_files/database/db_31_0_csv/task_statements.csv
"""
import sys
from pathlib import Path

import pandas as pd

OUT = Path(__file__).resolve().parent.parent / "data" / "onet_tasks.csv"
OCCUPATIONS = [  # spread from high to low expected LLM exposure
    "43-4051.00",  # Customer Service Representatives
    "43-3031.00",  # Bookkeeping, Accounting, and Auditing Clerks
    "13-2011.00",  # Accountants and Auditors
    "23-2011.00",  # Paralegals and Legal Assistants
    "27-3043.00",  # Writers and Authors
    "27-3091.00",  # Interpreters and Translators
    "15-1252.00",  # Software Developers
    "13-1161.00",  # Market Research Analysts and Marketing Specialists
    "19-3011.00",  # Economists
    "11-1021.00",  # General and Operations Managers
    "41-2031.00",  # Retail Salespersons
    "29-1141.00",  # Registered Nurses
    "47-2111.00",  # Electricians
    "53-3032.00",  # Heavy and Tractor-Trailer Truck Drivers
    "35-2014.00",  # Cooks, Restaurant
]

src = pd.read_csv(sys.argv[1], dtype=str)
src = src[src["O*NET-SOC Code"].isin(OCCUPATIONS)].sample(frac=1, random_state=42)
src = src.assign(core=src["Task Type"].ne("Core")).sort_values("core", kind="stable")  # core tasks first
df = (src.groupby("O*NET-SOC Code").head(10)
         .rename(columns={"Task ID": "task_id", "O*NET-SOC Code": "occupation_code",
                          "Title": "occupation_title", "Task": "task"})
         [["task_id", "occupation_code", "occupation_title", "task"]]
         .sort_values(["occupation_code", "task_id"]))
df.to_csv(OUT, index=False, encoding="utf-8")
print(df.occupation_title.value_counts().to_string(), "\n", len(df), "tasks ->", OUT)
