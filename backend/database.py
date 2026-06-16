import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tasks.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create tasks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'active',
            priority TEXT DEFAULT 'medium',
            due_date TEXT,
            category TEXT DEFAULT 'Personal',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create subtasks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subtasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()

def get_tasks():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch all tasks
    cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
    tasks = [dict(row) for row in cursor.fetchall()]
    
    # Fetch subtasks for each task
    for task in tasks:
        cursor.execute("SELECT * FROM subtasks WHERE task_id = ?", (task['id'],))
        task['subtasks'] = [dict(row) for row in cursor.fetchall()]
        
    conn.close()
    return tasks

def create_task(title, description='', priority='medium', due_date=None, category='Personal'):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tasks (title, description, priority, due_date, category)
        VALUES (?, ?, ?, ?, ?)
    ''', (title, description, priority, due_date, category))
    task_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return task_id

def update_task(task_id, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    fields = []
    values = []
    
    allowed_fields = ['title', 'description', 'status', 'priority', 'due_date', 'category']
    for field in allowed_fields:
        if field in data:
            fields.append(f"{field} = ?")
            values.append(data[field])
            
    if not fields:
        conn.close()
        return False
        
    values.append(task_id)
    query = f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?"
    cursor.execute(query, values)
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success

def delete_task(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Delete associated subtasks first
    cursor.execute("DELETE FROM subtasks WHERE task_id = ?", (task_id,))
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success

def create_subtask(task_id, title):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO subtasks (task_id, title)
        VALUES (?, ?)
    ''', (task_id, title))
    subtask_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return subtask_id

def update_subtask(subtask_id, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE subtasks SET status = ? WHERE id = ?", (status, subtask_id))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success

def delete_subtask(subtask_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM subtasks WHERE id = ?", (subtask_id,))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success

def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM tasks")
    total_tasks = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'completed'")
    completed_tasks = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'active'")
    active_tasks = cursor.fetchone()[0]
    
    # Priority counts
    cursor.execute("SELECT priority, COUNT(*) FROM tasks GROUP BY priority")
    priority_counts = {row['priority']: row[1] for row in cursor.fetchall()}
    
    # Category counts
    cursor.execute("SELECT category, COUNT(*) FROM tasks GROUP BY category")
    category_counts = {row['category']: row[1] for row in cursor.fetchall()}
    
    conn.close()
    return {
        'total': total_tasks,
        'completed': completed_tasks,
        'active': active_tasks,
        'by_priority': priority_counts,
        'by_category': category_counts
    }
