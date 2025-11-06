import pandas as pd
import hashlib
from flask import Flask, render_template, request, send_file
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def normalize_email(email):
    if pd.isna(email):
        return ""
    return str(email).strip().lower()

def normalize_phone(phone):
    if pd.isna(phone):
        return ""
    phone = str(phone).replace(" ", "").replace("-", "")
    if phone.startswith("0"):
        phone = phone[1:]
    if not phone.startswith("+"):
        phone = "+91" + phone
    return phone

def sha256_hash(data):
    if data == "":
        return ""
    return hashlib.sha256(data.encode()).hexdigest()

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files["file"]

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        df = pd.read_csv(filepath)

        df["email"] = df["email"].apply(normalize_email)
        df["phone"] = df["phone"].apply(normalize_phone)

        df["email"] = df["email"].apply(sha256_hash)
        df["phone"] = df["phone"].apply(sha256_hash)

        df = df.drop(columns=["email", "phone"])

        output_file = os.path.join(OUTPUT_FOLDER, "hashed_output.csv")
        df.to_csv(output_file, index=False)

        return render_template("index.html", success=True, download="hashed_output.csv")

    return render_template("index.html")
    
@app.route("/download/<filename>")
def download_file(filename):
    return send_file(os.path.join(OUTPUT_FOLDER, filename), as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)

