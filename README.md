# Linux Monitor - Real-Time CLI + GUI Tool

Linux Monitor is an open-source system monitoring tool for Linux that offers:

✅ Real-time **Command Line Interface (CLI)** monitoring  
✅ Real-time **Graphical User Interface (GUI)** through a web browser (localhost:6100)

Built with **Python**, **FastAPI**, and **psutil**.

---

## 📦 Installation

```bash
git clone https://github.com/your-username/linux-monitor.git
cd linux-monitor
pip install -r requirements.txt
```

---

## 🚀 Usage

### CLI (Command Line Interface)
```bash
python monitor.py --cli
```
- Displays real-time CPU, Memory, Disk, and Network usage directly in your terminal.

### GUI (Web Browser Interface)
```bash
python monitor.py --gui
```
- Opens a web server at [http://localhost:6100](http://localhost:6100).
- Displays real-time system stats with automatic updates.

---

## 🛠 Requirements

- Python 3.8+
- FastAPI
- Uvicorn
- Psutil

Install them using:

```bash
pip install -r requirements.txt
```

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ✨ Author

- GitHub: [your-username](https://github.com/your-username)

Contributions are welcome! Fork it, improve it, and send a pull request 🚀
