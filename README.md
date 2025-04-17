# 📎 ShareBin

ShareBin is an intentionally vulnerable web application built for cybersecurity training and analysis. It allows users to create and share notes and files, explore security flaws, and learn how to identify and mitigate common vulnerabilities.

> ⚠️ This project is for **educational purposes only**. Do not deploy it to a public server without fixing the vulnerabilities listed below.

---

## 📖 About This Project

This repository was created as part of an academic assignment for the _Security Essentials_ course. The goal of **ShareBin** is to serve as a realistic, hands-on platform to explore common web application security vulnerabilities. It forms the basis of a comprehensive security analysis report I had to write for this course. ShareBin is heavily inspired by the OWASP Juice Shop.

By deliberately introducing flaws into the application, ShareBin acts as a sandbox for practicing threat modeling, vulnerability discovery, offensive and defensive cybersecurity.

> **⚠️ Work in Progress:**  
> ShareBin is currently under active development. While some functionality is complete (user auth, note creation, friend system, file uploads), other parts are still being built or refined. Expect changes and refactors in future commits.

---

## 🔮 Planned Features & Roadmap

The following features are planned but not yet implemented. Some are intended to **improve functionality**, others to **introduce more vulnerabilities** for educational purposes.

- [ ] Password reset functionality (with spoofable email flow)
- [ ] Public profile pages and user search filters
- [ ] Basic admin dashboard functions (with insecure role management)
- [ ] Tagging and search by note tags
- [ ] Rate-limiting middleware (and ways to bypass it)
- [ ] File type-based restrictions (and how to bypass them)
- [ ] Secure vs insecure modes

If you'd like to contribute a new feature or vulnerability for inclusion in the educational version of ShareBin, please open a discussion or PR!

## 🧰 Features

- 📝 Create, view, edit, and delete notes
- 🔐 Visibility controls: Public, Private, and Friends-Only
- 📎 File uploads and downloads per note
- 🧑‍🤝‍🧑 Friend system: send/accept/decline friend requests
- 🔍 Public note search
- 🚪 Simple authentication system

---

## 🚨 Known Vulnerabilities (Intentionally Included)

| Vulnerability ID | Description |
|------------------|-------------|
| `vuln01`         | No two-factor authentication |
| `vuln02`         | Weak password policy |
| `vuln03`         | No audit trail or logging |
| `vuln04`         | Note visibility misconfiguration |
| `vuln05`         | Insecure session token storage |
| `vuln06`         | No server-side validation of input |
| `vuln07`         | No access control enforcement on private notes |
| `vuln08`         | No IP/user rate limiting |
| `vuln09`         | Missing role-based access checks |
| `vuln10`         | Session token not validated on each request |
| `vuln11`         | SQL injection due to raw queries |
| `vuln12`         | Sensitive data not encrypted |
| `vuln13`         | Missing per-user access checks |
| `vuln14`         | Poor query optimization (DoS risk) |
| `vuln15`         | File authenticity not verified |
| `vuln16`         | No logging for file access |
| `vuln17`         | Insecure file paths |
| `vuln18`         | No file size limit / risk of storage exhaustion |
| `vuln19`         | Files accessible to anyone with the link |
| `vuln20`         | No virus scanning on uploaded files |

---

## 🏗️ Technology Stack

- **Frontend**: HTML, JavaScript, TailwindCSS, Fontawesome
- **Backend**: Python (Flask)
- **Database**: SQLite
- **Authentication**: Cookie-based session handling
- **Containerization**: Docker (optional)
- **CI/CD**: GitHub Actions (optional)

---

## 🧪 Installation

### 📦 Requirements

- Python 3.10+
- `virtualenv` or `venv`
- Flask
- SQLite3

### ⚙️ Local Setup

```bash
# Clone the repository
git clone https://github.com/LouisI299/ShareBin-Cybersecurity.git
cd sharebin-cybersecurity

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

### ⚙️ Docker Setup (Optional)

```bash
docker build -t sharebin .
docker run -p 5000:5000 sharebin
```

 
