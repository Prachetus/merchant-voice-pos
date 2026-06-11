# merchant-voice-pos
# 🎙️ VoicePOS: The Hands-Free Merchant Inventory System

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-Backend-black.svg)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/MySQL-Database-orange.svg)](https://www.mysql.com/)

## 📌 Problem Statement
Local merchants and shop owners constantly juggle serving customers, handling cash, and managing inventory. Manually typing out inventory deductions on a screen or ledger during peak hours is slow and error-prone. Shop owners need a frictionless way to log sales without breaking eye contact with their customers.

## 💡 The Solution
**VoicePOS** is an interactive, voice-driven Point of Sale (POS) backend prototype. It allows merchants to simply speak their orders (e.g., *"Two packets of milk"*). The system uses the browser's native Web Speech API to capture the audio, parses the natural language in Python to extract item quantities, instantly updates a live MySQL inventory database, and triggers automated low-stock alerts via WhatsApp.

---

## ✨ Key Features
* **🎙️ Live Voice-to-Text:** Captures Indian English accents natively in the browser without requiring third-party cloud API keys.
* **🧠 NLP Data Extraction:** Python backend intelligently strips raw conversational text into structured `Quantity` and `Item` variables (e.g., handles string numbers like "three" and digits like "3").
* **⚡ Live Database Updates:** Connects seamlessly to a local MySQL instance to deduct stock in real-time.
* **🚨 Automated Stock Thresholds:** Constantly monitors inventory levels against predefined safety thresholds.
* **📱 WhatsApp Click-to-Chat Alerts:** Automatically generates a pre-filled WhatsApp link for instant reordering when stock dips into the danger zone.

---

## 🛠️ Tech Stack
* **Frontend:** HTML5, Vanilla JavaScript, Web Speech API (`SpeechRecognition`)
* **Backend:** Python, Flask (`app.py`), Regular Expressions (`re`)
* **Database:** MySQL (`mysql-connector-python`)

---

## 🚀 How to Run Locally (For Judges)

### 1. Prerequisites
Ensure you have the following installed on your machine:
* Python 3.8+
* A local MySQL Server (e.g., XAMPP, WAMP, or MySQL Community Server)

### 2. Environment Setup
Clone the repository and set up a virtual environment:
```powershell
git clone <your-github-repo-link-here>
cd merchant-voice-pos
python -m venv venv
venv\Scripts\activate  # On Windows
