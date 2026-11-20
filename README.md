# UdyamFlow ⚡

> **One-Sitting Digital Onboarding & Intelligent Verification Platform for MSMEs**  
> *Developed for Airtel SYNC Hackathon 2026 by Team TheSaints (Punjab Engineering College, Chandigarh).*

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📌 Problem Overview

Traditional B2B telecom and enterprise service onboarding for Micro, Small, and Medium Enterprises (MSMEs) in India suffers from high drop-off rates (~60% across the funnel) and an average turnaround time of **17+ days** with multiple follow-up calls. 

Major pain points include:
- Manual, fragmented KYC document validation and high document rejection rates (outdated utility bills, mismatched signatory names).
- Rigid, one-size-fits-all product catalogues that confuse small business owners.
- Lack of vernacular support for Tier-2 / Tier-3 business owners.
- Lost revenue from dropped leads due to absent back-office triage.

**UdyamFlow** solves this by compressing the entire discovery, eligibility, verification, and dispatch journey into a **single sitting (< 10 minutes)**.

---

## 🚀 Key Features

### 1. 🔍 Instant Government Registry Lookups
- **GSTIN & Udyam Integration:** Real-time lookup with checksum validation and automated prefill of business legal name, constitution, and principal address.
- **Fuzzy Search & Typeahead:** Gracefully suggests matches when users make minor typos in registration queries.

### 2. 🛡️ Smart KYC & DPDP Compliance Engine
- **Document Freshness Audit:** Automatically flags address proof and utility bills older than 90 days.
- **Signatory Cross-Check:** Reconciles applicant identity against Sole Proprietorship / Partnership registration records.
- **Privacy by Design (DPDP Act 2023):** Built-in explicit consent logging, masked Aadhaar storage (`XXXX-XXXX-8924`), and auditable SHA-256 verification hashes.

### 3. 🤖 AI Telecom Bundle Advisor
- Context-aware recommendation engine tailored to business verticals:
  - *Clinics & Professional Offices:* High-uptime fiber, static IP, cloud backups & endpoint cybersecurity.
  - *Multi-Site & Retail Chains:* 4G/5G failover for POS continuity & centralized CCTV surveillance.
  - *Kirana & Micro-Retail:* Quick AirFiber setup, POS connectivity & WhatsApp store catalogue.
  - *Manufacturing / Industrial:* Dedicated 1:1 leased lines, perimeter firewall & IoT telemetry.

### 4. 📦 Interactive Order Lifecycle Tracker
- Real-time milestone tracker simulating end-to-end dispatch and provisioning:
  `Order Placed` ➔ `KYC Verified` ➔ `Technician Dispatched` ➔ `Feasibility Audit` ➔ `Service Active`.

### 5. 🌐 Vernacular & Accessible UI
- Instant language toggle supporting **English**, **Hindi (हिन्दी)**, **Tamil (தமிழ்)**, and **Telugu (తెలుగు)**.

### 6. 📊 Drop-off Lead Triage & Recovery
- Back-office analytics dashboard that scores dropped leads using a propensity model based on business size, turnover, and abandonment stage to trigger automated WhatsApp nudges or warm-assist field visits.

---

## 🏗️ Architecture & Tech Stack

```
udyam-flow/
├── app.py                 # Core Flask application & REST API endpoints
├── data/                  # Mock registries, product catalogue & synthetic leads
│   ├── mock_gstin_registry.csv
│   ├── mock_udyam_registry.csv
│   ├── product_catalogue.csv
│   ├── smb_leads.csv
│   └── kyc_documents/
├── static/
│   ├── css/style.css      # Custom responsive styling
│   └── js/app.js          # Dynamic UI state, validation & language switching
├── templates/
│   └── index.html         # Single-page onboarding portal
├── docs/                  # Hackathon case study brief & presentation slides
│   ├── Airtel_SYNC_Case.pdf
│   └── presentation.pdf
├── requirements.txt
├── run.bat
└── README.md
```

- **Backend:** Python, Flask (RESTful micro-endpoints)
- **Frontend:** Vanilla JavaScript (ES6+), Modern Semantic HTML5 & CSS3
- **Data Engine:** In-memory indexed CSV registries for low-latency lookups

---

## 🛠️ Quickstart

### Prerequisites
- Python 3.9+
- pip

### 1. Clone the repository
```bash
git clone https://github.com/pratstick/udyam-flow.git
cd udyam-flow
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the application
On Windows:
```bash
run.bat
```
Or with Python directly:
```bash
python app.py
```

Open your browser at **[http://localhost:5000](http://localhost:5000)** to experience the onboarding flow.

---

## 📄 Case Study & Hackathon Context

This project was built for the **Airtel SYNC Hackathon 2026** under **Track A: Project Udyam Digital**.  
Pitch deck and presentation slides are preserved under the [`docs/`](docs/) directory.

*Team TheSaints — Punjab Engineering College (PEC), Chandigarh.*
