# 🎯 ParkKar Slot Detection Microservice (Python + OpenCV)

_Real-time AI-powered parking slot detection and MJPEG streaming microservice for the ParkKar smart parking platform._

---

## 🚀 Overview

This microservice powers the **AI-based detection** and **live video streaming** component of the ParkKar system. It uses OpenCV to analyze parking lot video feeds and determine slot occupancy status. Results are streamed visually and communicated in real-time to the main Node.js backend for live updates via WebSocket.

---

## 🔍 Features

- 🧠 **AI Slot Detection** using OpenCV (based on adaptive thresholding & region monitoring)
- 🎥 **MJPEG Live Stream** with frame-by-frame video piping to the browser
- 📡 **Slot Update API** to send live status to the central server
- 🧰 Built with **FastAPI** for fast, async-compatible routing
- 📦 Docker-compatible and deployable as a microservice

---

## 🛠️ Tech Stack

| Layer         | Tools / Tech           |
|---------------|------------------------|
| Server        | FastAPI                |
| Detection     | OpenCV, NumPy          |
| Stream Format | MJPEG (`multipart/x-mixed-replace`) |
| Inter-service | REST (via `requests`)  |
| Packaging     | Docker-ready           |
| Python        | 3.10+ (pref. 3.11)     |

---

## 📁 Project Structure

parkkar-slotdetection-microservice/
├── app/
│ ├── main.py # FastAPI routes
│ ├── detection/
│ │ ├── runner.py # Script runner logic
│ │ └── scripts/ # One script per parking lot
│ ├── utils/
│ │ └── notifier.py # Sends POST request to Node backend
├── Dockerfile
├── requirements.txt
├── README.md



🔗 Main App Repo: [ParkKar](https://github.com/Dhruvv245/ParkKar)

This microservice is part of the full ParkKar ecosystem. For the frontend, real-time updates, and dashboards, refer to the main repository. 🚗💡


uvicorn app.main:app --host 0.0.0.0 --port 8000