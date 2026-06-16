import subprocess
import time
import urllib.request
import urllib.error
import json
import os
import sys

def run_tests():
    print("=== STARTING BACKEND INTEGRATION TESTS ===")
    
    # Define test database path and ensure it starts clean
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', 'tasks.db')
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print("Cleaned up existing database for testing.")
        except Exception as e:
            print(f"Could not remove database file: {e}")

    # Start Flask server in subprocess on a test-specific port (5001)
    # We override the port using environment variables or modify the run call
    env = os.environ.copy()
    env["FLASK_APP"] = "backend/app.py"
    
    print("Starting Flask server on port 5001...")
    server_process = subprocess.Popen(
        [sys.executable, "-c", "import sys; sys.path.append('backend'); from app import app; app.run(port=5001, debug=False, use_reloader=False)"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    time.sleep(2.0)
    
    base_url = "http://127.0.0.1:5001"
    
    try:
        # Helper for HTTP requests
        def make_request(path, method="GET", data=None):
            url = f"{base_url}{path}"
            req_data = None
            headers = {}
            if data is not None:
                req_data = json.dumps(data).encode('utf-8')
                headers = {"Content-Type": "application/json"}
            
            req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
            with urllib.request.urlopen(req) as response:
                return response.status, json.loads(response.read().decode('utf-8'))

        # Test 1: GET /api/tasks (expect empty list)
        print("Test 1: Get initial tasks...")
        status, body = make_request("/api/tasks")
        assert status == 200, f"Expected 200, got {status}"
        assert isinstance(body, list), "Expected list of tasks"
        assert len(body) == 0, f"Expected 0 tasks, got {len(body)}"
        print("[OK] Test 1 passed: Initial task list is empty.")

        # Test 2: POST /api/tasks (create task)
        print("Test 2: Create a task...")
        task_payload = {
            "title": "Buy groceries",
            "description": "Milk, eggs, and bread",
            "priority": "high",
            "category": "Shopping",
            "due_date": "2026-12-31"
        }
        status, body = make_request("/api/tasks", method="POST", data=task_payload)
        assert status == 201, f"Expected 201, got {status}"
        assert "id" in body, "Expected task ID in response"
        task_id = body["id"]
        print(f"[OK] Test 2 passed: Task created with ID {task_id}.")

        # Test 3: GET /api/tasks (verify task properties)
        print("Test 3: Fetch tasks and verify details...")
        status, body = make_request("/api/tasks")
        assert status == 200
        assert len(body) == 1
        created_task = body[0]
        assert created_task["id"] == task_id
        assert created_task["title"] == "Buy groceries"
        assert created_task["priority"] == "high"
        assert created_task["category"] == "Shopping"
        assert created_task["status"] == "active"
        print("[OK] Test 3 passed: Task details verified successfully.")

        # Test 4: POST /api/tasks/<id>/subtasks (add subtask)
        print("Test 4: Add a subtask...")
        subtask_payload = {"title": "Buy 1L Whole Milk"}
        status, body = make_request(f"/api/tasks/{task_id}/subtasks", method="POST", data=subtask_payload)
        assert status == 201
        assert "id" in body
        subtask_id = body["id"]
        print(f"[OK] Test 4 passed: Subtask created with ID {subtask_id}.")

        # Test 5: GET /api/tasks (verify subtask is nested)
        print("Test 5: Verify nested subtasks...")
        status, body = make_request("/api/tasks")
        assert status == 200
        task_with_subtask = body[0]
        assert "subtasks" in task_with_subtask
        assert len(task_with_subtask["subtasks"]) == 1
        subtask = task_with_subtask["subtasks"][0]
        assert subtask["id"] == subtask_id
        assert subtask["title"] == "Buy 1L Whole Milk"
        assert subtask["status"] == "active"
        print("[OK] Test 5 passed: Subtask nested successfully.")

        # Test 6: PUT /api/subtasks/<id> (toggle subtask status)
        print("Test 6: Toggle subtask completion...")
        status, body = make_request(f"/api/subtasks/{subtask_id}", method="PUT", data={"status": "completed"})
        assert status == 200
        
        # Verify subtask status updated
        _, body = make_request("/api/tasks")
        assert body[0]["subtasks"][0]["status"] == "completed"
        print("[OK] Test 6 passed: Subtask toggled to completed.")

        # Test 7: GET /api/stats (verify statistics API)
        print("Test 7: Fetch stats dashboard API...")
        status, body = make_request("/api/stats")
        assert status == 200
        assert body["total"] == 1
        assert body["active"] == 1
        assert body["completed"] == 0
        assert body["by_priority"]["high"] == 1
        assert body["by_category"]["Shopping"] == 1
        print("[OK] Test 7 passed: Dashboard statistics API verified.")

        # Test 8: PUT /api/tasks/<id> (complete task)
        print("Test 8: Toggle main task completion...")
        status, body = make_request(f"/api/tasks/{task_id}", method="PUT", data={"status": "completed"})
        assert status == 200
        
        # Verify stats updated
        _, body = make_request("/api/stats")
        assert body["active"] == 0
        assert body["completed"] == 1
        print("[OK] Test 8 passed: Main task completed.")

        # Test 9: DELETE /api/tasks/<id> (delete task and verify cascading delete)
        print("Test 9: Delete task...")
        status, body = make_request(f"/api/tasks/{task_id}", method="DELETE")
        assert status == 200
        
        # Verify empty
        _, body = make_request("/api/tasks")
        assert len(body) == 0
        print("[OK] Test 9 passed: Task deleted successfully.")
        
        print("\n=== ALL BACKEND INTEGRATION TESTS PASSED SUCCESSFULLY! ===")
        
    except AssertionError as e:
        print(f"\n[ERROR] TEST FAILURE: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] UNEXPECTED ERROR RUNNING TESTS: {e}")
        sys.exit(1)
    finally:
        print("Stopping Flask test server...")
        server_process.terminate()
        server_process.wait()
        
        # Clean up database file after test
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
                print("Cleaned up database file after test run.")
            except Exception as e:
                print(f"Could not clean database: {e}")

if __name__ == "__main__":
    run_tests()
