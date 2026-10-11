import flask, os, io, zipfile, cv2 as cv, numpy as np
import main

app = flask.Flask(__name__)

@app.get("/")
def index():
    return flask.render_template("index.html")

@app.post("/export")
def export():
    file = flask.request.files.get("file")
    if file is None:
        flask.abort(400, "no file")

    if os.path.splitext(file.filename)[1].lower() != ".png":
        flask.abort(400, "file not a .png")

    img = cv.imdecode(np.frombuffer(file.read(), np.uint8), cv.IMREAD_COLOR)
    if img is None:
        flask.abort(400, "could not read image")

    anims = main.getAnimations(img)
    
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for i, frames in enumerate(main.exportAnimations(anims, img, file.filename)):
            gif = io.BytesIO()
            frames[0].save(gif, format="GIF", save_all=True, append_images=frames[1:], duration=83, loop=0, disposal=2)
            zf.writestr(f"{i+1}.gif", gif.getvalue())
    buf.seek(0)

    return flask.send_file(buf, mimetype="application/zip", as_attachment=True, download_name=f"{file.filename}.zip")

if __name__ == "__main__":
    app.run()
