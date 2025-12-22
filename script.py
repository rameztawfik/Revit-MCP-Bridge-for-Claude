# CODE FOR REVIT 2020 (IronPython)
import os
import json
import clr

# Import Revit Services
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *

# BRIDGE FILES
BRIDGE_FILE = r"C:\Users\%user_name%\RevitAI\command.json"
RESPONSE_FILE = r"C:\Users\%user_name%\RevitAI\response.json"

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

def main():
    if not os.path.exists(BRIDGE_FILE):
        print("No commands from Claude waiting.")
        return

    # 1. Read the Command
    try:
        with open(BRIDGE_FILE, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print("Error reading command: " + str(e))
        return

    response = {"status": "success", "data": ""}

    # 2. Decide what to do
    try:
        # --- OPTION A: EXECUTE CODE (Dangerous but powerful) ---
        if data["type"] == "EXECUTE_CODE":
            code_to_run = data["code"]
            
            # We need to import Transaction here so the AI code can use it
            from Autodesk.Revit.DB import Transaction
            
            # This 'exec' command runs the text Claude sent as real code
            exec(code_to_run)
            response["data"] = "Code executed successfully."

        # --- OPTION B: READ DATA ---
        elif data["type"] == "READ_DATA":
            query = data["query"]
            
            if query == "get_all_walls":
                walls = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
                info = ["Wall ID: " + str(w.Id) + " Name: " + w.Name for w in walls]
                response["data"] = info
                
            elif query == "get_project_info":
                response["data"] = {"Title": doc.Title, "Path": doc.PathName}
            
            else:
                response["data"] = "Unknown Query"

    except Exception as e:
        response["status"] = "error"
        response["data"] = str(e)

    # 3. Write Response back to Claude
    with open(RESPONSE_FILE, 'w') as f:
        json.dump(response, f)

    # 4. Delete the command file so we don't run it twice
    os.remove(BRIDGE_FILE)
    print("AI Command Processed: " + response["status"])

# Run the function
main()