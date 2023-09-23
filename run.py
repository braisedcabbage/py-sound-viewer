from flask import Flask, request, send_from_directory, after_this_request
from flask_cors import CORS
import os
import subprocess

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "/Users/savvadmitriev/Documents/py-sound-viewer"
app.config['WTF_CSRF_ENABLED'] = False
CORS(app)


@app.route('/', methods=['GET'])
#def idk():
  #  print("HELLO")
   # return 'PRIVET'


@app.route('/', methods=['POST'])
def upload_file():
    print("Request received mtf")
    if 'f' in request.files:
        file = request.files['f']
        filename = file.filename[:-4]
        mode = request.form.get('mode', 'bars')  # получение режима, с 'bars' в качестве значения по умолчанию
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename + ".wav"))

        # Выполнение скриптов после загрузки файла
        subprocess.call(["sh", "convert_to_stereo.sh", filename])
        subprocess.call(["python3", "main.py", "-m", mode, "-c", "#ddddff", "--output", filename + "_stereo"])
        subprocess.call(["sh", "add_audio_to_video.sh", "-a", filename + "_stereo", "-v", filename + "_stereo"])

        # Удаление промежуточных файлов
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename + '.wav'))
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename + "_stereo.wav"))
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename + "_stereo.mp4"))

        @after_this_request
        def remove_file(response):
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename + "_stereo_processed.mp4"))
            except Exception as error:
                app.logger.error("Error removing or closing downloaded file handle", error)
            return response
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename + "_stereo_processed.mp4", as_attachment=True)


try:
    with open(os.path.join(app.config['UPLOAD_FOLDER'], 'testfile'), 'w') as f:
        pass
    print('Directory is writable')
except PermissionError:
    print('Directory is not writable')

if __name__ == '__main__':
    app.run(debug=True)