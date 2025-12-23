import os
import json
import clr

# Update this path manually to match your folder!

BRIDGE_FOLDER = r"C:\Users\%user_name%\RevitAI"
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
            # Note: The AI must include its own imports (Transaction, etc.)
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