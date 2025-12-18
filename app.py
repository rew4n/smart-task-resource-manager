from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# SQLite database stored in project folder as tasks.db
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    done = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.before_request
def create_tables():
    db.create_all()

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/tasks", methods=["GET", "POST"])
def tasks():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()

        if title:
            db.session.add(Task(title=title, description=description))
            db.session.commit()

        return redirect(url_for("tasks"))

    all_tasks = Task.query.order_by(Task.created_at.desc()).all()
    return render_template("tasks.html", tasks=all_tasks)



@app.route("/tasks/<int:task_id>/toggle", methods=["POST"])
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.done = not task.done
    db.session.commit()
    return redirect(url_for("tasks"))

@app.route("/tasks/<int:task_id>/delete", methods=["POST"])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("tasks"))

@app.route("/tasks/<int:task_id>/edit", methods=["GET"])
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    return render_template("edit_task.html", task=task)

@app.route("/tasks/<int:task_id>/edit", methods=["POST"])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)

    title = request.form.get("title", "").strip()
    if not title:
        flash("Title cannot be empty.")
        return redirect(url_for("edit_task", task_id=task.id))

    task.title = title
    db.session.commit()
    flash("Task updated.")
    return redirect(url_for("tasks"))




if __name__ == "__main__":
    app.secret_key = "dev-secret"  # later you can move this to env var
    app.run(debug=True)
