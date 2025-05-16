import * as tf from '@tensorflow/tfjs';

// Create a simple sequential model
const createModel = () => {
  const model = tf.sequential();
  
  // Input layer
  model.add(tf.layers.dense({
    units: 16,
    activation: 'relu',
    inputShape: [5] // 5 input features: rainfall, slope, soil type, vegetation, elevation
  }));
  
  // Hidden layers
  model.add(tf.layers.dense({units: 8, activation: 'relu'}));
  model.add(tf.layers.dense({units: 4, activation: 'relu'}));
  
  // Output layer
  model.add(tf.layers.dense({
    units: 1,
    activation: 'sigmoid' // Binary classification: 0 (no landslide) or 1 (landslide)
  }));
  
  // Compile the model
  model.compile({
    optimizer: 'adam',
    loss: 'binaryCrossentropy',
    metrics: ['accuracy']
  });
  
  return model;
};

// Function to preprocess input data
const preprocessInput = (data) => {
  // Normalize input features
  const normalizedData = {
    rainfall: data.rainfall / 1000, // Assuming max rainfall is 1000mm
    slope: data.slope / 90, // Assuming max slope is 90 degrees
    soilType: data.soilType / 3, // Assuming 3 soil types
    vegetation: data.vegetation / 100, // Assuming vegetation cover percentage
    elevation: data.elevation / 5000 // Assuming max elevation is 5000m
  };
  
  return tf.tensor2d([
    [
      normalizedData.rainfall,
      normalizedData.slope,
      normalizedData.soilType,
      normalizedData.vegetation,
      normalizedData.elevation
    ]
  ]);
};

// Function to predict landslide probability
const predictLandslide = async (model, inputData) => {
  const inputTensor = preprocessInput(inputData);
  const prediction = model.predict(inputTensor);
  const probability = await prediction.data();
  return probability[0];
};

export { createModel, predictLandslide }; 