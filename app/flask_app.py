from flask import Flask, request, render_template, flash
from agents import CrewAIAgentFlow
import os
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = "secretKey"
app.config['UPLOAD_FOLDER'] = './uploads'

client = MongoClient(os.getenv("MONGO_URI", "mongodb://mongodb:27017/"))
db = client.sensitive_datastore
collection = db.sensitive_data

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == 'POST':
        if 'filename' not in request.files:
            flash("no file part in the request")
            return render_template("index.html")

        file = request.files['filename']

        if file.filename == '':
            flash("no file selected")
            return render_template("index.html")

        if file:
            file_content = file.read().decode('utf-8')
            result = CrewAIAgentFlow(file_content)

            document = {
                "filename": file.filename,
                "output1": str(result['classification-res']),
                "output2": str(result['sensitive_fields_res']),
                "timestamp": datetime.utcnow(),
            }

            collection.insert_one(document)

            return render_template(
                "output.html", 
                output1 = str(result['classification-res']),
                output2 = str(result['sensitive_fields_res'])
            )
    return render_template("index.html")


@app.route("/entries", methods=["GET"])
def show_entries():
    documents = list(collection.find({}, {"filename": 1, "output1": 1,"output2": 1, "timestamp": 1}))
    return render_template("entries.html", entries=documents)

@app.route("/delete/<id>", methods=["POST"])
def delete_entry(id):
    try:
        x = collection.delete_one({"_id": ObjectId(id)})
        if x.deleted_count > 0:
            flash(f"file {id} deleted successfully")
        else:
            flash(f"file {id} not found!")

    except Exception as e:
        flash(f"Error deleting entry: {e}")

    return show_entries()

# if __name__ == "__main__":
#     app.run(debug=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)