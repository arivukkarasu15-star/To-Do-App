# Tick-IT — Task Manager

A simple offline task manager built with a Python Flask backend and a clean flat slate HTML/CSS/JS frontend.

## Features

- **Flat Slate UI**: Simple, clean dark slate design with FontAwesome icons.
- **Standalone App Window**: Launches in app mode via Chrome/Brave/Edge so it feels like a native desktop app.
- **Subtask Checklists**: Break tasks down into smaller items.
- **Categories**: Filter tasks by Personal, Work, Shopping, Health, and Ideas.
- **Automatic Lifecycle Control**: Server starts/stops automatically when the desktop window is opened or closed.

## Tech Stack

- **Backend**: Python 3, Flask, SQLite3
- **Frontend**: HTML5, CSS3, Vanilla ES6 JavaScript, FontAwesome 6

## How to Run

1. Install requirements:
   ```bash
   pip install Flask
   ```
2. Start the app:
   ```bash
   python run.py
   ```
   This will launch the app in standalone Chromium mode.

## REST API

- `GET /api/tasks` - Get all tasks
- `POST /api/tasks` - Create task
- `PUT /api/tasks/<id>` - Update task details/status
- `DELETE /api/tasks/<id>` - Delete task
- `POST /api/tasks/<id>/subtasks` - Create subtask
- `PUT /api/subtasks/<id>` - Toggle subtask status
- `DELETE /api/subtasks/<id>` - Delete subtask
- `GET /api/heartbeat` - Server heartbeat ping
