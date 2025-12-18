from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Temporary in-memory storage (later we’ll replace with SQLite)
TASKS = []

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/tasks", methods=["GET", "POST"])
def tasks():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        if title:
            TASKS.append({"title": title, "done": False})
        return redirect(url_for("tasks"))

    return render_template("tasks.html", tasks=TASKS)

if __name__ == "__main__":
    app.run(debug=True)
