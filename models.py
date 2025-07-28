from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class InsertPayload(BaseModel):
    data: List[Dict[str, Any]] = Field(
        ...,
        description="Array of objects where each object represents a row to insert. Keys are column names, values are the data to insert.",
        example=[{"column1": "value1", "column2": 123}]
    )

class UpdatePayload(BaseModel):
    filter: Dict[str, Any] = Field(
        ...,
        description="Filter criteria to identify which rows to update. Keys are column names, values are the values to match.",
        example={"id": 123}
    )
    updates: Dict[str, Any] = Field(
        ...,
        description="Values to update. Keys are column names, values are the new values to set.",
        example={"status": "completed", "updated_at": "2023-01-01"}
    )

class DeletePayload(BaseModel):
    filter: Dict[str, Any] = Field(
        ...,
        description="Filter criteria to identify which rows to delete. Keys are column names, values are the values to match.",
        example={"id": 123}
    )

class ColumnDefinition(BaseModel):
    name: str = Field(..., description="Name of the column")
    type: str = Field(..., description="SQL data type of the column (e.g., STRING, INT, TIMESTAMP)")
    comment: Optional[str] = Field(None, description="Optional comment describing the column's purpose")
    nullable: bool = Field(True, description="Whether the column can contain NULL values")

class CreateTablePayload(BaseModel):
    table_name: str = Field(
        ..., 
        description="Full table name in the format 'catalog.schema.table'",
        example="my_catalog.my_schema.my_table"
    )
    columns: List[ColumnDefinition] = Field(
        ...,
        description="List of column definitions for the new table"
    )
    comment: Optional[str] = Field(None, description="Optional comment describing the table's purpose")
    location: Optional[str] = Field(None, description="Optional storage location for the table data")
    partitioned_by: Optional[List[str]] = Field(None, description="Optional list of column names to partition the table by")
