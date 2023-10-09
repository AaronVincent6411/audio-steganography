from flask import Flask, render_template, request, redirect, url_for, send_file
import os

app = Flask(__name__)

app.config['OUTPUT_FOLDER'] = 'static/output'


@app.route('/', methods=['GET', 'POST'])
def index():
    result = ""

    if request.method == 'POST':
        audio_file = request.files['audio_file']
        secret_message = request.form['secret_message']

        if audio_file and allowed_file(audio_file.filename):
            # Process the audio file and hide the message
            # Implement your echo hiding logic here
            result = "Message successfully hidden in audio."
            # Save the modified audio file
            modified_audio_path = os.path.join(app.config['OUTPUT_FOLDER'], 'modified_audio.wav')
            # Use your echo hiding logic to create the modified audio file
            # For example: modify_audio(audio_file, secret_message, modified_audio_path)

    return render_template('index.html', result=result)


@app.route('/download')
def download():
    # Provide a link to download the modified audio file
    modified_audio_path = os.path.join(app.config['OUTPUT_FOLDER'], 'modified_audio.wav')
    return send_file(modified_audio_path, as_attachment=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'wav'}


if __name__ == '__main__':
    app.run(debug=True)