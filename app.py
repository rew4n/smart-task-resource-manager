from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/tasks")
def tasks():
    # temporary fake tasks
    task_list = [
        {"id": 1, "title": "Buy groceries", "status": "pending"},
        {"id": 2, "title": "Finish Flask project", "status": "in progress"},
        {"id": 3, "title": "Clean the house", "status": "completed"}
    ]
    return render_template("tasks.html", tasks=task_list)

if __name__ == "__main__":
    app.run(debug=True)
