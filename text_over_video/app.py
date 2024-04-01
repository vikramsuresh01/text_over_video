from flask import Flask, render_template, request, redirect, url_for, send_from_directory, send_file
import cv2
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'mp4'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# Function to check if the file has an allowed extension
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to add text to video
def add_text_to_video(video_path, text, position='top_left', color='#FFFFFF'):
    cap = cv2.VideoCapture(video_path)

    # Get the width and height of the video
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Define the codec and create VideoWriter object
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], 'output_video.mp4')
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, 20.0, (width, height))

    while True:
        ret, frame = cap.read()

        if ret:
            font = cv2.FONT_HERSHEY_SIMPLEX

            # Calculate text position based on user input
            if 'left' in position:
                text_x = 50
            elif 'right' in position:
                text_x = width - len(text) * 20 - 50
            else:  # For center positions
                text_x = (width - len(text) * 20) // 2

            if 'top' in position:
                text_y = 50
            elif 'bottom' in position:
                text_y = height - 50
            else:  # For center positions
                text_y = height // 2

            # Convert color from hex to BGR tuple
            color_bgr = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))

            # Add text with specified color
            cv2.putText(frame, text, (text_x, text_y), font, 1, color_bgr, 2, cv2.LINE_4)
            out.write(frame)
        else:
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            text = request.form['text']
            position = request.form.get('position', 'top_left')  # Default to 'top_left' if not provided
            color = request.form.get('color', '#FFFFFF')  # Default to white color if not provided

            add_text_to_video(file_path, text, position, color)

            # Redirect the user to the correct URL for downloading the modified video
            return redirect(url_for('output_file'))
    return render_template('upload.html')

@app.route('/output/output_video.mp4')
def output_file():
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], 'output_video.mp4')
    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    # Ensure the output directory exists
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    app.run(debug=True)
