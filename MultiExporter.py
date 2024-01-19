import adsk.core, adsk.fusion, adsk.cam, traceback
import os
import json

def load_history():
    history_file = os.path.join(os.path.expanduser("~"), "fusion_export_history.json")
    if os.path.exists(history_file):
        with open(history_file, "r") as file:
            return json.load(file)
    return {}

def save_history(history):
    history_file = os.path.join(os.path.expanduser("~"), "fusion_export_history.json")
    with open(history_file, "w") as file:
        json.dump(history, file)

def select_path(
    ui: adsk.core.UserInterface,
    root: str,
    body: adsk.fusion.BRepBody,
    history: dict
):
    name = body.name

    if name.startswith("$"):
        parts = name[1:].split(" ")
        directory = os.path.join(root, parts[0])        
        os.makedirs(directory, exist_ok=True)
        path = directory + "/" + parts[1] + '.stl' 
        return path, history

    history_id: str = body.parentComponent.id + "_" + name
    directory = root
    
    if (history_id in history):
        directory = os.path.dirname(history[history_id])

    dialog = ui.createFileDialog()
    dialog.title = "Select destination file"
    dialog.initialDirectory = directory
    dialog.initialFilename = name + '.stl'

    result = dialog.showSave()
    if result != adsk.core.DialogResults.DialogOK: 
        return "", history

    history[history_id] = dialog.filename
    return dialog.filename, history

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = app.activeProduct

        # Check if the active design is available
        if not design:
            ui.messageBox('No Design')
            return

        history = load_history()
        
        # Get the current selection
        selection = ui.activeSelections

        # Ask the user to select a root destination folder
        folder_dialog = ui.createFolderDialog()
        folder_dialog.title = "Select root destination folder" 
        
        result = folder_dialog.showDialog()
        if result != adsk.core.DialogResults.DialogOK:
            return

        root = folder_dialog.folder

        # Iterate over selected bodies
        for item in selection:
            body = adsk.fusion.BRepBody.cast(item.entity)

            if body: 
                path, history = select_path(ui, root, body, history) 

                if path is "":
                    continue

                # Set the options for export
                manager = adsk.fusion.ExportManager.cast(app.activeProduct.exportManager)
                export_options = manager.createSTLExportOptions(body, path)
                manager.execute(export_options)

        save_history(history);        
        ui.messageBox('Done')
    
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
