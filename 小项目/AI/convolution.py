import sys
import argparse
import os
from PIL import Image
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models

def build_model(num_layers):
    model = models.Sequential()
    model.add(layers.Input(shape=(128, 128, 3)))
    for i in range(num_layers):
        model.add(layers.Conv2D(16, (3, 3), activation='relu', padding='same', name=f'conv_{i+1}'))
    return model

def load_and_preprocess_image(image_path):
    img = Image.open(image_path).convert('RGB')
    img = img.resize((128, 128))
    img_array = np.array(img) / 255.0
    return np.expand_dims(img_array, axis=0)

def save_feature_maps(feature_map, base_filename, layer_num):
    fmap = feature_map[0]  # remove batch dimension
    for i in range(fmap.shape[-1]):
        channel = fmap[:, :, i]
        channel = (channel - channel.min()) / (channel.max() - channel.min() + 1e-5)  # normalize to 0-1
        img = Image.fromarray(np.uint8(channel * 255))
        filename = f"{base_filename}_conv{layer_num}_channel{i}.png"
        img.save(filename)
        print(f"Saved: {filename}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("images", nargs='+', help="Input image files")
    parser.add_argument("--layers", type=int, default=1, help="Convolutional layer to extract (1-based index)")
    args = parser.parse_args()

    model = build_model(args.layers)
    intermediate_layer_model = models.Model(inputs=model.input, outputs=model.layers[args.layers - 1].output)

    for image_file in args.images:
        img_input = load_and_preprocess_image(image_file)
        feature_map = intermediate_layer_model.predict(img_input)
        
        base, ext = os.path.splitext(image_file)
        save_feature_maps(feature_map, base, args.layers)

if __name__ == "__main__":
    main()
