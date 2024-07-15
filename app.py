from flask import Flask, render_template, request, send_file, redirect, url_for
from werkzeug.utils import secure_filename
import albumentations as A
import cv2
import os
from glob import glob
import zipfile
import io
import shutil

app = Flask(__name__)

# Define individual augmentation transformations
transforms = {
    'rotate': A.Rotate(limit=40, p=1.0),
    'hflip': A.HorizontalFlip(p=1.0),
    'vflip': A.VerticalFlip(p=1.0),
    'brighter': A.RandomBrightnessContrast(brightness_limit=(0.2, 0.4), contrast_limit=0, p=1.0),
    'darker': A.RandomBrightnessContrast(brightness_limit=(-0.4, -0.2), contrast_limit=0, p=1.0),
    'rgb_shift': A.RGBShift(r_shift_limit=20, g_shift_limit=20, b_shift_limit=20, p=1.0),
    'hue_saturation_value': A.HueSaturationValue(hue_shift_limit=20, sat_shift_limit=30, val_shift_limit=20, p=1.0)
}

# Configuration for file uploads
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['AUGMENTED_FOLDER'] = 'augmented'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def augment_image(image, transformation):
    augmented = transformation(image=image)
    return augmented['image']

def load_images_from_folder(folder_path):
    image_paths = glob(os.path.join(folder_path, '*'))
    images = []
    for path in image_paths:
        image = cv2.imread(path)
        if image is not None:
            images.append((path, image))
    return images

def save_augmented_images(images, output_folder):
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder)
    
    for path, image in images:
        filename = os.path.basename(path).split('.')[0]
        image_output_folder = os.path.join(output_folder, filename)
        if not os.path.exists(image_output_folder):
            os.makedirs(image_output_folder)
        for aug_name, transformation in transforms.items():
            augmented_image = augment_image(image, transformation)
            output_path = os.path.join(image_output_folder, f"{filename}_{aug_name}.jpg")
            cv2.imwrite(output_path, augmented_image)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'photo' not in request.files:
            return redirect(request.url)
        files = request.files.getlist('photo')
        if not files or files[0].filename == '':
            return redirect(request.url)
        
        # Clear the uploads folder
        if os.path.exists(app.config['UPLOAD_FOLDER']):
            shutil.rmtree(app.config['UPLOAD_FOLDER'])
        os.makedirs(app.config['UPLOAD_FOLDER'])
        
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
        
        return redirect(url_for('augment'))
    return render_template('index.html')

@app.route('/augment', methods=['GET'])
def augment():
    images = load_images_from_folder(app.config['UPLOAD_FOLDER'])
    if not images:
        return "No images found in the upload folder.", 400
    save_augmented_images(images, app.config['AUGMENTED_FOLDER'])
    return redirect(url_for('download'))

@app.route('/download', methods=['GET'])
def download():
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for foldername, subfolders, filenames in os.walk(app.config['AUGMENTED_FOLDER']):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                zf.write(file_path, os.path.relpath(file_path, app.config['AUGMENTED_FOLDER']))
    memory_file.seek(0)
    return send_file(memory_file, download_name='augmented_images.zip', as_attachment=True)

if __name__ == '__main__':
    # Ensure necessary folders exist
    for folder in [app.config['UPLOAD_FOLDER'], app.config['AUGMENTED_FOLDER']]:
        if not os.path.exists(folder):
            os.makedirs(folder)
    app.run(debug=True)
