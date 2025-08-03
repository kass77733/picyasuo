from flask import Flask, request, render_template, send_from_directory
from PIL import Image
import io
import os
import time
import platform
 
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
 
 
def resize_image(image, target_width, target_height):
    width, height = image.size
    if width / height > target_width / target_height:
        new_height = int(height * target_width / width)
        new_width = target_width
    else:
        new_width = int(width * target_height / height)
        new_height = target_height
    return image.resize((new_width, new_height), Image.LANCZOS)
 
 
@app.route('/', methods=['GET', 'POST'])
def index():
    output_file = None
    if request.method == 'POST':
        if 'image' not in request.files:
            return render_template('index.html', error='No file part')
        image_file = request.files['image']
        if image_file.filename == '':
            return render_template('index.html', error='No file selected')
        if image_file:
            try:
                image = Image.open(io.BytesIO(image_file.read()))
                image = image.convert('RGB')
                scale_enabled = request.form.get('scale_enabled')
                target_resolution_str = request.form.get('target_resolution')
                if scale_enabled and target_resolution_str:
                    try:
                        target_width_str, target_height_str = target_resolution_str.split('*')
                        target_width = int(target_width_str)
                        target_height = int(target_height_str)
                        image = resize_image(image, target_width, target_height)
                    except ValueError:
                        return render_template('index.html', error='请输入正确格式的分辨率参数（格式如：宽度*高度）。')
                else:
                    target_width = None
                    target_height = None
                if target_width is not None and target_height is not None:
                    # 创建一个具有目标分辨率的BufferedImage
                    new_image = Image.new('RGB', (target_width, target_height), (255, 255, 255))  # 白色背景
                    x = (target_width - image.size[0]) // 2
                    y = (target_height - image.size[1]) // 2
                    new_image.paste(image, (x, y))
                    image = new_image
 
                file_name = f'lo_{time.strftime("%Y%m%d%H%M%S")}.webp'
                output_file = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
                image.save(output_file, format='webp', quality=80)
                return render_template('index.html', success=f"图片已成功压缩并保存为: {file_name}", output_file=file_name)
            except Exception as e:
                return render_template('index.html', error=f"操作失败: {e}")
    return render_template('index.html', output_file=output_file)
 
 
@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
 
 
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
