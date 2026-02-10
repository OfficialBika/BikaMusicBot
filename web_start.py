import os
import signal
import subprocess
import threading
import time

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

PORT = int(os.getenv("PORT", "10000"))

app = FastAPI()

@app.get("/")
async def root():
    return JSONResponse({"ok": True, "service": "BikaMusicBot"})

@app.get("/health")
async def health():
    return JSONResponse({"ok": True})

def run_web():
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")

def main():
    # 1) Start web server in a thread (keeps Render happy: PORT listening)
    t = threading.Thread(target=run_web, daemon=True)
    t.start()

    # 2) Start the actual bot using repo's start script
    # Yukki-style repos commonly have "bash start"
    bot_proc = subprocess.Popen(["bash", "start"])

    # 3) Handle shutdown signals cleanly
    def shutdown(*_):
        try:
            bot_proc.terminate()
        except Exception:
            pass

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    # 4) Wait for bot process to exit
    while True:
        code = bot_proc.poll()
        if code is not None:
            # Bot exited -> keep web alive a bit and then exit (Render will restart)
            time.sleep(2)
            break
        time.sleep(1)

if __name__ == "__main__":
    main()
