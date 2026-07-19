# 🏛️ ArtifactVault

> **Digital Museum Catalog & Heritage Item Manager for Maharashtra Heritage Museum**

ArtifactVault is a web-based museum management platform developed to digitally preserve, organize, and manage historical artifacts from Maharashtra's rich cultural heritage. The application enables museums to maintain artifact records, manage curator operations, track artifact loans, and provide visitors with an interactive digital catalog.

---

## Overview

Traditional museum record management is often manual, making artifact organization and retrieval time-consuming. ArtifactVault addresses this challenge by providing a centralized digital platform for catalog management, loan tracking, and public access to historical collections.

This project has been developed as an academic project using modern web technologies and Python-based backend architecture.

---

## Key Features

- Digital Artifact Catalog
- Artifact Search & Advanced Filtering
- Curator Dashboard
- Loan Tracking System
- Bulk CSV Import
- RESTful API
- MongoDB Database Integration
- Authentication & Authorization
- Responsive User Interface
- Heritage-focused Design

---

## Museum Theme

**Maharashtra Heritage Museum**

The platform showcases collections inspired by Maharashtra's historical legacy, including:

- Maratha Empire Artifacts
- Historic Fort Collections
- Ancient Coins
- Temple Sculptures
- Historical Manuscripts
- Traditional Maharashtrian Costumes
- Cultural Heritage Collections

---

## Technology Stack

### Frontend
- HTML5
- CSS3
- JavaScript

### Backend
- Python
- Django
- Django REST Framework

### Database
- MongoDB

### Python Concepts
- Object-Oriented Programming (OOP)
- Dictionaries
- List Comprehensions
- Tuples
- CSV Processing
- Regular Expressions (Regex)
- Threading
- Exception Handling
- Datetime Module

---

## 📂 Project Structure

```
ArtifactVault/
│
├── apps/
│   ├── artifacts/
│   ├── common/
│   ├── curators/
│   ├── frontend/
│   └── loans/
│
├── config/
├── data/
├── static/
├── templates/
├── requirements.txt
├── manage.py
└── README.md
```

---

##  Getting Started

### Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/ArtifactVault.git
```

### Navigate to Project

```bash
cd ArtifactVault
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file and configure the MongoDB connection.

```env
MONGODB_URI=your_mongodb_connection_string
DATABASE_NAME=artifactvault
SECRET_KEY=your_secret_key
DEBUG=True
```

### Start Development Server

```bash
python manage.py runserver
```

Application will be available at:

```
http://127.0.0.1:8000/
```

---

## Application Preview

Screenshots of the application will be added here.

- Home Page
- Public Catalog
- Artifact Details
- Curator Dashboard
- Loan Tracking

---

## Future Enhancements

- AI-based Artifact Recognition
- QR Code Integration
- Virtual Museum Tour
- Exhibition Management
- Visitor Analytics
- Multi-language Support

---

## Developer

**Nikhil Patil**

Master of Computer Applications (MCA)

---
## 📄 License

This project has been developed for academic and educational purposes.
