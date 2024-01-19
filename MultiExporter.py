import adsk.core, adsk.fusion, adsk.cam, traceback
import os

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

        # Get the current selection
        selection = ui.activeSelections

        # Ask the user to select a folder for the exported STL files
        folder_dialog = ui.createFolderDialog()
        folder_dialog.title = "Select destination folder" 
        
        result = folder_dialog.showDialog()
        if result != adsk.core.DialogResults.DialogOK:
            return

        destination = folder_dialog.folder
     
        def create_path(body):
            return body.name

        # Iterate over selected bodies
        for item in selection:
            body = adsk.fusion.BRepBody.cast(item.entity)


            if body: 
                path = create_path(body)
                path = os.path.join(destination, path) + '.stl'

                # Set the options for export
                manager = adsk.fusion.ExportManager.cast(app.activeProduct.exportManager)
                export_options = manager.createSTLExportOptions(body)
                export_options.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementMedium
                export_options.filename = path

                # Export the body
                manager.execute(export_options)

        ui.messageBox('Done')
    
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
