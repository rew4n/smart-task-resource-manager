from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, date
from functools import wraps

app = Flask(__name__)
app.secret_key = "dev-secret"  # keep for now (later move to env var)

# Hardcoded demo user
DEMO_USER = {
    "username": "admin",
    "password": "123"
}

# SQLite database stored in project folder as tasks.db
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.Date, nullable=True)
    done = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create tables once when app starts (better than before_request)
with app.app_context():
    db.create_all()

def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        # Strict: must be logged in as DEMO_USER
        if session.get("user") != DEMO_USER["username"]:
            flash("Please log in first.")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapper

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if username == DEMO_USER["username"] and password == DEMO_USER["password"]:
            session.clear()  # prevents weird “old session data” issues
            session["user"] = username
            flash("Logged in successfully.")
            return redirect(url_for("tasks"))
        else:
            flash("Invalid username or password.")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.")
    return redirect(url_for("home"))

@app.route("/tasks", methods=["GET", "POST"])
@login_required
def tasks():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()

        due_date_raw = request.form.get("due_date", "").strip()
        due_date = date.fromisoformat(due_date_raw) if due_date_raw else None

        if title:
            db.session.add(Task(title=title, description=description, due_date=due_date))
            db.session.commit()

        return redirect(url_for("tasks"))

    today = date.today()
    due_soon_cutoff = today + timedelta(days=3)

    all_tasks = Task.query.order_by(
        Task.due_date.is_(None),
        Task.due_date.asc(),
        Task.created_at.desc()
    ).all()

    return render_template(
        "tasks.html",
        tasks=all_tasks,
        today=today,
        due_soon_cutoff=due_soon_cutoff
    )

@app.route("/tasks/<int:task_id>/toggle", methods=["POST"])
@login_required
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.done = not task.done
    db.session.commit()
    return redirect(url_for("tasks"))

@app.route("/tasks/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("tasks"))

@app.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        due_date_raw = request.form.get("due_date", "").strip()
        due_date = date.fromisoformat(due_date_raw) if due_date_raw else None

        if not title:
            flash("Title cannot be empty.")
            return redirect(url_for("edit_task", task_id=task.id))

        task.title = title
        task.description = description
        task.due_date = due_date
        db.session.commit()

        flash("Task updated.")
        return redirect(url_for("tasks"))

    return render_template("edit_task.html", task=task)

if __name__ == "__main__":
    app.run(debug=True)
