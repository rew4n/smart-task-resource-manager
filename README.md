# Smart Task & Resource Manager – API Documentation

## Overview

This project provides a RESTful JSON API for managing tasks.
The API is built using Flask, SQLAlchemy, and SQLite, and supports full CRUD operations.

Authentication is session-based (single demo user for now).

Base URL
http://127.0.0.1:5000

## Authentication

User must be logged in before accessing protected endpoints

Demo credentials:

Username: admin
Password: 123


Login via: POST /login


Sessions are used to identify the logged-in user.

## API Endpoints

Get all tasks
GET /api/tasks

Returns all tasks belonging to the logged-in user.

Response (200 OK):

[
  {
    "id": 1,
    "title": "Finish Flask project",
    "description": "Add API and login system",
    "due_date": "2025-12-20",
    "done": false,
    "created_at": "2025-12-18T14:30:00"
  }
]

Create a new task
POST /api/tasks

Request Body (JSON):

{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "due_date": "2025-12-22"
}


Response (201 Created):

{
  "message": "Task created successfully"
}

Update a task
PUT /api/tasks/<task_id>

Request Body (JSON):

{
  "title": "Buy groceries (updated)",
  "description": "Milk, eggs, bread, fruit",
  "due_date": "2025-12-23",
  "done": true
}


Response (200 OK):

{
  "message": "Task updated successfully"
}

Delete a task
DELETE /api/tasks/<task_id>

Response (200 OK):

{
  "message": "Task deleted successfully"
}

## Security Notes

All API routes are protected by session-based authentication

Tasks are filtered by the logged-in user (owner)

Users cannot access or modify other users’ tasks

## Technologies Used

Python 3

Flask

Flask-SQLAlchemy

SQLite

HTML / Jinja2

Git & GitHub

## Future Improvements

Token-based authentication (JWT)

Multiple users

Pagination and filtering

Frontend client using the API

Deployment to cloud (Render / Railway / AWS)