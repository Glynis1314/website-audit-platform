# SiteVerify

**A comprehensive website audit platform** built to perform automated diagnostics on any domain. The solution parses SSL certificates, validates security headers, benchmarks page load performance, scans for accessibility/SEO issues, audits internal/external links, profiles forms, and generates professional PDF reports.

---

## Architecture & Workflow

1. **Streamlit User Interface**: A modern multi-page web application using Streamlit.
2. **Scanner Engine**: A synchronous Selenium-driven headless browser that loads target websites, waits for dynamic content, captures viewport screenshots, and extracts W3C performance timing parameters.
3. **Diagnostic Analyzers**:
   - **Security Analyzer**: Inspects HTTPS status, audits SSL certificate validity/expiration, checks for HTTP security response headers, and scans for insecure input forms.
   - **Accessibility Analyzer**: Evaluates page title presence, image alternative tags, button content, heading hierarchy, and input control labels (including support for `aria-label` and `aria-labelledby`).
   - **Performance Analyzer**: Analyzes page asset counts (scripts, style sheets, images), page size, and processes W3C navigation/resource timings (DNS lookup, TCP handshake, TTFB, and page load latency).
   - **SEO Analyzer**: Reviews title length, meta description, viewport responsiveness configurations, canonical tags, open graph metadata, and heading structures.
   - **Form Intelligence**: Profiles interactive forms, input elements, buttons, and flags potential security gaps (e.g. autocomplete on password fields).
   - **Link Auditor**: Deterministically audits anchor links for broken or connection-failed URLs using a concurrent thread pool worker model.
4. **SQLite Scan Database**: Persists scan history logs, overall scores, metadata, screenshot paths, and complete JSON reports.
5. **PDF Report Compiler**: Compiles scan results into professional, executive-ready PDF reports available for direct download.

---

## Getting Started

### Prerequisites

- Python 3.10+
- Google Chrome browser (for Selenium headless execution)

### Installation & Run

```bash
# Clone the repository
git clone https://github.com/yourusername/SiteVerify.git
cd SiteVerify

# Install dependencies
pip install -r requirements.txt

# Run the Streamlit Application
streamlit run app.py
```

---

## License

MIT © 2026 — Built with love for web audit and security automation.