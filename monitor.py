import argparse
import psutil
import time
import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import smtplib
from email.mime.text import MIMEText

# -------------------- Configuration for Alerts -------------------- #
CPU_THRESHOLD = 90
MEMORY_THRESHOLD = 80
DISK_THRESHOLD = 90
NETWORK_THRESHOLD = 100  # MB

# Email configuration
FROM_EMAIL = "your-email@gmail.com"
FROM_PASSWORD = "your-app-password"
TO_EMAIL = "target-user@example.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# To avoid sending duplicate emails
already_alerted = {
    "cpu": False,
    "memory": False,
    "disk": False,
    "network_sent": False,
    "network_recv": False
}

def send_email(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = TO_EMAIL

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(FROM_EMAIL, FROM_PASSWORD)
        server.send_message(msg)

# -------------------- FastAPI WebSocket (GUI) -------------------- #
app = FastAPI()

html = """
<!DOCTYPE html>
<html>
<head>
    <title>Linux Monitor (Real-Time)</title>
    <meta http-equiv="refresh" content="10">
    <style>
        body { font-family: Arial, sans-serif; background-color: #f0f2f5; text-align: center; }
        h1 { color: #333; }
        #data { margin-top: 20px; font-size: 18px; }
        .alert { color: white; background-color: red; padding: 10px; border-radius: 5px; margin-top: 20px; }
        .normal { color: green; font-size: 20px; margin-top: 20px; }
    </style>
</head>
<body>
    <h1>🔍 Real-Time Linux Monitoring Tool</h1>
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

        message = ""
        alert_active = False

        message += f"CPU Usage: {cpu}%\\n"
        message += f"Memory Usage: {memory}%\\n"
        message += f"Disk Usage: {disk}%\\n"
        message += f"Bytes Sent: {net.bytes_sent / (1024 * 1024):.2f} MB\\n"
        message += f"Bytes Received: {net.bytes_recv / (1024 * 1024):.2f} MB\\n"

        # Check and send alerts
        if cpu > CPU_THRESHOLD and not already_alerted["cpu"]:
            send_email("⚠️ CPU ALERT", f"CPU usage exceeded {CPU_THRESHOLD}%: Currently at {cpu}%")
            already_alerted["cpu"] = True
            alert_active = True
            message += "\\nALERT: CPU Usage exceeded!"

        if memory > MEMORY_THRESHOLD and not already_alerted["memory"]:
            send_email("⚠️ Memory ALERT", f"Memory usage exceeded {MEMORY_THRESHOLD}%: Currently at {memory}%")
            already_alerted["memory"] = True
            alert_active = True
            message += "\\nALERT: Memory Usage exceeded!"

        if disk > DISK_THRESHOLD and not already_alerted["disk"]:
            send_email("⚠️ Disk ALERT", f"Disk usage exceeded {DISK_THRESHOLD}%: Currently at {disk}%")
            already_alerted["disk"] = True
            alert_active = True
            message += "\\nALERT: Disk Usage exceeded!"

        if (net.bytes_sent / (1024 * 1024)) > NETWORK_THRESHOLD and not already_alerted["network_sent"]:
            send_email("⚠️ Network Sent ALERT", f"Network bytes sent exceeded {NETWORK_THRESHOLD}MB")
            already_alerted["network_sent"] = True
            alert_active = True
            message += "\\nALERT: Network Sent exceeded!"

        if (net.bytes_recv / (1024 * 1024)) > NETWORK_THRESHOLD and not already_alerted["network_recv"]:
            send_email("⚠️ Network Received ALERT", f"Network bytes received exceeded {NETWORK_THRESHOLD}MB")
            already_alerted["network_recv"] = True
            alert_active = True
            message += "\\nALERT: Network Received exceeded!"

        if alert_active:
            message = "<div class='alert'>" + message.replace("\\n", "<br>") + "</div>"
        else:
            message = "<div class='normal'>✅ All Systems Normal</div>"

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
