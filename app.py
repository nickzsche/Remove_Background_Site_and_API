from flask import Flask, request, render_template, send_file
from rembg import remove
import os
import uuid
import time
import threading

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {"png", "jpg", "jpeg", "gif"}

def cleanup_uploaded_files():
    while True:
        for filename in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(file_path) and time.time() - os.path.getctime(file_path) > 30:
                os.remove(file_path)
        time.sleep(60)  # Her 60 saniyede bir kontrol et

@app.route("/", methods=["GET", "POST"])
def remove_background():
    if request.method == "POST":
        if "image" not in request.files:
            return "No image provided", 400

        image_file = request.files["image"]

        if image_file.filename == '' or not allowed_file(image_file.filename):
            return "Invalid file type. Please select a .png, .jpg, .jpeg, or .gif file.", 400

        image = image_file.read()
        output_image = remove(image)

        unique_filename = str(uuid.uuid4()) + ".png"  # Uzantıyı .png olarak ayarlayın

        temp_filename = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)

        with open(temp_filename, "wb") as temp_file:
            temp_file.write(output_image)

        return render_template("result.html", temp_filename=unique_filename)

    return render_template("index.html")

@app.route("/download/<filename>")
def download(filename):
    try:
        return send_file(os.path.join(app.config["UPLOAD_FOLDER"], filename), as_attachment=True)
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    # Temizlik işlemini başlatan bir thread oluşturun
    cleanup_thread = threading.Thread(target=cleanup_uploaded_files)
    cleanup_thread.daemon = True
    cleanup_thread.start()

    # Flask uygulamasını çalıştır
    app.run(debug=True)
