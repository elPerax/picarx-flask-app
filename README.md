# 🌐 Picar-X Flask Dashboard  

**Course:** Internet of Things 2 (IoT 2) – Fall 2025  
**Student:** Samuel Reyes Cifuentes  
**Institution:** Champlain College Saint-Lambert  

---

## 🚀 Project Overview

This repository contains the **Flask-based web dashboard** used to interact with the **VisionTrack-X PiCarX robot**.  
The dashboard provides a full cloud-connected interface to:

- Monitor the rover in **real time**  
- Visualize **historical telemetry** from Neon PostgreSQL  
- Remotely control **motors, steering, camera, and TTS**

This app is the **visualization & control layer** of the IoT pipeline:

> **Sense → Publish (MQTT) → Store → Sync → Visualize → Control**

The PiCarX handles **sensing + MQTT**,  
the Flask app handles **visualization + remote control**.

---


## 🔗 Related Repository (Full PiCar-X System)

👉 **Main PiCar-X Project Repository:**  
https://github.com/elPerax/Picar-X-v2.0-IoT-Smart-Robot-Car

This Flask dashboard is the *cloud & visualization component* of that full system.

---

## 🎥 Youtube video Link for Milestome 3
https://www.youtube.com/watch?v=Gjl8jm351ow

---

## 🧠 Features Implemented

### ✅ Live Sensor Dashboard
- Real-time **ultrasonic distance** graph  
- Real-time **grayscale mid-value** graph  
- Shows the **latest TTS message** spoken by the robot  
- Data pulled directly from **Adafruit IO REST API**

### ✅ Historical Data Visualization
- Plots **ultrasonic** and **grayscale** telemetry stored in **Neon PostgreSQL**  
- Date range selection / filtering  
- Uses **Chart.js** for interactive, responsive graphs  

### ✅ Remote Robot Controls
- **Motor control:** forward / backward / stop  
- **Steering control:** left / right / center  
- **Camera control:** pan / tilt  
- **Text-to-Speech:** send phrases to the robot  
- **Line tracking:** start / stop  
- **Obstacle avoidance:** start / stop  

Commands are sent through **Adafruit IO command feeds**.

### ✅ About Page
- Overview of **hardware + software stack**  
- Short descriptions of **team members** (no personal photos)  
- Includes the **official VisionTrack-X car photo**

### ✅ Modern UI (Final-Project Ready)
- Custom **dark theme** (`style.css`)  
- Hero banner with **logo + car image**  
- Centered layout, clean typography, responsive design  
- Fully deployable on **Render**

---

## ⚙️ System Architecture (Dashboard Perspective)

```text
Sensors (Ultrasonic, Grayscale, TTS)
        ↓
 Adafruit IO Feeds (MQTT / REST)
        ↓
   Flask Web Dashboard (Render)
        ↓
Neon PostgreSQL (Historical Data)
        ↓
Robot Control → Commands published to AIO feeds

PiCar-X Robot
    → publishes live values → Adafruit IO
            ↓
Flask Dashboard (this repo)
    → reads live values from Adafruit IO
    → reads historical logs from Neon
    → sends control commands back to AIO
```

##  📁 Directory Structure
```picarx-flask-app/
├── static/
│   ├── css/
│   │   └── style.css           # Full UI theme
│   ├── js/
│   │   ├── charts_ultra.js     # Ultrasonic historical charts
│   │   └── charts_gray.js      # Grayscale historical charts
│   └── img/                    # Car / logo images
│
├── templates/
│   ├── base.html               # Navbar + shared layout
│   ├── home.html               # Live dashboard
│   ├── about.html              # About page
│   ├── sensor_data.html
│   ├── charts_ultra.html
│   ├── charts_gray.html
│   ├── control_motors.html
│   ├── control_steering.html
│   ├── camera.html
│   ├── tts_control.html
│   ├── line_tracking.html
│   └── obstacle.html
│
├── app.py                      # Flask routes + Neon + AIO integration
├── requirements.txt            # Python dependencies
├── runtime.txt                 # Python version (for Render)
├── Procfile                    # Gunicorn startup command
└── .gitignore                  # .env and other local-only files
```
## 🔧 Configuration
Create a .env file (not committed to Git) with:
```AIO_USERNAME=your_adafruit_username
AIO_KEY=your_adafruit_key

AIO_ULTRASONIC_FEED=ultrasonic_distance
AIO_GRAYSCALE_MID_FEED=grayscale_mid
AIO_TTS_FEED=tts
AIO_COMMAND_FEED=picarx-command
AIO_STEERING_FEED=steering-command
AIO_CAMERA_FEED=camera-command

PG_DSN=postgresql://username:password@host:5432/dbname?sslmode=require
```

## 🧩 How to Run Locally

```# 1️⃣ Clone the repository
git clone https://github.com/<yourname>/picarx-flask-app.git
cd picarx-flask-app

# 2️⃣ Create and activate a virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate

# macOS / Linux:
# source venv/bin/activate

# 3️⃣ Install dependencies
pip install -r requirements.txt

# 4️⃣ Create `.env` file (see configuration section)

# 5️⃣ Run the Flask app
python app.py
Then open the dashboard in your browser:

text
Copy code
http://127.0.0.1:5000
```
## 🌐 Deployment on Render

This repo is ready for Render:

✔ Procfile included

✔ runtime.txt included

✔ Gunicorn entrypoint configured

Deployment steps:

Push this repository to GitHub.

In Render, create a new Web Service.

Connect it to this repo and select the correct branch (e.g. main).

Add all environment variables from the .env section.

Click Deploy.

Render will:

Use the Python version from runtime.txt

Install packages from requirements.txt

Start the app using Gunicorn (command in Procfile)

After each commit, you can either rely on Auto Deploys or trigger a Manual Deploy → Latest Commit.

## 📊 Example Live Data (as seen on the dashboard)
Timestamp:      2025-11-30 23:51:10
Ultrasonic:     42 cm
Grayscale Mid:  533
Last TTS:       "Hello, this is VisionTrack-X!"

## 🧰 Tools & Libraries

Flask – Web server framework

requests – HTTP client for Adafruit IO REST API

Chart.js – Front-end charting library

Gunicorn – Production WSGI server (Render)

Neon PostgreSQL – Cloud database for historical data

Render – Hosting platform + CI/CD

## 🧠 Reflection


Working on the VisionTrack-X Flask Dashboard was the final step in bringing the entire IoT ecosystem together.  
Throughout this project, I built both sides of the system:

- The **hardware & sensing layer** (PiCar-X robot, sensors, actuators)  
- The **cloud & visualization layer** (Flask dashboard, Adafruit IO, Neon)  

Because of this, I got to fully understand how an IoT solution works from end to end.

The first part of the project — wiring, calibrating, and coding the PiCar-X — was extremely hands-on.  
I built scripts to control ultrasonic sensing, grayscale line tracking, DHT11 measurements, TTS audio, servo steering, and motor movement.  
I also configured MQTT publishing to Adafruit IO, structured local CSV logging, and automated nightly uploads to Google Drive.  
This stage forced me to deeply understand hardware behavior, sensor timing, asynchronous events, and the constraints of real devices.

The Flask dashboard represented the second half of the ecosystem.  
Here, the challenge shifted from hardware to **software architecture and cloud integration**.  
I had to make a UI that felt like a real control interface—not a school assignment—and integrate it with:

- Adafruit IO REST APIs (live sensor values + command feeds)  
- Neon PostgreSQL (historical logs)  
- A responsive front-end (Chart.js, CSS)  
- Flask routes, templates, and cloud deployment via Render  

This required careful planning: handling JSON payloads, ensuring the charts updated cleanly, preventing broken layouts, and keeping everything responsive.  
Building the control pages (motors, steering, camera, TTS, line tracking, obstacle avoidance) taught me how to design a safe, reliable command interface that would not accidentally send repeated or conflicting signals to the robot.

What made this dashboard meaningful is that I had already completed the PiCar-X hardware system.  
I wasn’t just designing a UI — I was building the missing half of a connected IoT product.  
Seeing the robot publish data through MQTT, watching the dashboard plot that same data, and then sending commands back from the dashboard to the robot completed the full loop:

**Device → Cloud → Dashboard → Device**

This final stage made everything click.  
It showed me how real-world IoT devices use multiple layers — hardware, networking, cloud storage, APIs, and visualization — to create a complete system.  
By the end, the VisionTrack-X ecosystem felt like a coherent product:  
the sensing scripts, logging pipeline, MQTT feeds, cloud database, and dashboard all worked together seamlessly.

Overall, this project helped me understand IoT not just as “a robot with sensors,” but as an integrated system made up of hardware, software, cloud pipelines, and user-facing dashboards.  
It was challenging, but seeing the robot respond to cloud commands and watching live values graph in real time made the entire process extremely rewarding.
