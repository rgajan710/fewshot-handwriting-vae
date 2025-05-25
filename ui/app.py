from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
import torch
from src.models.vae import VAE  # We'll create this
import numpy as np
from PIL import Image

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['GENERATED_FOLDER'] = 'static/generated'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['GENERATED_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_model(language):
    model_path = f'models/vae_{language}.pth'
    model = VAE()
    if os.path.exists(model_path):
        model.load_state_dict(torch.load(model_path))
    model.eval()
    return model

def process_image(image_path):
    image = Image.open(image_path).convert('L')
    image = image.resize((64, 64))
    image = np.array(image) / 255.0
    image = torch.FloatTensor(image).unsqueeze(0).unsqueeze(0)
    return image

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return jsonify({'success': True, 'filename': filename})
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/generate', methods=['POST'])
def generate_font():
    try:
        language = request.form.get('language', 'english')
        image_file = request.files.get('image')
        text = request.form.get('text', '')

        if not image_file:
            return jsonify({'error': 'No image provided'}), 400

        # Save uploaded image
        filename = secure_filename(image_file.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(image_path)

        # Process image
        input_tensor = process_image(image_path)
        
        # Load model and generate font
        model = load_model(language)
        with torch.no_grad():
            generated = model(input_tensor)
            
        # Save generated font
        output_filename = f'generated_{filename}'
        output_path = os.path.join(app.config['GENERATED_FOLDER'], output_filename)
        
        # Convert tensor to image and save
        generated_image = generated.squeeze().numpy() * 255
        generated_image = Image.fromarray(generated_image.astype(np.uint8))
        generated_image.save(output_path)

        return jsonify({
            'success': True,
            'generated_font': output_filename,
            'preview_text': text
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)