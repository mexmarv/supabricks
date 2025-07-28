from fastapi import FastAPI, Request, HTTPException
from auth import verify_pat, DATABRICKS_HOST
from db import spark, get_table_df, list_all_tables
from models import InsertPayload, UpdatePayload, DeletePayload, CreateTablePayload
from utils import apply_filter, dict_to_sql_filter
import pandas as pd
import threading
import time
import os
from cleartunnel import start_tunnel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Supabricks",
    description="A powerful REST API for Databricks that provides SQL-like operations through HTTP endpoints. Supabricks enables you to interact with Databricks tables using standard REST operations, similar to Supabase but for Databricks.",
    version="3.2",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "Supabricks Team",
        "url": "https://github.com/mexmarv/supabricks",  # Replace with actual repo URL if available
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    }
)

@app.on_event("startup")
def startup_event():
    print(f"🧠 Supabricks started. Detected host: {DATABRICKS_HOST}")
    
    # Start ClearTunnel if enabled
    if os.getenv("ENABLE_CLEARTUNNEL", "true").lower() == "true":
        tunnel_url = start_tunnel(8000)
        if tunnel_url:
            print(f"🌐 API accessible via: {tunnel_url}")

@app.middleware("http")
async def auth_pat_middleware(request: Request, call_next):
    if request.url.path.startswith("/tables"):
        user_info = verify_pat(request)
        request.state.user = user_info
    return await call_next(request)

@app.get("/", 
    summary="API Root",
    description="Returns basic information about the Supabricks API including version and available endpoints.")
def root():
    tunnel_url = os.getenv("CLEARTUNNEL_URL", None)
    return {
        "app": "Supabricks",
        "version": "3.2",
        "docs": "/docs",
        "tables_endpoint": "/tables",
        "public_url": tunnel_url
    }

@app.get("/tables", 
    summary="List All Tables",
    description="Returns a list of all tables accessible to the authenticated user across all catalogs and schemas.")
def list_tables():
    return list_all_tables()

@app.get("/tables/{full_table_name}", 
    summary="Query Table Rows",
    description="Retrieves rows from the specified table. The table name should be in the format 'catalog.schema.table'.")
def get_rows(full_table_name: str, limit: int = 100):
    df = get_table_df(full_table_name)
    if df.empty:
        raise HTTPException(status_code=404, detail="Table not found or empty")
    return df.head(limit).to_dict(orient="records")

@app.post("/tables/{full_table_name}", 
    summary="Insert Rows",
    description="Inserts new rows into the specified table. Provide data as an array of objects where each object represents a row.")
def insert_rows(full_table_name: str, payload: InsertPayload):
    df = pd.DataFrame(payload.data)
    try:
        # Convert DataFrame to SQL insert statements
        columns = ", ".join(df.columns)
        values_list = []
        for _, row in df.iterrows():
            values = ", ".join([f"'{str(val)}'" if val is not None else "NULL" for val in row])
            values_list.append(f"({values})")
        
        values_str = ", ".join(values_list)
        query = f"INSERT INTO {full_table_name} ({columns}) VALUES {values_str}"
        spark.sql(query)
        return {"status": "inserted", "rows": len(payload.data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/tables/{full_table_name}", 
    summary="Update Rows",
    description="Updates rows in the specified table that match the filter criteria. Provide filter conditions and the values to update.")
def update_rows(full_table_name: str, payload: UpdatePayload):
    try:
        filter_expr = dict_to_sql_filter(payload.filter)
        updates = ", ".join([f"{k} = '{v}'" for k, v in payload.updates.items()])
        query = f"UPDATE {full_table_name} SET {updates} WHERE {filter_expr}"
        spark.sql(query)
        return {"status": "updated", "where": payload.filter}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/tables/{full_table_name}", 
    summary="Delete Rows",
    description="Deletes rows from the specified table that match the filter criteria.")
def delete_rows(full_table_name: str, payload: DeletePayload):
    try:
        filter_expr = dict_to_sql_filter(payload.filter)
        query = f"DELETE FROM {full_table_name} WHERE {filter_expr}"
        spark.sql(query)
        return {"status": "deleted", "where": payload.filter}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tables/create", 
    summary="Create New Table",
    description="Creates a new table with the specified schema. Provide table name, column definitions, and optional properties.")
def create_table(payload: CreateTablePayload):
    try:
        # Build CREATE TABLE statement
        columns_def = ", ".join([f"{col.name} {col.type}{' NOT NULL' if not col.nullable else ''}" + 
                              (f" COMMENT '{col.comment}'" if col.comment else "") 
                              for col in payload.columns])
        query = f"CREATE TABLE {payload.table_name} ({columns_def})"
        
        # Add optional clauses if provided
        if payload.comment:
            query += f" COMMENT '{payload.comment}'"
        if payload.location:
            query += f" LOCATION '{payload.location}'"
        if payload.partitioned_by and len(payload.partitioned_by) > 0:
            partition_cols = ", ".join(payload.partitioned_by)
            query += f" PARTITIONED BY ({partition_cols})"
        
        # Execute the query
        spark.sql(query)
        return {"status": "created", "table": payload.table_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/tables/drop/{full_table_name}", 
    summary="Drop Table",
    description="Permanently deletes the specified table. Use with caution as this operation cannot be undone.")
def drop_table(full_table_name: str):
    try:
        query = f"DROP TABLE {full_table_name}"
        spark.sql(query)
        return {"status": "dropped", "table": full_table_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
