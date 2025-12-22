from mcp.server.fastmcp import FastMCP
import json
import os
import time
import sys

# --- PATHS ---
BRIDGE_FILE = r"C:\Users\%user_name%\RevitAI\command.json"
RESPONSE_FILE = r"C:\Users\%user_name%\RevitAI\response.json"

mcp = FastMCP("Revit-2020-Controller")

def wait_for_revit():
    """Waits for Revit to write a response back to us."""
    # WE REMOVED THE PRINT STATEMENT HERE TO STOP THE 'W' ERROR
    for i in range(120): # Increased wait time to 2 minutes just in case
        if os.path.exists(RESPONSE_FILE):
            time.sleep(0.5)
            try:
                with open(RESPONSE_FILE, 'r') as f:
                    data = json.load(f)
                os.remove(RESPONSE_FILE)
                return data
            except:
                pass 
        time.sleep(1)
    return {"error": "Revit timed out. Did you click the 'Run AI' button?"}

@mcp.tool()
def send_revit_command(python_code: str) -> str:
    """Send raw Python code to Revit to execute."""
    payload = {"type": "EXECUTE_CODE", "code": python_code}
    
    with open(BRIDGE_FILE, 'w') as f:
        json.dump(payload, f)
        
    return str(wait_for_revit())

@mcp.tool()
def read_revit_data(request_type: str) -> str:
    """Ask Revit for data."""
    payload = {"type": "READ_DATA", "query": request_type}
    
    with open(BRIDGE_FILE, 'w') as f:
        json.dump(payload, f)
        
    return str(wait_for_revit())

if __name__ == "__main__":
    mcp.run()