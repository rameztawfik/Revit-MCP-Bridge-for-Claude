🏗️ Revit MCP Bridge for Claude
====================================

**A secure, "air-gapped" bridge allowing Claude (AI) to control Autodesk Revit via the Model Context Protocol (MCP).**

🌟 Overview
-----------

Connecting AI to Revit is notoriously difficult because Revit uses a proprietary API that doesn't allow external connections. Most solutions require complex C# plugins or unsafe DLLs.

This project solves that by creating a **local file bridge**:

1.  **Claude (The Brain)** writes Python code or requests to a JSON file.
    
2.  **Revit (The Hands)** reads the file via a custom button and executes the command.
    
3.  **The Result** is sent back to Claude.
    

**Safety First:** This system is designed to be "Human-in-the-Loop." Claude cannot mess up your model in the background; you must physically click a button in Revit to approve and execute the AI's code.

🛠️ Prerequisites
-----------------

Before you start, ensure you have these installed:

1.  [**Python 3.10+**](https://www.python.org/downloads/)
    
    *   _Critical:_ Must check **"Add Python to PATH"** during installation.
        
2.  [**Claude Desktop App**](https://claude.ai/download)
    
    *   _Note:_ This does not work on the web version.
        
3.  [**pyRevit**](https://www.google.com/search?q=https://github.com/eirannejad/pyRevit/releases)
    
    *   Standard tool to run Python scripts inside Revit.
        
4.  **The mcp library**
    
    *   Run pip install mcp\[cli\] in your terminal.
    *   ```pip install mcp\[cli\]```
        

📂 Project Structure
--------------------

We will create a folder (e.g., C:\\Users\\YOUR\_NAME\\RevitAI) to act as the bridge.

Plaintext

```text
C:\Users\YOUR_NAME\RevitAI\
├── server.py           # The MCP Server (Talks to Claude)
├── command.json        # The message file (Claude writes here)
├── response.json       # The answer file (Revit writes here)
└── (Logs generated automatically)
```

🚀 Installation Guide
---------------------

### Step 1: Create the Bridge Folder

1.  Create a folder: C:\\Users\\YOUR\_USERNAME\\RevitAI
    
2.  **Important:** In File Explorer, go to View and check **"File name extensions"**.
    
3.  Create an empty text file inside and rename it strictly to command.json (Delete the .txt extension).
    

### Step 2: The Claude Server Script

Create a file named server.py in your folder and paste this code. This is the "Silent Version" (fixes JSON errors).

Python

```python

# server.py
from mcp.server.fastmcp import FastMCP
import json
import os
import time

# --- CONFIGURATION: UPDATE PATHS TO MATCH YOUR USERNAME ---
USER_PATH = os.path.expanduser("~") # Gets C:\Users\YourName automatically
BRIDGE_FILE = os.path.join(USER_PATH, "RevitAI", "command.json")
RESPONSE_FILE = os.path.join(USER_PATH, "RevitAI", "response.json")

mcp = FastMCP("Revit-2020-Controller")

def wait_for_revit():
    """Waits for Revit to respond silently."""
    for i in range(120): # Wait 2 mins max
        if os.path.exists(RESPONSE_FILE):
            time.sleep(0.5) # Allow write to finish
            try:
                with open(RESPONSE_FILE, 'r') as f:
                    data = json.load(f)
                os.remove(RESPONSE_FILE)
                return data
            except:
                pass # File busy, retry
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
    """Ask Revit for data (e.g. 'get_all_walls', 'get_project_info')."""
    payload = {"type": "READ_DATA", "query": request_type}
    with open(BRIDGE_FILE, 'w') as f:
        json.dump(payload, f)
    return str(wait_for_revit())

if __name__ == "__main__":
    mcp.run()
```

### Step 3: The Revit Button (pyRevit)

1.  %APPDATA%\\pyRevit\\Extensions\\
    
2.  Create this folder hierarchy: MyAI.extension -> MyAI.tab -> Tools.panel -> RunAI.pushbutton.
    
3.  Create a file script.py inside the RunAI.pushbutton folder:

Python    

```python

# script.py (Runs inside Revit)
import os
import json
import clr

# Update this path manually to match your folder!
BRIDGE_FOLDER = r"C:\Users\YOUR_USERNAME\RevitAI"
BRIDGE_FILE = os.path.join(BRIDGE_FOLDER, "command.json")
RESPONSE_FILE = os.path.join(BRIDGE_FOLDER, "response.json")

doc = __revit__.ActiveUIDocument.Document

def main():
    if not os.path.exists(BRIDGE_FILE):
        return # No commands waiting

    try:
        with open(BRIDGE_FILE, 'r') as f:
            data = json.load(f)
    except:
        return

    response = {"status": "success", "data": ""}

    try:
        if data["type"] == "EXECUTE_CODE":
            # Dangerous Magic: Execute the text as code
            from Autodesk.Revit.DB import Transaction
            exec(data["code"]) 
            response["data"] = "Code executed successfully."

        elif data["type"] == "READ_DATA":
            if data["query"] == "get_project_info":
                response["data"] = {"Title": doc.Title, "Path": doc.PathName}
            # Add more queries here!

    except Exception as e:
        response["status"] = "error"
        response["data"] = str(e)

    with open(RESPONSE_FILE, 'w') as f:
        json.dump(response, f)
    
    os.remove(BRIDGE_FILE)

main() 
```

### Step 4: Configure Claude

1.  Open Command Prompt and type where python. Copy the full path (e.g., C:\\Python312\\python.exe).
    
2.  Open Claude -> Settings -> Developer -> **Edit Config**.
    
3.  Paste this (Update the paths!):
    
JSON

```JSON

{
  "mcpServers": {
    "revit-agent": {
      "command": "C:\\Path\\To\\python.exe",
      "args": [
        "-u",
        "C:\\Users\\YOUR_USERNAME\\RevitAI\\server.py"
      ]
    }
  }
}
```

_Note: The -u flag is critical to prevent "Server Disconnected" errors._

🚦 How to Use
-------------

1.  **Restart Claude:** Ensure the "Plug" icon 🔌 appears in the chat bar.
    1.  Open Claude -> Settings -> Developer -> **Edit Config**.
    2.  Ensure the config file is running.
    3.  You may not need the Plug icon to appear in the chat bar, Claude will still be running with the MCP is the above steps are correct.
    
2.  **Restart Revit:** You should see a "MyAI" tab with a "RunAI" button.
    
3.  **Prompt Claude:** _"Create a script to draw a wall 10ft long."_
    
4.  **Wait:** Claude will say "I have sent the command..."
    
5.  **Click:** Go to Revit and click **RunAI**.
    
6.  **Success:** Claude receives the confirmation and reports back.
    

🐛 Troubleshooting & "Gotchas"
------------------------------

| Error Message              | Cause                                                      | Solution                                                                 |
|---------------------------|------------------------------------------------------------|--------------------------------------------------------------------------|
| Server disconnected       | Claude can't find Python or the script.                    | Use the full path to `python.exe` in the config file. Add the `-u` flag. |
| Unexpected token 'W'...   | The server printed text ("Waiting...") which isn't JSON.   | Remove all `print()` statements from `server.py`.                        |
| Button doesn't work       | `command.json.txt` double extension.                       | Enable **File Extensions** in Windows View settings and rename properly. |
| Icon missing in Claude    | JSON syntax error in config.                               | Check for missing commas or single backslashes `\` (must be `\\`).       |


🔮 Future Roadmap
-----------------

*   \[ \] **Automated Listener:** Implement a generic IExternalEventHandler in Revit to listen for file changes automatically (removing the need to click the button).
    
*   \[ \] **More Read Tools:** Add specific tools to read Sheet Lists, Family Types, and Materials.
    

_Built with ❤️ using the Model Context Protocol for Revit._