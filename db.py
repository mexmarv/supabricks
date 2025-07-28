import pandas as pd
import os
import time
import logging
from dotenv import load_dotenv
from databricks import sql
from auth import DATABRICKS_HOST

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get Databricks connection details
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")

# Function to get a SQL connection
def get_connection():
    """Get a connection to Databricks SQL"""
    try:
        # Remove https:// from hostname if present
        hostname = DATABRICKS_HOST.replace("https://", "")
        logger.info(f"Connecting to Databricks SQL: {hostname}")
        
        # Extract the workspace ID from the hostname
        # Format: adb-<workspace_id>.<random_number>.azuredatabricks.net
        workspace_id = hostname.split('.')[0].replace('adb-', '')
        
        # Try to connect with SQL warehouse endpoint path
        connection = sql.connect(
            server_hostname=hostname,
            http_path=f"/sql/1.0/warehouses/{os.getenv('DATABRICKS_WAREHOUSE_ID', '0')}",
            access_token=DATABRICKS_TOKEN
        )
        return connection
    except Exception as e:
        logger.error(f"Error connecting to Databricks: {e}")
        # Try alternative http_path formats
        try:
            hostname = DATABRICKS_HOST.replace("https://", "")
            logger.info(f"Retrying connection with SQL protocol path")
            
            # Extract the workspace ID from the hostname
            workspace_id = hostname.split('.')[0].replace('adb-', '')
            
            connection = sql.connect(
                server_hostname=hostname,
                http_path=f"/sql/protocolv1/o/{workspace_id}/{os.getenv('DATABRICKS_CLUSTER_ID', '0')}",
                access_token=DATABRICKS_TOKEN
            )
            return connection
        except Exception as e2:
            logger.error(f"Error on second connection attempt: {e2}")
            
            # Try one more time with the SQL endpoint format
            try:
                hostname = DATABRICKS_HOST.replace("https://", "")
                logger.info(f"Retrying connection with SQL endpoint path")
                connection = sql.connect(
                    server_hostname=hostname,
                    http_path=f"/sql/1.0/endpoints/{os.getenv('DATABRICKS_ENDPOINT_ID', '0')}",
                    access_token=DATABRICKS_TOKEN
                )
                return connection
            except Exception as e3:
                logger.error(f"Error on third connection attempt: {e3}")
                return None

class SparkSession:
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    def _ensure_connection(self):
        """Ensure we have an active connection and cursor"""
        if self.connection is None:
            self.connection = get_connection()
            if self.connection:
                self.cursor = self.connection.cursor()
    
    def sql(self, query, max_retries=3):
        """Execute SQL query and return results as DataFrame"""
        retries = 0
        while retries < max_retries:
            try:
                logger.info(f"Executing query: {query}")
                
                # Ensure we have a connection
                self._ensure_connection()
                if not self.connection or not self.cursor:
                    raise Exception("Failed to establish connection")
                
                # Execute query
                self.cursor.execute(query)
                
                # Convert to pandas DataFrame
                columns = [desc[0] for desc in self.cursor.description] if self.cursor.description else []
                data = self.cursor.fetchall()
                df = pd.DataFrame(data, columns=columns)
                
                logger.info(f"Query returned {len(df)} rows")
                return df
            except Exception as e:
                retries += 1
                logger.error(f"Error executing query (attempt {retries}/{max_retries}): {e}")
                
                # Close and reset connection on error
                self._close_connection()
                
                if retries < max_retries:
                    # Exponential backoff
                    wait_time = 2 ** retries
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Max retries reached. Query failed: {query}")
                    # Return empty DataFrame on error
                    return pd.DataFrame()
    
    def _close_connection(self):
        """Close the current connection and reset state"""
        try:
            if self.cursor:
                self.cursor.close()
        except:
            pass
        
        try:
            if self.connection:
                self.connection.close()
        except:
            pass
            
        self.connection = None
        self.cursor = None
    
    def close(self):
        """Close the connection"""
        self._close_connection()

# Create spark session
spark = SparkSession()

# Register cleanup on exit
import atexit
atexit.register(spark.close)

def get_table_df(full_table_name):
    """Get table data as DataFrame
    
    Args:
        full_table_name: Full table name in format catalog.schema.table
    """
    try:
        logger.info(f"Getting data from table: {full_table_name}")
        query = f"SELECT * FROM {full_table_name} LIMIT 100"
        return spark.sql(query)
    except Exception as e:
        logger.error(f"Error getting table data: {e}")
        return pd.DataFrame()

def list_catalogs():
    """List all available Unity Catalogs"""
    try:
        logger.info("Listing catalogs")
        df = spark.sql("SHOW CATALOGS")
        catalogs = [row["catalog"] for _, row in df.iterrows()]
        logger.info(f"Found {len(catalogs)} catalogs: {catalogs}")
        return catalogs
    except Exception as e:
        logger.error(f"Error listing catalogs: {e}")
        return []

def list_schemas(catalog):
    """List all schemas in a specific catalog"""
    try:
        logger.info(f"Listing schemas in catalog: {catalog}")
        # Try different column names that might be returned
        df = spark.sql(f"SHOW SCHEMAS IN {catalog}")
        
        # Check which column name is present in the result
        if "namespace" in df.columns:
            schemas = [row["namespace"] for _, row in df.iterrows()]
        elif "schema" in df.columns:
            schemas = [row["schema"] for _, row in df.iterrows()]
        elif "databaseName" in df.columns:
            schemas = [row["databaseName"] for _, row in df.iterrows()]
        else:
            # If none of the expected columns are found, log the columns and return empty
            logger.warning(f"Unexpected schema result columns: {df.columns.tolist()}")
            schemas = []
            
        logger.info(f"Found {len(schemas)} schemas in {catalog}: {schemas}")
        return schemas
    except Exception as e:
        logger.error(f"Error listing schemas in {catalog}: {e}")
        return []

def list_tables_in_schema(catalog, schema):
    """List all tables in a specific schema"""
    try:
        logger.info(f"Listing tables in {catalog}.{schema}")
        df = spark.sql(f"SHOW TABLES IN {catalog}.{schema}")
        
        # Check which column name is present in the result
        if "tableName" in df.columns:
            table_name_col = "tableName"
        elif "name" in df.columns:
            table_name_col = "name"
        else:
            # If none of the expected columns are found, log the columns and return empty
            logger.warning(f"Unexpected table result columns: {df.columns.tolist()}")
            return []
            
        tables = [{
            "name": row[table_name_col],
            "full_name": f"{catalog}.{schema}.{row[table_name_col]}",
            "catalog": catalog,
            "schema": schema
        } for _, row in df.iterrows()]
        
        logger.info(f"Found {len(tables)} tables in {catalog}.{schema}")
        return tables
    except Exception as e:
        logger.error(f"Error listing tables in {catalog}.{schema}: {e}")
        return []

def list_all_tables():
    """List all tables across all catalogs and schemas using a more efficient approach"""
    try:
        logger.info("Listing all tables using a single query approach")
        
        # This query will get all tables from all catalogs and schemas
        # Exclude system catalogs and schemas
        query = """SELECT 
            table_catalog as catalog, 
            table_schema as schema, 
            table_name as name,
            concat(table_catalog, '.', table_schema, '.', table_name) as full_name
        FROM information_schema.tables
        WHERE table_type = 'BASE TABLE'
        AND table_catalog NOT LIKE 'sys%'
        AND table_catalog NOT IN ('information_schema', 'system')
        """
        
        df = spark.sql(query)
        
        if df.empty:
            logger.warning("No tables found or information_schema query failed, falling back to recursive method")
            return _list_all_tables_recursive(exclude_system=True)
        
        # Convert DataFrame to list of dictionaries
        tables = df.to_dict(orient="records")
        logger.info(f"Found a total of {len(tables)} tables using information_schema")
        return tables
    except Exception as e:
        logger.error(f"Error listing all tables with information_schema: {e}")
        logger.info("Falling back to recursive method")
        return _list_all_tables_recursive(exclude_system=True)

def _list_all_tables_recursive(exclude_system=True):
    """List all tables across all catalogs and schemas using recursive approach (fallback)"""
    all_tables = []
    try:
        logger.info("Starting to list all tables recursively across all catalogs and schemas")
        catalogs = list_catalogs()
        
        for catalog in catalogs:
            # Skip system catalogs
            if exclude_system and (catalog.startswith('sys') or catalog in ['information_schema', 'system']):
                logger.info(f"Skipping system catalog: {catalog}")
                continue
                
            logger.info(f"Processing catalog: {catalog}")
            schemas = list_schemas(catalog)
            
            for schema in schemas:
                # Skip system schemas
                if exclude_system and (schema.startswith('sys') or schema in ['information_schema', 'system']):
                    logger.info(f"Skipping system schema: {catalog}.{schema}")
                    continue
                    
                logger.info(f"Processing schema: {catalog}.{schema}")
                tables = list_tables_in_schema(catalog, schema)
                all_tables.extend(tables)
                
        logger.info(f"Found a total of {len(all_tables)} tables recursively")
        return all_tables
    except Exception as e:
        logger.error(f"Error listing all tables recursively: {e}")
        return []
