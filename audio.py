from flask import Flask, render_template, request, send_file
import os
import wave

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'static/output'

# Here we are checking whether folder exists else we create a new one
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

#This is the function which hides message into audio
def hide_message(input_audio, secret_message, output_audio):
    waveaudio = wave.open(input_audio, mode='rb')
    frame_bytes = bytearray(list(waveaudio.readframes(waveaudio.getnframes())))
    secret_message = secret_message + int((len(frame_bytes)-(len(secret_message)*8*8))/8) *'#'
    bits = list(map(int, ''.join([bin(ord(i)).lstrip('0b').rjust(8,'0') for i in secret_message])))
    for i, bit in enumerate(bits):
        frame_bytes[i] = (frame_bytes[i] & 254) | bit
    frame_modified = bytes(frame_bytes)
    with wave.open(output_audio, 'wb') as fd:
        fd.setparams(waveaudio.getparams())
        fd.writeframes(frame_modified)
    waveaudio.close()


@app.route('/')
def index():
    return render_template('main.html')


@app.route('/hide', methods=['POST'])
def upload_file():
    #Here we asks the user to input audio file and message
    uploaded_file = request.files['audio_file']
    secret_message = request.form['secret_message']

    if uploaded_file.filename != '':
        # Here we save the uploaded file
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
        uploaded_file.save(audio_path)

        # Here we create external path to output audio and pass the input audio , secret message and output path to hide_message function
        output_audio_path = os.path.join(app.config['OUTPUT_FOLDER'], 'modified_audio.wav')
        hide_message(audio_path, secret_message, output_audio_path)

        modified_audio_path = os.path.join(app.config['OUTPUT_FOLDER'], 'modified_audio.wav')

        # After hiding we provide a link to download the modified audio
        return send_file(modified_audio_path, as_attachment=True)

#Extract function
@app.route('/extract', methods=['POST'])
def extract_message():
    uploaded_file = request.files['audio_file']
    audio_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
    uploaded_file.save(audio_path)

    waveaudio = wave.open(audio_path, mode='rb')
    frame_bytes = bytearray(list(waveaudio.readframes(waveaudio.getnframes())))
    extracted = [frame_bytes[i] & 1 for i in range(len(frame_bytes))]
    string = "".join(chr(int("".join(map(str,extracted[i:i+8])),2)) for i in range(0,len(extracted),8))
    msg = string.split("###")[0]
    waveaudio.close()

    if not msg or not msg.isprintable():
        return " "

    return f"{msg}"

if __name__ == '__main__':
    app.run(debug=True)

