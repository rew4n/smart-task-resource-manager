from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, date
from functools import wraps

app = Flask(__name__)
app.secret_key = "dev-secret"  # move to env var in production

# Demo user (for learning purposes)
DEMO_USER = {
    "username": "admin",
    "password": "123"
}

# Database config
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# --------------------
# Models
# --------------------
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.String(80), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.Date)
    done = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


def init_db():
    with app.app_context():
        db.create_all()


# --------------------
# Auth helpers
# --------------------
def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            flash("Please log in first.")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapper


# --------------------
# Routes (HTML)
# --------------------
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if username == DEMO_USER["username"] and password == DEMO_USER["password"]:
            session.clear()
            session["user"] = username
            flash("Logged in successfully.")
            return redirect(url_for("tasks"))

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
        due_date_raw = request.form.get("due_date", "")
        due_date = date.fromisoformat(due_date_raw) if due_date_raw else None

        if title:
            db.session.add(Task(
                owner=session["user"],
                title=title,
                description=description,
                due_date=due_date
            ))
            db.session.commit()

        return redirect(url_for("tasks"))

    today = date.today()
    due_soon_cutoff = today + timedelta(days=3)

    tasks = Task.query.filter_by(owner=session["user"]).order_by(
        Task.due_date.is_(None),
        Task.due_date.asc(),
        Task.created_at.desc()
    ).all()

    return render_template(
        "tasks.html",
        tasks=tasks,
        today=today,
        due_soon_cutoff=due_soon_cutoff
    )


@app.route("/tasks/<int:task_id>/toggle", methods=["POST"])
@login_required
def toggle_task(task_id):
    task = Task.query.filter_by(id=task_id, owner=session["user"]).first_or_404()
    task.done = not task.done
    db.session.commit()
    return redirect(url_for("tasks"))


@app.route("/tasks/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id, owner=session["user"]).first_or_404()
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("tasks"))


@app.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    task = Task.query.filter_by(id=task_id, owner=session["user"]).first_or_404()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        due_date_raw = request.form.get("due_date", "")
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


# --------------------
# API (JSON)
# --------------------
@app.route("/api/tasks", methods=["GET"])
@login_required
def api_get_tasks():
    tasks = Task.query.filter_by(owner=session["user"]).order_by(
        Task.created_at.desc()
    ).all()

    return {
        "tasks": [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "due_date": t.due_date.isoformat() if t.due_date else None,
                "done": t.done,
                "created_at": t.created_at.isoformat()
            }
            for t in tasks
        ]
    }


@app.route("/api/tasks", methods=["POST"])
@login_required
def api_create_task():
    data = request.get_json()
    if not data or not data.get("title"):
        return {"error": "Title is required"}, 400

    due_date = date.fromisoformat(data["due_date"]) if data.get("due_date") else None

    task = Task(
        owner=session["user"],
        title=data["title"],
        description=data.get("description", ""),
        due_date=due_date
    )

    db.session.add(task)
    db.session.commit()

    return {"message": "Task created", "task_id": task.id}, 201


@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
@login_required
def api_update_task(task_id):
    task = Task.query.filter_by(id=task_id, owner=session["user"]).first_or_404()
    data = request.get_json()

    for field in ["title", "description", "done"]:
        if field in data:
            setattr(task, field, data[field])

    if "due_date" in data:
        task.due_date = date.fromisoformat(data["due_date"]) if data["due_date"] else None

    db.session.commit()
    return {"message": "Task updated"}


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
@login_required
def api_delete_task(task_id):
    task = Task.query.filter_by(id=task_id, owner=session["user"]).first_or_404()
    db.session.delete(task)
    db.session.commit()
    return {"message": "Task deleted"}


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
