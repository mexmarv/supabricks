# Supabricks

<div align="center">

![Supabricks Logo](/supabicks.PNG)

**A Supabase-style API layer for Databricks Unity Catalog**

</div>

## Overview

Supabricks provides a REST API interface to Databricks Unity Catalog using FastAPI, enabling simple CRUD operations on Delta tables. It's designed to make Databricks data accessible through a clean, RESTful interface similar to Supabase.

## Features

- **RESTful API for Delta Tables**: Access and manipulate Delta tables through standard HTTP methods
- **PAT Authentication**: Secure access using Databricks Personal Access Tokens
- **Dynamic Table Discovery**: Automatically detects tables in your catalog every 60 seconds
- **Complete CRUD Operations**: Full support for Create, Read, Update, and Delete operations on both data and tables
- **Table Management**: Create and drop tables with customizable schemas
- **Delta Table Integration**: Leverages Delta Lake's MERGE capabilities for efficient updates
- **System Catalog Filtering**: Improved performance by excluding system catalogs and tables
- **OpenAPI Documentation**: Interactive API docs available at `/docs` and `/redoc`
- **ClearTunnel Integration**: Expose your FastAPI app publicly from within Databricks Apps

## Architecture

| Component | Description |
|-----------|-------------|
| FastAPI | Modern, high-performance web framework for building APIs |
| Databricks SDK | Handles user verification via Personal Access Tokens |
| PySpark | SQL engine for interacting with Delta tables |
| Auto-Polling | Background thread that detects tables every 60 seconds |
| ClearTunnel | Enables external access to the API from Databricks Apps |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/tables` | GET | List all available tables (excludes system tables) |
| `/tables/{table}` | GET | Retrieve rows from a table with optional filtering |
| `/tables/{table}` | POST | Insert new rows into a table |
| `/tables/{table}` | PUT | Update rows in a table using MERGE |
| `/tables/{table}` | DELETE | Delete rows from a table |
| `/tables/create` | POST | Create a new table with custom schema |
| `/tables/drop/{table}` | DELETE | Drop an existing table |

## Performance

| Operation | Typical Latency |
|-----------|------------------|
| GET /tables | 500ms–1.5s |
| GET /tables/{table} | 0.5s–2s |
| POST /tables/{table} | 2s–6s |
| PUT (MERGE) | 3s–10s |
| DELETE | 2s–6s |
| POST /tables/create | 3s–8s |
| DELETE /tables/drop/{table} | 2s–5s |

## Installation

### Requirements

- Python 3.8+
- Databricks workspace with Unity Catalog enabled
- Databricks Personal Access Token
- Databricks SQL Warehouse ID

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/supabricks.git
   cd supabricks
   ```

2. Create a `.env` file with your Databricks credentials:
   ```
   DATABRICKS_HOST=https://your-databricks-instance.cloud.databricks.com/
   DATABRICKS_TOKEN=your-personal-access-token
   ENABLE_CLEARTUNNEL=true
   DATABRICKS_WAREHOUSE_ID=your-sql-warehouse-id
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

## Deploying to Databricks

1. Package the application:
   ```bash
   zip -r supabricks_v3.2.zip .
   ```

2. Upload the ZIP file to your Databricks workspace under **Apps**

3. Configure the app using the provided `app.yaml`

4. Run the app and check the logs to find the ClearTunnel URL:
   - Look for a line like: `CLEARTUNNEL_URL=Urls(tunnel='https://your-unique-url.trycloudflare.com'...)`
   - This is the public URL you'll use to access your API

## Connecting to the API

### Authentication

All API requests require a Databricks Personal Access Token (PAT) for authentication. This ensures that users can only access data they have permissions for in Databricks.

1. Generate a PAT in your Databricks workspace:
   - Go to User Settings > Access Tokens > Generate New Token

2. Include the token in all API requests:
   ```bash
   curl -H "Authorization: Bearer your-personal-access-token" https://your-cleartunnel-url/tables
   ```

## Testing the API

Here's how to test each endpoint of the API:

### 1. Check API Connection

```bash
curl -H "Authorization: Bearer your-personal-access-token" https://your-cleartunnel-url/
```

### 2. List All Tables

```bash
curl -H "Authorization: Bearer your-personal-access-token" https://your-cleartunnel-url/tables
```

### 3. Create a New Table

```bash
curl -X POST -H "Authorization: Bearer your-personal-access-token" \
  -H "Content-Type: application/json" \
  -d '{
    "table_name": "catalog.schema.test_table",
    "columns": [
      {"name": "id", "type": "STRING", "nullable": false},
      {"name": "value", "type": "INT"},
      {"name": "description", "type": "STRING"}
    ],
    "comment": "Test table created via API"
  }' \
  https://your-cleartunnel-url/tables/create
```

### 4. Query a Table

```bash
curl -H "Authorization: Bearer your-personal-access-token" https://your-cleartunnel-url/tables/catalog.schema.test_table?limit=10
```

### 5. Insert Data

```bash
curl -X POST -H "Authorization: Bearer your-personal-access-token" \
  -H "Content-Type: application/json" \
  -d '{"data": [{"id": "test1", "value": 100, "description": "Test record"}]}' \
  https://your-cleartunnel-url/tables/catalog.schema.test_table
```

### 6. Update Data

```bash
curl -X PUT -H "Authorization: Bearer your-personal-access-token" \
  -H "Content-Type: application/json" \
  -d '{"filter": {"id": "test1"}, "updates": {"value": 200}}' \
  https://your-cleartunnel-url/tables/catalog.schema.test_table
```

### 7. Delete Data

```bash
curl -X DELETE -H "Authorization: Bearer your-personal-access-token" \
  -H "Content-Type: application/json" \
  -d '{"filter": {"id": "test1"}}' \
  https://your-cleartunnel-url/tables/catalog.schema.test_table
```

### 8. Drop a Table

```bash
curl -X DELETE -H "Authorization: Bearer your-personal-access-token" \
  https://your-cleartunnel-url/tables/drop/catalog.schema.test_table
```

## Measuring API Performance

To measure API performance, you can use the `time` command with curl:

```bash
time curl -H "Authorization: Bearer your-personal-access-token" https://your-cleartunnel-url/tables
```

Or create a shell script that captures timing information for each API call.

## Best Use Cases

- Admin portals and dashboards
- Data ingestion tools (batch processing)
- BI dashboards via the `/tables` endpoint
- Schema management and table creation
- Embedded applications requiring audit-compliant Delta APIs

## Limitations

- Not designed for high-throughput OLTP workloads
- Not optimized for real-time streaming writes
- Performance depends on underlying Databricks cluster configuration

## ClearTunnel Integration

Supabricks v3.2 includes [ClearTunnel](https://github.com/cleartunnel/cleartunnel) support to expose the FastAPI app publicly from within Databricks Apps, which do not allow incoming ports by default. This solves the accessibility issue when using Supabricks inside the Databricks environment.

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.