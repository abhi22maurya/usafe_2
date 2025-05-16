import gradio as gr
import numpy as np

# Placeholder model (replace with trained TensorFlow model)
def predict_landslide(elevation, slope, rainfall):
    # Simulated risk calculation
    risk = (elevation / 5000 + slope / 90 + rainfall / 500) / 3
    return f"Landslide Risk: {risk:.2%}"

interface = gr.Interface(
    fn=predict_landslide,
    inputs=[
        gr.Slider(0, 5000, label="Elevation (m)"),
        gr.Slider(0, 90, label="Slope (degrees)"),
        gr.Slider(0, 500, label="Rainfall (mm)"),
    ],
    outputs="text",
    title="UttarakhandSafe Landslide Predictor"
)

interface.launch()