# CyberAware Web Application

A Flask + HTML/CSS/JavaScript conversion of the supplied CyberAware Python project.

## Included
- Learning modules: phishing, password security, social engineering, malware and safe browsing
- Phishing keyword awareness checker
- Fictional password strength checker
- Cybersecurity quiz and saved awareness assessment
- Social engineering reference cards and security tips
- Student learning progress tracker
- Student and assessment record search
- Dashboard statistics
- Downloadable student PDF report

The original Tkinter desktop window has been replaced by a responsive browser dashboard.

## Run on Windows
1. Install Python 3.10 or newer.
2. Open Command Prompt in this folder.
3. Create and activate a virtual environment:

   ```bat
   py -m venv venv
   venv\Scripts\activate
   ```

4. Install dependencies:

   ```bat
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. Start the application:

   ```bat
   python app.py
   ```

6. Open http://127.0.0.1:5000 in your browser.

## Data storage
The application creates `cyberaware_progress.json` and `cyberaware_assessments.json` in this project folder when records are saved. Back these files up regularly.

## Public deployment
This is a development-ready starter. Before public deployment:
- Set Flask debug mode off and use a production WSGI server (for example Waitress on Windows or Gunicorn on Linux).
- Add authentication and role-based access before exposing student records.
- Use a persistent database such as PostgreSQL or SQLite with backups.
- Add HTTPS, rate limiting, input validation and a privacy notice.
- Do not treat the keyword checker or password score as a security scanner or definitive verdict.
- Do not collect real passwords. The password tool is intended for fictional test strings only.

## Notes on conversion
The assessment percentage is calculated from the submitted score before saving. The duplicate progress-saving block in the supplied script has been consolidated. The Tkinter GUI is represented by the browser dashboard.
