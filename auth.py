from fastapi import Request, HTTPException
from databricks.sdk import WorkspaceClient
from databricks.sdk.errors import PermissionDenied
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_databricks_host():
    try:
        # First try to get from .env file
        env_host = os.getenv("DATABRICKS_HOST")
        if env_host:
            return env_host
            
        # Then try to get from metadata API
        from requests import get
        host = get("http://169.254.169.254/latest/meta-data/public-hostname", timeout=2).text
        if host:
            host_url = "https://" + host
            # Save the detected host to .env file
            save_host_to_env(host_url)
            return host_url
        return None
    except:
        default_host = "https://<your-workspace>.cloud.databricks.com"
        return os.getenv("DATABRICKS_HOST", default_host)

def save_host_to_env(host_url):
    """Save the detected host URL to .env file"""
    if not host_url:
        return
    
    # Read current .env file
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    env_vars = {}
    
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    
    # Only update if not already set
    if "DATABRICKS_HOST" not in env_vars:
        env_vars['DATABRICKS_HOST'] = host_url
        
        # Write back to .env file
        with open(env_path, 'w') as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
        
        print(f"📝 Saved Databricks host to .env file: {host_url}")

DATABRICKS_HOST = get_databricks_host()

def verify_pat(request: Request):
    # Try to get token from .env file first
    env_token = os.getenv("DATABRICKS_TOKEN")
    
    # Then check Authorization header
    auth = request.headers.get("Authorization")
    if auth and auth.startswith("Bearer dapi"):
        token = auth.split(" ")[1]
        # Save token to .env if not already there
        if not env_token:
            save_token_to_env(token)
    elif env_token:
        token = env_token
    else:
        raise HTTPException(status_code=401, detail="Missing or invalid PAT")
        
    try:
        w = WorkspaceClient(host=DATABRICKS_HOST, token=token)
        user = w.current_user.me()
        return {"token": token, "user": user.user_name}
    except PermissionDenied:
        raise HTTPException(status_code=403, detail="Permission denied")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def save_token_to_env(token):
    """Save the token to .env file"""
    if not token:
        return
    
    # Read current .env file
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    env_vars = {}
    
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    
    # Only update if not already set
    if "DATABRICKS_TOKEN" not in env_vars:
        env_vars['DATABRICKS_TOKEN'] = token
        
        # Write back to .env file
        with open(env_path, 'w') as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
        
        print(f"📝 Saved Databricks token to .env file")