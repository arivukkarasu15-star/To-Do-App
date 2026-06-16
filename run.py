import sys
import os
import threading
import time
import subprocess
import webbrowser

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

def find_browser_exe(name):
    roots = [
        r"C:\Program Files",
        r"C:\Program Files (x86)",
        os.path.expandvars(r"%LocalAppData%")
    ]
    search_dirs = []
    for r in roots:
        if name == "chrome.exe":
            search_dirs.append(os.path.join(r, "Google"))
        elif name == "msedge.exe":
            search_dirs.append(os.path.join(r, "Microsoft"))
        elif name == "brave.exe":
            search_dirs.append(os.path.join(r, "BraveSoftware"))
            
    for s_dir in search_dirs:
        if not os.path.exists(s_dir):
            continue
        for root, dirs, files in os.walk(s_dir):
            if name in files:
                return os.path.join(root, name)
    return None

def open_app_mode():
    time.sleep(1.0) # Wait for Flask server to initialize
    url = "http://127.0.0.1:5000"
    
    # Try opening Chromium browsers in standalone app mode
    browsers = ["brave.exe", "chrome.exe", "msedge.exe"]
    for browser in browsers:
        path = find_browser_exe(browser)
        if path:
            try:
                subprocess.Popen([path, f"--app={url}"])
                return
            except Exception:
                pass
                
    # Fallback to default browser tab
    webbrowser.open(url)

def main():
    # Launch browser window in a background daemon thread
    threading.Thread(target=open_app_mode, daemon=True).start()
    
    # Run the Flask app in the main thread.
    # The heartbeat monitor in backend/app.py will call os._exit(0) when the window is closed,
    # shutting down this process and cleaning up.
    import app as backend_app
    backend_app.app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)

if __name__ == "__main__":
    main()
