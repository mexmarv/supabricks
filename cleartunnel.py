# cleartunnel.py
import os
import time
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def start_tunnel(local_port=8000):
    print("🚇 Starting Cloudflare Tunnel...")
    
    # Check if ClearTunnel is enabled via environment variable
    if os.getenv("ENABLE_CLEARTUNNEL", "true").lower() != "true":
        print("⚠️ Cloudflare Tunnel is disabled via ENABLE_CLEARTUNNEL flag")
        return None
    
    try:
        # Import pycloudflared (will be available after pip install)
        try:
            from pycloudflared import try_cloudflare
        except ImportError:
            print("❌ pycloudflared not installed. Please run: pip install pycloudflared")
            return None
        
        print(f"🚀 Starting Cloudflare Tunnel on port {local_port}...")
        
        # Start the tunnel using pycloudflared
        # This will automatically download cloudflared binary if needed
        public_url = try_cloudflare(port=local_port)
        
        if not public_url:
            print("❌ Failed to establish Cloudflare Tunnel")
            return None
        
        print(f"✅ Cloudflare Tunnel established: {public_url}")
        
        # Save the URL to .env file
        save_tunnel_url(public_url)
        return public_url
        
    except Exception as e:
        print("❌ Cloudflare Tunnel failed:", e)
        return None

def save_tunnel_url(url):
    """Save the tunnel URL to .env file"""
    if not url:
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
    
    # Update or add CLEARTUNNEL_URL
    env_vars['CLEARTUNNEL_URL'] = url
    
    # Write back to .env file
    with open(env_path, 'w') as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    
    print(f"📝 Saved tunnel URL to .env file")
