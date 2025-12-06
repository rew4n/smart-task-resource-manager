from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Smart Task & Resource Manager is running 🚀"

if __name__ == "__main__":
    app.run(debug=True)
