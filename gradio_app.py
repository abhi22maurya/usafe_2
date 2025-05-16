import gradio as gr
import numpy as np
import tensorflow as tf
from tensorflow import keras

# Create a placeholder model (in a real scenario, you would load a trained model)
def create_model():
    model = keras.Sequential([
        keras.layers.Dense(16, activation='relu', input_shape=(5,)),
        keras.layers.Dense(8, activation='relu'),
        keras.layers.Dense(4, activation='relu'),
        keras.layers.Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

# Load or create the model
model = create_model()

def predict_landslide(rainfall, slope, soil_type, vegetation, elevation):
    # Normalize inputs
    rainfall_norm = rainfall / 1000
    slope_norm = slope / 90
    soil_type_norm = soil_type / 3
    vegetation_norm = vegetation / 100
    elevation_norm = elevation / 5000
    
    # Create input array
    input_data = np.array([[rainfall_norm, slope_norm, soil_type_norm, vegetation_norm, elevation_norm]])
    
    # Make prediction
    prediction = model.predict(input_data)[0][0]
    
    # Return formatted result
    risk_level = "High" if prediction > 0.7 else "Medium" if prediction > 0.3 else "Low"
    return {
        "Probability": f"{prediction:.2%}",
        "Risk Level": risk_level,
        "Recommendations": get_recommendations(risk_level)
    }

def get_recommendations(risk_level):
    if risk_level == "High":
        return [
            "Immediate evacuation recommended",
            "Monitor weather conditions closely",
            "Contact local authorities",
            "Prepare emergency supplies"
        ]
    elif risk_level == "Medium":
        return [
            "Stay alert for weather changes",
            "Prepare evacuation plan",
            "Monitor local alerts",
            "Secure loose objects"
        ]
    else:
        return [
            "Regular monitoring recommended",
            "Maintain emergency preparedness",
            "Stay informed about weather updates",
            "Review evacuation routes"
        ]

# Create Gradio interface
with gr.Blocks(title="Landslide Risk Prediction") as demo:
    gr.Markdown("# Landslide Risk Prediction System")
    gr.Markdown("Enter the environmental parameters to assess landslide risk")
    
    with gr.Row():
        with gr.Column():
            rainfall = gr.Slider(0, 1000, label="Rainfall (mm)")
            slope = gr.Slider(0, 90, label="Slope Angle (degrees)")
            soil_type = gr.Radio(
                ["Sandy", "Clay", "Rocky"],
                label="Soil Type"
            )
            vegetation = gr.Slider(0, 100, label="Vegetation Cover (%)")
            elevation = gr.Slider(0, 5000, label="Elevation (m)")
            
            submit_btn = gr.Button("Predict Risk")
        
        with gr.Column():
            output = gr.JSON(label="Prediction Results")
    
    submit_btn.click(
        fn=predict_landslide,
        inputs=[rainfall, slope, soil_type, vegetation, elevation],
        outputs=output
    )

if __name__ == "__main__":
    demo.launch() 