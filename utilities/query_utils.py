from dotenv import load_dotenv
import os
import pandas as pd
import pyodbc

def none_if_empty(v):
    if v is None:
        return None
    if isinstance(v, str):
        s = v.strip()
        return None if s == "" else s
    return v

def one_if_empty(v):
    if not isinstance(v, int):
        return 1
    return v

def csv_ids(s):
    s = none_if_empty(s)
    if s is None:
        return None
    # split on commas only, strip spaces
    parts = [p.strip() for p in s.split(",") if p.strip() != ""]
    return ",".join(parts) if parts else None

def get_conn_str():
    load_dotenv()
    env = {
        "server": os.getenv("DB_SERVER"),
        "database": os.getenv("DB_NAME"),
        "username": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "driver": os.getenv("DB_DRIVER"),
    }

    return (
        f"DRIVER={env['driver']};"
        f"SERVER={env['server']};"
        f"DATABASE={env['database']};"
        f"UID={env['username']};"
        f"PWD={env['password']};"
        f"TrustServerCertificate=yes;"
    )

def build_millitary_query(Str_ID, Org_IDs, Company_ID, Person_Inst_IDs, Org_Type, Business_Entity_ID, WithChilds, Military_Status, Financial_Company_IDs):
    sql = "EXEC dbo.Rpt_Personnel_Military_Data ?, ?, ?, ?, ?, ?, ?, ?, ?"
    params = [
        (Str_ID),
        csv_ids(Org_IDs),                 # string IDs → comma CSV or None
        one_if_empty(Company_ID),
        csv_ids(Person_Inst_IDs),         # string IDs → comma CSV or None
        (Org_Type),
        one_if_empty(Business_Entity_ID),
        int(WithChilds),                  # always bit (0/1)
        (Military_Status),
        csv_ids(Financial_Company_IDs),   # string IDs → comma CSV or None
    ]
    return sql, params

def build_custodies_query(Str_ID, Org_IDs, Company_ID, Person_Inst_IDs, Org_Type, Business_Entity_ID, WithChilds, Employee_Status, Financial_Company_IDs, Custody_IDs):
    sql = "EXEC dbo.Rpt_Personnel_Custodies_Data ?, ?, ?, ?, ?, ?, ?, ?, ?, ?"
    params = [
        (Str_ID),
        csv_ids(Org_IDs),                 # string IDs → comma CSV or None
        one_if_empty(Company_ID),
        csv_ids(Person_Inst_IDs),         # string IDs → comma CSV or None
        (Org_Type),
        one_if_empty(Business_Entity_ID),
        int(WithChilds),                  # always bit (0/1)
        (Employee_Status),
        csv_ids(Financial_Company_IDs),   # string IDs → comma CSV or None
        csv_ids(Custody_IDs),             # string IDs → comma CSV or None
    ]
    return sql, params

def get_df_from_query(query):
    sql, params = query
    with pyodbc.connect(get_conn_str()) as conn:
        df = pd.read_sql_query(sql, conn, params=params)
        return df
