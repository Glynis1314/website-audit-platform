# 🌐 website-audit-platform

An intelligent website auditing platform that automates website inspection using Selenium and Streamlit. SiteVerify analyzes website structure, forms, security, accessibility, and performance to generate comprehensive audit reports with downloadable PDFs.

---

## 🚀 Features

- 🌍 Website Scanning using Selenium
- 📝 Form Intelligence Analysis
- 🔒 Security Assessment
- ♿ Accessibility Evaluation
- ⚡ Performance Analysis
- 📊 Overall Website Health Score
- 📄 Professional PDF Report Generation
- 📸 Automatic Website Screenshot Capture
- 💡 Intelligent Recommendations

---

## 🛠️ Tech Stack

- Python
- Streamlit
- Selenium
- BeautifulSoup
- ReportLab
- Pillow
- WebDriver Manager

---

## 📂 Project Structure

```
SiteVerify/
│
├── app.py
├── requirements.txt
├── README.md
│
├── services/
│   ├── scanner.py
│   ├── form_analyzer.py
│   ├── security.py
│   ├── accessibility.py
│   └── performance.py
│
├── utils/
│   ├── report_generator.py
│   └── pdf_generator.py
│
├── screenshots/
└── reports/
```

---

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/Glynis1314/SiteVerify.git
```

Move into the project directory:

```bash
cd SiteVerify
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the environment

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
streamlit run app.py
```

---

## 📊 Analysis Modules

### 📝 Form Intelligence

- Detects forms
- Counts input fields
- Detects email/password/search fields
- Identifies hidden inputs

### 🔒 Security

- HTTPS verification
- Password autocomplete detection
- Security scoring
- Security recommendations

### ♿ Accessibility

- Missing image alt attributes
- Unlabelled form controls
- Empty buttons
- Accessibility score

### ⚡ Performance

- HTML size analysis
- Images
- JavaScript files
- CSS stylesheets
- Links
- Performance score

---

## 📄 Report Generation

SiteVerify generates a downloadable PDF report containing:

- Website Information
- Overall Website Score
- Form Analysis
- Security Report
- Accessibility Report
- Performance Analysis
- Recommendations

---

## 🎯 Future Enhancements

- Docker Support
- Render Deployment
- Lighthouse Integration
- SEO Analysis
- Broken Link Detection
- Cookie Analysis
- SSL Certificate Inspection
- Responsive Design Testing

---

## 👨‍💻 Author

**Glynis D'Mello**

GitHub: https://github.com/Glynis1314

---

## ⭐ If you like this project

Give it a ⭐ on GitHub!