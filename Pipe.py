"""This file acts as the main module for this script."""

import traceback
import adsk.core
import adsk.fusion

# Initialize the global variables for the Application and UserInterface objects.
app = adsk.core.Application.get()
ui = app.userInterface

def run(_context: str):
    """This function is called by Fusion when the script is run."""

    try:
        # Get the active design
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox('No active design found!')
            return

        # Get the root component
        root_comp = design.rootComponent

        # Define pipe parameters
        outer_diameter = 2.0  # mm (outer diameter)
        wall_thickness = 0.2   # mm (wall thickness)
        inner_diameter = outer_diameter - 2 * wall_thickness  # mm (inner diameter)
        pipe_length = 100.0   # mm
        pipe_profile = 'round' # or 'square'

        # Create a sketch on the XY plane for the pipe profile
        sketches = root_comp.sketches
        xy_plane = root_comp.xYConstructionPlane
        pipe_sketch = sketches.add(xy_plane)

        # Draw the pipe profile (outer and inner circles for a hollow pipe)
        if pipe_profile == 'round':
            center_point = adsk.core.Point3D.create(0, 0, 0)
            # Outer circle
            outer_circle = pipe_sketch.sketchCurves.sketchCircles.addByCenterRadius(center_point, outer_diameter / 2)
            # Inner circle
            inner_circle = pipe_sketch.sketchCurves.sketchCircles.addByCenterRadius(center_point, inner_diameter / 2)
        else:
            ui.messageBox('Only round profiles are supported in this version.')
            return

        # Extrude the sketch to create a hollow 3D pipe
        extrudes = root_comp.features.extrudeFeatures
        profile = pipe_sketch.profiles.item(0)  # Area between outer and inner circles
        extrude_input = extrudes.createInput(profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        distance = adsk.core.ValueInput.createByReal(pipe_length / 10)  # Convert mm to cm
        extrude_input.setDistanceExtent(False, distance)
        extrude = extrudes.add(extrude_input)

        # Create a new sketch for cut paths (on the same XY plane)
        cut_sketch = sketches.add(xy_plane)

        # Add cut paths (outer and inner perimeters as cut lines)
        if pipe_profile == 'round':
            # Outer cut path
            outer_cut = cut_sketch.sketchCurves.sketchCircles.addByCenterRadius(center_point, outer_diameter / 2)
            # Inner cut path
            inner_cut = cut_sketch.sketchCurves.sketchCircles.addByCenterRadius(center_point, inner_diameter / 2)

        # Show success message
        ui.messageBox('Success! Hollow pipe with cut paths created.\nPlease use File > Export to save the cut sketch as DXF manually.')

    except:  #pylint:disable=bare-except
        # Write the error message to the TEXT COMMANDS window.
        app.log(f'Failed:\n{traceback.format_exc()}')
        ui.messageBox(f'Error: {traceback.format_exc()}')