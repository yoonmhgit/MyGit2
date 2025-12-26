from flask import Flask, render_template, request, send_file, jsonify
import os
from werkzeug.utils import secure_filename
import io
import base64
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
from datetime import datetime

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

CAMERA_PROFILES = {
    'arri': {
        'name': 'ARRI Alexa',
        'color_matrix': [1.05, 0.98, 1.02],
        'contrast': 1.1,
        'saturation': 1.15,
        'description': 'ARRI Alexa natural color profile'
    },
    'red': {
        'name': 'RED Digital Cinema',
        'color_matrix': [1.08, 0.95, 1.05],
        'contrast': 1.15,
        'saturation': 1.2,
        'description': 'RED high contrast profile'
    },
    'canon': {
        'name': 'Canon Cinema',
        'color_matrix': [1.03, 1.02, 0.98],
        'contrast': 1.05,
        'saturation': 1.1,
        'description': 'Canon warm tone profile'
    },
    'sony': {
        'name': 'Sony Venice',
        'color_matrix': [1.02, 1.0, 1.03],
        'contrast': 1.08,
        'saturation': 1.12,
        'description': 'Sony balanced profile'
    },
    'blackmagic': {
        'name': 'Blackmagic',
        'color_matrix': [1.0, 1.0, 1.0],
        'contrast': 1.0,
        'saturation': 1.05,
        'description': 'Blackmagic flat profile'
    }
}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def apply_brightness(image, value):
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(value)


def apply_contrast(image, value):
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(value)


def apply_saturation(image, value):
    enhancer = ImageEnhance.Color(image)
    return enhancer.enhance(value)


def apply_sharpness(image, value):
    enhancer = ImageEnhance.Sharpness(image)
    return enhancer.enhance(value)


def apply_temperature(image, value):
    img_array = np.array(image)
    
    if len(img_array.shape) == 2:
        return image
    
    img_array = img_array.astype(float)
    
    if value > 0:
        img_array[:, :, 0] = np.clip(img_array[:, :, 0] * (1 + value * 0.5), 0, 255)
        img_array[:, :, 2] = np.clip(img_array[:, :, 2] * (1 - value * 0.3), 0, 255)
    else:
        img_array[:, :, 0] = np.clip(img_array[:, :, 0] * (1 + value * 0.3), 0, 255)
        img_array[:, :, 2] = np.clip(img_array[:, :, 2] * (1 - value * 0.5), 0, 255)
    
    img_array = img_array.astype(np.uint8)
    return Image.fromarray(img_array)


def apply_hsl(image, hue=0, saturation=0, lightness=0):
    img_array = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2HSV).astype(float)
    
    if hue != 0:
        img_array[:, :, 0] = (img_array[:, :, 0] + hue) % 180
    
    if saturation != 0:
        img_array[:, :, 1] = np.clip(img_array[:, :, 1] * (1 + saturation), 0, 255)
    
    if lightness != 0:
        img_array[:, :, 2] = np.clip(img_array[:, :, 2] * (1 + lightness), 0, 255)
    
    img_array = img_array.astype(np.uint8)
    img_rgb = cv2.cvtColor(img_array, cv2.COLOR_HSV2RGB)
    return Image.fromarray(img_rgb)


def apply_camera_profile(image, profile_name):
    if profile_name not in CAMERA_PROFILES:
        return image
    
    profile = CAMERA_PROFILES[profile_name]
    
    img_array = np.array(image).astype(float)
    
    if len(img_array.shape) == 3:
        color_matrix = profile['color_matrix']
        img_array[:, :, 0] = np.clip(img_array[:, :, 0] * color_matrix[0], 0, 255)
        img_array[:, :, 1] = np.clip(img_array[:, :, 1] * color_matrix[1], 0, 255)
        img_array[:, :, 2] = np.clip(img_array[:, :, 2] * color_matrix[2], 0, 255)
    
    img = Image.fromarray(img_array.astype(np.uint8))
    
    img = apply_contrast(img, profile['contrast'])
    img = apply_saturation(img, profile['saturation'])
    
    return img


@app.route('/')
def index():
    return render_template('index.html', camera_profiles=CAMERA_PROFILES)


@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        try:
            image = Image.open(file.stream)
            
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            max_size = (1920, 1080)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            buffered = io.BytesIO()
            image.save(buffered, format='JPEG', quality=95)
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return jsonify({
                'success': True,
                'image': f'data:image/jpeg;base64,{img_str}',
                'width': image.width,
                'height': image.height
            })
        except Exception as e:
            return jsonify({'error': f'Failed to process image: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400


@app.route('/process', methods=['POST'])
def process_image():
    try:
        data = request.json
        image_data = data.get('image', '').split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        adjustments = data.get('adjustments', {})
        
        if 'brightness' in adjustments and adjustments['brightness'] != 1.0:
            image = apply_brightness(image, adjustments['brightness'])
        
        if 'contrast' in adjustments and adjustments['contrast'] != 1.0:
            image = apply_contrast(image, adjustments['contrast'])
        
        if 'saturation' in adjustments and adjustments['saturation'] != 1.0:
            image = apply_saturation(image, adjustments['saturation'])
        
        if 'sharpness' in adjustments and adjustments['sharpness'] != 1.0:
            image = apply_sharpness(image, adjustments['sharpness'])
        
        if 'temperature' in adjustments and adjustments['temperature'] != 0:
            image = apply_temperature(image, adjustments['temperature'])
        
        hue = adjustments.get('hue', 0)
        hsl_saturation = adjustments.get('hsl_saturation', 0)
        lightness = adjustments.get('lightness', 0)
        
        if hue != 0 or hsl_saturation != 0 or lightness != 0:
            image = apply_hsl(image, hue, hsl_saturation, lightness)
        
        if 'camera_profile' in adjustments and adjustments['camera_profile']:
            image = apply_camera_profile(image, adjustments['camera_profile'])
        
        buffered = io.BytesIO()
        image.save(buffered, format='JPEG', quality=95)
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'image': f'data:image/jpeg;base64,{img_str}'
        })
    
    except Exception as e:
        return jsonify({'error': f'Failed to process image: {str(e)}'}), 500


@app.route('/download', methods=['POST'])
def download_image():
    try:
        data = request.json
        image_data = data.get('image', '').split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'edited_image_{timestamp}.jpg'
        
        return send_file(
            io.BytesIO(image_bytes),
            mimetype='image/jpeg',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        return jsonify({'error': f'Failed to download image: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
