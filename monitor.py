import argparse
import psutil
import time
import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

# -------------------- Configuration for Alerts -------------------- #
# Set threshold values for alerts
CPU_THRESHOLD = 90
MEMORY_THRESHOLD = 80
DISK_THRESHOLD = 90
NETWORK_THRESHOLD = 100  # MB of network usage (change as per requirements)

# -------------------- FastAPI WebSocket (GUI) -------------------- #
app = FastAPI()

html = """
<!DOCTYPE html>
<html>
<head>
    <title>Linux Monitor (Real-Time)</title>
</head>
<body>
    <h1>Real-Time Linux Monitoring Tool</h1>
    <div id="data"></div>
    
    <script>
        var ws = new WebSocket("ws://localhost:6100/ws");
        ws.onmessage = function(event) {
            document.getElementById('data').innerHTML = event.data.replace(/\\n/g, '<br>');
        };
    </script>
</body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        net = psutil.net_io_counters()
        
        message = (
            f"CPU Usage: {cpu}%\n"
            f"Memory Usage: {memory}%\n"
            f"Disk Usage: {disk}%\n"
            f"Bytes Sent: {net.bytes_sent / (1024 * 1024):.2f} MB\n"
            f"Bytes Received: {net.bytes_recv / (1024 * 1024):.2f} MB\n"
        )
        
        # Trigger alerts in WebSocket if thresholds are crossed
        if cpu > CPU_THRESHOLD:
            message += f"ALERT: CPU Usage EXCEEDED {CPU_THRESHOLD}%\n"
        if memory > MEMORY_THRESHOLD:
            message += f"ALERT: Memory Usage EXCEEDED {MEMORY_THRESHOLD}%\n"
        if disk > DISK_THRESHOLD:
            message += f"ALERT: Disk Usage EXCEEDED {DISK_THRESHOLD}%\n"
        if (net.bytes_sent / (1024 * 1024)) > NETWORK_THRESHOLD:
            message += f"ALERT: Network Sent EXCEEDED {NETWORK_THRESHOLD}MB\n"
        if (net.bytes_recv / (1024 * 1024)) > NETWORK_THRESHOLD:
            message += f"ALERT: Network Received EXCEEDED {NETWORK_THRESHOLD}MB\n"
        
        await websocket.send_text(message)
        await asyncio.sleep(1)

# -------------------- CLI Alert Function -------------------- #
def live_cli_monitor():
    try:
        while True:
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            net = psutil.net_io_counters()
            
            print("\033c", end="")  # Clear screen
            print(f"CPU Usage: {cpu}%")
            print(f"Memory Usage: {memory}%")
            print(f"Disk Usage: {disk}%")
            print(f"Bytes Sent: {net.bytes_sent / (1024 * 1024):.2f} MB")
            print(f"Bytes Received: {net.bytes_recv / (1024 * 1024):.2f} MB")
            
            # Check thresholds and alert in CLI
            if cpu > CPU_THRESHOLD:
                print(f"\033[91mALERT: CPU Usage EXCEEDED {CPU_THRESHOLD}%\033[0m")
            if memory > MEMORY_THRESHOLD:
                print(f"\033[91mALERT: Memory Usage EXCEEDED {MEMORY_THRESHOLD}%\033[0m")
            if disk > DISK_THRESHOLD:
                print(f"\033[91mALERT: Disk Usage EXCEEDED {DISK_THRESHOLD}%\033[0m")
            if (net.bytes_sent / (1024 * 1024)) > NETWORK_THRESHOLD:
                print(f"\033[91mALERT: Network Sent EXCEEDED {NETWORK_THRESHOLD}MB\033[0m")
            if (net.bytes_recv / (1024 * 1024)) > NETWORK_THRESHOLD:
                print(f"\033[91mALERT: Network Received EXCEEDED {NETWORK_THRESHOLD}MB\033[0m")
            
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopped monitoring.")

# -------------------- Main Function -------------------- #
def main():
    parser = argparse.ArgumentParser(description="Linux Monitoring Tool")
    parser.add_argument('--cli', action='store_true', help="Run in CLI mode (live)")
    parser.add_argument('--gui', action='store_true', help="Run in GUI mode (localhost:6100)")
    
    args = parser.parse_args()
    
    if args.cli:
        live_cli_monitor()
    elif args.gui:
        import uvicorn
        uvicorn.run("monitor:app", host="0.0.0.0", port=6100, reload=False)
    else:
        print("Please specify --cli or --gui mode. Use --help for help.")

if __name__ == "__main__":
    main()
