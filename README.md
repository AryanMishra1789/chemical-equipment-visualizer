# Chemical Equipment Parameter Visualizer

A hybrid **Web and Desktop** application for uploading, analyzing, and visualizing chemical equipment data from CSV files. Built with a shared Django REST backend consumed by both a React.js web frontend and a PyQt5 desktop frontend also Provides a downloadable PDF Report in the **Latex format**.

🔗 **Live Demo**: [ec2-13-201-134-135.ap-south-1.compute.amazonaws.com](ec2-13-201-134-135.ap-south-1.compute.amazonaws.com) 

---

## 📋 Features

| Feature | Web (React) | Desktop (PyQt5) |
|---|---|---|
| CSV File Upload | Drag & Drop + Button | File Dialog |
| Data Summary (Stats) | Stat Cards | Stat Cards |
| Chart Visualization | Chart.js Bar Chart | Matplotlib Bar Chart |
| Data Table | Styled HTML Table | QTableWidget |
| Upload History (Last 5) | Sidebar List | Right Panel |
| PDF Report Generation in Latex Format | Download Button | Download Button |
| Basic Authentication | Session Auth | Login Dialog |

---

## 🛠 Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend (Web) | React.js + Chart.js | Interactive charts & tables |
| Frontend (Desktop) | PyQt5 + Matplotlib | Native desktop visualization |
| Backend | Django + Django REST Framework | Common REST API |
| Data Handling | Pandas | CSV parsing & analytics |
| PDF Generation | LaTeX (pdflatex) | Professional PDF reports |
| Database | SQLite | Store last 5 uploaded datasets |
| Version Control | Git & GitHub | Collaboration & submission |

---

## 📁 Project Structure

```
chemical-equipment-visualizer/
├── backend/                    # Django Backend
│   ├── api/
│   │   ├── models.py           # Dataset model
│   │   ├── views.py            # API views (Upload, History, Report)
│   │   ├── urls.py             # API URL routing
│   │   ├── utils.py            # CSV analysis & PDF generation
│   │   └── report_template.tex # LaTeX report template
│   ├── backend/
│   │   ├── settings.py         # Django settings
│   │   └── urls.py             # Root URL config
│   ├── manage.py
│   └── requirements.txt
├── web/                        # React Frontend
│   ├── src/
│   │   ├── App.js              # Main application component
│   │   ├── App.css             # Application styles
│   │   └── index.css           # Global styles & theme
│   └── package.json
├── desktop/                    # PyQt5 Desktop App
│   └── main.py                 # Desktop application
├── sample_equipment_data.csv   # Sample data for testing
└── README.md
```

---

## 🚀 Setup Instructions

### Prerequisites

- **Python 3.9+**
- **Node.js 16+** and npm
- **LaTeX** (MiKTeX on Windows / TexLive on Linux) — required for PDF report generation
- **Git**

---

### 1. Clone the Repository

```bash
git clone https://github.com/AryanMishra1789/chemical-equipment-visualizer.git
cd chemical-equipment-visualizer
```

### 2. Backend Setup (Django)

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create a superuser (for admin access)
python manage.py createsuperuser

# Start the server
python manage.py runserver
```

The backend API will be available at `http://127.0.0.1:8000`.

### 3. Web Frontend Setup (React)

```bash
cd web

# Install dependencies
npm install

# Start development server
npm start
```

The web app will be available at `http://localhost:3000`.

### 4. Desktop Frontend Setup (PyQt5)

```bash
cd desktop

# Install dependencies (if not already in venv)
pip install PyQt5 matplotlib pandas requests

# Run the desktop app
python main.py
```

A login dialog will appear. Enter your Django credentials to proceed.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/upload/` | Upload a CSV file, returns analysis summary |
| `GET` | `/api/history/` | Get last 5 uploaded datasets |
| `GET` | `/api/report/<id>/` | Download PDF report for a dataset |

### Sample API Response (`POST /api/upload/`)

```json
{
  "id": 1,
  "total_equipment": 15,
  "avg_flowrate": 149.61,
  "avg_pressure": 9.90,
  "avg_temperature": 150.07,
  "type_distribution": {
    "Reactor": 4,
    "Pump": 4,
    "Tank": 4,
    "Separator": 3
  },
  "table": [...]
}
```

---

## 📊 Sample Data

A sample CSV file (`sample_equipment_data.csv`) is included in the root directory for testing. It contains 15 chemical equipment entries with the following columns:

- **Equipment Name** – Unique identifier (e.g., Reactor-A1)
- **Type** – Equipment type (Reactor, Pump, Tank, Separator)
- **Flowrate** – Flow rate in m³/h
- **Pressure** – Pressure in bar
- **Temperature** – Temperature in °C

---

## 🌐 Deployment

The web version is deployed on **AWS EC2** (Mumbai region):

- **Live URL**: [http://13.201.134.135](http://13.201.134.135)
- **Backend API**: `http://13.201.134.135:8000/api/`
- **Stack**: Ubuntu 24.04 + nginx + Django + React build

---

## 📹 Demo Video

A short demo video (2–3 minutes) showcasing:
1. CSV upload on both Web and Desktop
2. Data visualization (charts + tables)
3. PDF report download
4. Upload history management

---

## 👤 Author

Built as part of the Intern Screening Task – Hybrid Web + Desktop Application.
