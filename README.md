# SiteVerify

SiteVerify is a single-page website auditing workstation that performs local diagnostics on target URLs for web developers, designers, and site administrators.

![Tests](https://github.com/Glynis1314/website-audit-platform/actions/workflows/tests.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Live Demo

[Live Demo](https://siteverify.onrender.com/) (may take ~30s to wake up on first load — free tier)

## What it does

SiteVerify performs automated, local checks on any target domain:

* **SSL certificate analysis**: Validates certificate trust, issuer data, and remaining validity days.
* **HTTP response headers**: Audits presence and strength of security headers (CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy).
* **Form security**: Profiles interactive fields, flags insecure action endpoints (HTTP actions on HTTPS pages), and highlights autocomplete settings on password inputs.
* **Accessibility heuristics**: Scans for image alternative attributes, input control labels, button structures, and heading level hierarchy.
* **Performance metrics**: Captures raw page size, asset counts (scripts, stylesheets, images), and processes W3C navigation timings (DNS lookup, TCP handshake, TTFB, DOM processing, and load latency).
* **SEO compliance**: Checks metadata titles, description length, responsive viewport settings, canonical tags, and Open Graph attributes.
* **Concurrent link validation**: Extracts anchor links, targets a deterministic subset of 30 unique URLs, and checks their status codes via a concurrent worker thread pool.
* **PDF reports**: Compiles all category results and telemetry metrics into an executive-ready PDF report for download.
* **Audit history**: Persists previous scans in a local database with a comparative trend chart.

---

## Screenshot placeholders

<!-- add screenshot here -->
![Main Dashboard](https://raw.githubusercontent.com/<user>/<repo>/main/screenshots/dashboard_placeholder.png)
*Figure 1: Main diagnostic workstation dashboard showing score gauges and security metrics.*

<!-- add screenshot here -->
![Category Tab Detail](https://raw.githubusercontent.com/<user>/<repo>/main/screenshots/tab_placeholder.png)
*Figure 2: Response headers audit and W3C timing readouts inside the metrics panels.*

<!-- add screenshot here -->
![History Log Trend](https://raw.githubusercontent.com/<user>/<repo>/main/screenshots/history_placeholder.png)
*Figure 3: Historical scan comparisons displaying successive score progressions.*

---

## Architecture

SiteVerify coordinates page crawling and diagnostic scanning synchronously to generate audits:

* **Telemetry ingestion**: The user inputs a target URL into the Streamlit interface.
* **Browser emulation**: A headless Selenium instance loads the target page, allows dynamic scripts to settle, captures a viewport screenshot, and gathers browser timings.
* **Diagnostic processing**: The DOM payload is passed to five diagnostic analyzers (security, accessibility, performance, SEO, forms) for rule checks.
* **Link auditing**: Anchor links are resolved, sorted, sliced to a 30-item sample, and audited concurrently using a ThreadPoolExecutor.
* **Data persistence**: Results are stored in a local SQLite database, updating global stats and url histories.
* **Reporting**: Telemetry is structured in Streamlit tabs and compiled into a downloadable PDF via ReportLab.

---

## Tech stack

* **Scanning**: Selenium, webdriver-manager
* **Parsing**: BeautifulSoup4, lxml
* **UI**: Streamlit, Plotly
* **Storage**: SQLite
* **PDF**: ReportLab
* **Testing**: unittest

---

## Security considerations

* **Input sanitization**: HTML-escapes all scraped third-party page elements (titles, links, finding details) before rendering them inside the Streamlit user interface to prevent cross-site scripting (XSS) vectors.
* **Database queries**: Uses parameterized SQL queries exclusively throughout database adapters to eliminate SQL injection vulnerabilities.
* **SSRF mitigation**: Validates all client-submitted target URLs before requesting them:
  * Restricts schemes strictly to http and https.
  * Blocks non-standard port connections (accepting only port 80 for HTTP and port 443 for HTTPS).
  * Resolves domains to all associated IPv4 and IPv6 addresses, blocking loopbacks, link-locals, private subnets, and cloud metadata endpoints.
  * Follows HTTP redirects manually up to 5 hops, re-validating the safety of every intermediate target before connection.
  * *Note on DNS-rebinding*: Check-time IP validation does not pin the subsequent requests/Selenium connection resolution (TOCTOU rebinding risk), which remains a known limitation.

---

## Getting Started

### Local Setup

Ensure you have Google Chrome installed on your host system.

1. Clone the repository:
   ```bash
   git clone https://github.com/<user>/<repo>.git
   cd SiteVerify
   ```
2. Install python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Launch the application:
   ```bash
   streamlit run app.py
   ```

### Docker Setup

Alternatively, run the tool inside a sandboxed Docker container containing Chrome dependencies:

```bash
# Build the container
docker build -t siteverify .

# Run the container (binds port 8501)
docker run -p 8501:8501 siteverify
```

Or start the application stack using docker-compose:
```bash
docker-compose up --build
```

---

## Running tests

Run the unit test suite locally to verify diagnostic parser checks:

```bash
python -m unittest test_suite.py
```

---

## Lessons learned

I originally designed the project with an over-engineered asynchronous task queue using Celery and Playwright that added unnecessary complexity without functioning correctly, which I eventually stripped down to a reliable synchronous Selenium architecture. Along the way, I resolved a race condition where parallel audits were overwriting a single screenshot file by implementing UUID-based unique paths. I also discovered and mitigated XSS risks from rendering raw scraped web content, and closed an SSRF gap where users could use the scanning server to probe local network endpoints. Admitting these vulnerabilities and cleaning up the async residue was a critical step in building a secure, stable auditing workstation.

---

## License

MIT © 2026 — Built with love for web audit and security automation.