from flask import Flask, request, jsonify
import database

app = Flask(__name__, static_folder="../frontend", static_url_path="")

# Initialize the database on startup
database.init_db()

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/api/tasks", methods=["GET", "POST"])
def manage_tasks():
    try:
        if request.method == "POST":
            data = request.json or {}
            if 'title' not in data:
                return jsonify({"error": "Missing title"}), 400
            
            task_id = database.create_task(
                title=data['title'],
                description=data.get('description', ''),
                due_date=data.get('due_date'),
                category=data.get('category', 'Personal')
            )
            return jsonify({"id": task_id, "message": "Created"}), 201
            
        return jsonify(database.get_tasks())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/tasks/<int:task_id>", methods=["PUT", "DELETE"])
def alter_task(task_id):
    try:
        if request.method == "DELETE":
            if database.delete_task(task_id):
                return jsonify({"message": "Deleted"})
            return jsonify({"error": "Not found"}), 404
            
        data = request.json or {}
        if database.update_task(task_id, data):
            return jsonify({"message": "Updated"})
        return jsonify({"error": "Not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/tasks/<int:task_id>/subtasks", methods=["POST"])
def add_subtask(task_id):
    try:
        data = request.json or {}
        if 'title' not in data:
            return jsonify({"error": "Missing subtask title"}), 400
        
        subtask_id = database.create_subtask(task_id, data['title'])
        return jsonify({"id": subtask_id, "message": "Subtask created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/subtasks/<int:subtask_id>", methods=["PUT", "DELETE"])
def manage_subtask(subtask_id):
    try:
        if request.method == "DELETE":
            if database.delete_subtask(subtask_id):
                return jsonify({"message": "Deleted"})
            return jsonify({"error": "Not found"}), 404
            
        data = request.json or {}
        if 'status' not in data:
            return jsonify({"error": "Missing status"}), 400
            
        if database.update_subtask(subtask_id, data['status']):
            return jsonify({"message": "Updated"})
        return jsonify({"error": "Not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
