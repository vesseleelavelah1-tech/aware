from flask import Flask, render_template, request, jsonify, send_file
from pathlib import Path
from datetime import datetime
import json, io, re

app = Flask(__name__)
BASE = Path(__file__).resolve().parent
PROGRESS_FILE = BASE / "cyberaware_progress.json"
ASSESS_FILE = BASE / "cyberaware_assessments.json"

LEARNING_MODULES = [
    "Introduction to Cybersecurity", "Phishing Awareness", "Password Security",
    "Social Engineering", "Safe Browsing", "Cybersecurity Quiz", "Security Tips",
    "Online Privacy", "Cybercrime Awareness"
]

QUIZ = [
 {"question":"What is phishing?","options":["A. A computer game","B. A fake attempt to steal information","C. A programming language","D. A computer keyboard"],"answer":"B","explanation":"Phishing uses deceptive messages to steal information."},
 {"question":"Which password is strongest?","options":["A. 123456","B. password","C. Alex123","D. T9#mQ2!vLp7@"],"answer":"D","explanation":"A long, unique password is harder to guess."},
 {"question":"What does MFA mean?","options":["A. Multi-Factor Authentication","B. Multiple File Access","C. Main Firewall Application","D. Manual File Arrangement"],"answer":"A","explanation":"MFA adds another verification step to an account login."},
 {"question":"What should you do with a suspicious link?","options":["A. Click immediately","B. Share it","C. Avoid clicking it","D. Enter your password"],"answer":"C","explanation":"Suspicious links may lead to fraudulent or harmful websites."},
 {"question":"What is malware?","options":["A. Helpful software","B. Harmful software","C. A web browser","D. A search engine"],"answer":"B","explanation":"Malware is software designed to cause harm or perform unwanted actions."}
]
ASSESSMENT = [
 {"question":"What is phishing?","options":["A. A computer game","B. An attempt to steal information using deceptive messages","C. A programming language","D. A computer component"],"answer":"B","explanation":"Phishing uses deceptive messages to steal information."},
 {"question":"What should you do with a suspicious email link?","options":["A. Click immediately","B. Forward it to everyone","C. Avoid clicking and verify the sender","D. Enter your password"],"answer":"C","explanation":"Always verify suspicious links before interacting with them."},
 {"question":"What does MFA mean?","options":["A. Multi-Factor Authentication","B. Main File Access","C. Multiple Folder Application","D. Manual File Analysis"],"answer":"A","explanation":"MFA uses multiple verification factors to protect accounts."},
 {"question":"What is smishing?","options":["A. A computer virus","B. Phishing through SMS messages","C. A secure password","D. A firewall"],"answer":"B","explanation":"Smishing is phishing conducted through text messages."},
 {"question":"Should you share your OTP with someone who calls you?","options":["A. Yes","B. Only with strangers","C. Only through SMS","D. No"],"answer":"D","explanation":"Never disclose your OTP to another person."}
]
ATTACKS = [
 {"name":"Phishing","description":"Fraudulent emails or messages designed to steal information.","protection":"Check the sender and avoid suspicious links."},
 {"name":"Smishing","description":"Phishing attacks carried out through SMS messages.","protection":"Do not trust unexpected SMS links."},
 {"name":"Vishing","description":"Scams carried out through phone or voice calls.","protection":"Never share passwords or OTPs over calls."},
 {"name":"Pretexting","description":"An attacker invents a story to gain your trust.","protection":"Verify someone's identity before sharing information."},
 {"name":"Baiting","description":"An attacker offers something tempting to trick a victim.","protection":"Avoid unknown USB drives and suspicious downloads."},
 {"name":"Impersonation","description":"Someone pretends to be a trusted person or organisation.","protection":"Confirm requests through an official contact method."},
 {"name":"Tailgating","description":"An unauthorised person follows someone into a restricted area.","protection":"Never allow unknown people to bypass access controls."}
]
TIPS = [
 "Use strong and unique passwords for every account.",
 "Enable two-factor authentication wherever possible.",
 "Never share your OTP or password with anyone.",
 "Avoid clicking suspicious email and SMS links.",
 "Keep your operating system and applications updated.",
 "Avoid downloading files from unknown websites.",
 "Verify unexpected requests for money or personal information.",
 "Use secure Wi-Fi and avoid sensitive activities on public networks.",
 "Back up important files regularly.",
 "Report suspicious messages to the appropriate authority."
]
SUSPICIOUS = ["urgent","verify your account","click here","password","claim your prize","account suspended","send money","free gift","limited time"]

def load_records(path):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []

def save_records(path, records):
    path.write_text(json.dumps(records, indent=4), encoding="utf-8")

def stats():
    progress = load_records(PROGRESS_FILE)
    assessments = load_records(ASSESS_FILE)
    latest = {}
    for rec in progress:
        sid = str(rec.get("student_id","")).strip()
        if sid: latest[sid] = rec
    scores = []
    assessment_students = set()
    for rec in assessments:
        sid = str(rec.get("student_id","")).strip()
        if sid: assessment_students.add(sid)
        try:
            value = float(rec.get("percentage",0))
            if 0 <= value <= 100: scores.append(value)
        except (ValueError, TypeError): pass
    pcts = []
    for rec in latest.values():
        try:
            value = float(rec.get("progress_percentage",0))
            if 0 <= value <= 100: pcts.append(value)
        except (ValueError, TypeError): pass
    return {
      "total_students": len(set(latest) | assessment_students),
      "students_with_progress": len(latest),
      "students_with_assessments": len(assessment_students),
      "assessment_attempts": len(scores),
      "average_assessment": round(sum(scores)/len(scores),2) if scores else 0,
      "average_progress": round(sum(pcts)/len(pcts),2) if pcts else 0
    }

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/api/content")
def content():
    return jsonify({"quiz":QUIZ,"assessment":ASSESSMENT,"modules":LEARNING_MODULES,
                    "attacks":ATTACKS,"tips":TIPS})

@app.get("/api/dashboard")
def dashboard():
    return jsonify(stats())

@app.post("/api/phishing")
def phishing():
    message = request.json.get("message","").lower()
    found = [word for word in SUSPICIOUS if word in message]
    return jsonify({"found":found, "suspicious":bool(found),
      "message":"Suspicious language detected. Treat this message cautiously." if found else "No suspicious keywords were detected. This does NOT guarantee safety.",
      "recommendations":["Do not click suspicious links.","Never share your password.","Verify the sender independently.","Report suspicious messages."] if found else ["Check the sender's address.","Inspect links carefully.","Avoid unexpected attachments."]})

@app.post("/api/password")
def password():
    value = request.json.get("password","")
    score = 0
    score += 2 if len(value)>=12 else (1 if len(value)>=8 else 0)
    score += int(any(c.isupper() for c in value))
    score += int(any(c.islower() for c in value))
    score += int(any(c.isdigit() for c in value))
    score += int(any(not c.isalnum() for c in value))
    level = "WEAK" if score<=2 else ("MODERATE" if score<=4 else "STRONG")
    advice = "Use a longer and more varied password." if score<=2 else ("Add more character variety and length." if score<=4 else "Keep it unique and never reuse it.")
    return jsonify({"score":score,"strength":level,"advice":advice})

@app.post("/api/quiz")
def quiz():
    data = request.json
    questions = QUIZ if data.get("kind")=="quiz" else ASSESSMENT
    answers = data.get("answers",[])
    details, score = [], 0
    for i,q in enumerate(questions):
        answer = str(answers[i]).upper() if i < len(answers) else ""
        correct = answer == q["answer"]
        score += int(correct)
        details.append({"question":q["question"],"selected":answer,"answer":q["answer"],"correct":correct,"explanation":q["explanation"]})
    total = len(questions)
    percentage = round(score/total*100,2)
    result = {"score":score,"total":total,"percentage":percentage,"details":details}
    if data.get("kind")=="assessment":
        sid = str(data.get("student_id","")).strip()
        if not sid: return jsonify({"error":"Please enter an anonymous student ID."}),400
        records=load_records(ASSESS_FILE)
        records.append({"student_id":sid,"score":score,"total_questions":total,"percentage":percentage,"created_at":datetime.now().isoformat(timespec="seconds")})
        save_records(ASSESS_FILE,records)
        result["saved"]=True
    return jsonify(result)

@app.post("/api/progress")
def progress():
    data=request.json
    sid=str(data.get("student_id","")).strip()
    if not sid: return jsonify({"error":"Student ID cannot be empty."}),400
    completed=[m for m in LEARNING_MODULES if m in data.get("completed",[])]
    pct=round(len(completed)/len(LEARNING_MODULES)*100,2)
    record={"student_id":sid,"completed_modules":completed,"total_modules":len(LEARNING_MODULES),
            "completed_count":len(completed),"progress_percentage":pct,"created_at":datetime.now().isoformat(timespec="seconds")}
    records=load_records(PROGRESS_FILE); records.append(record); save_records(PROGRESS_FILE,records)
    return jsonify(record)

@app.get("/api/records")
def records():
    progress=load_records(PROGRESS_FILE); assessments=load_records(ASSESS_FILE)
    sid=request.args.get("student_id","").strip().lower()
    if sid:
        progress=[r for r in progress if str(r.get("student_id","")).lower()==sid]
        assessments=[r for r in assessments if str(r.get("student_id","")).lower()==sid]
    return jsonify({"progress":progress,"assessments":assessments})

@app.get("/api/report/<student_id>")
def pdf_report(student_id):
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import inch
    except ImportError:
        return jsonify({"error":"PDF support is not installed. Run: pip install reportlab"}),500
    progress=[r for r in load_records(PROGRESS_FILE) if str(r.get("student_id","")).lower()==student_id.lower()]
    assessments=[r for r in load_records(ASSESS_FILE) if str(r.get("student_id","")).lower()==student_id.lower()]
    if not progress and not assessments: return jsonify({"error":"No records found for this student."}),404
    latest=progress[-1] if progress else {}
    safe=re.sub(r"[^A-Za-z0-9_-]","_",student_id)
    buffer=io.BytesIO()
    doc=SimpleDocTemplate(buffer,pagesize=A4)
    styles=getSampleStyleSheet(); story=[
      Paragraph("CYBERAWARE STUDENT PERFORMANCE REPORT",styles["Title"]),Spacer(1,.2*inch),
      Paragraph("Anonymous Student ID: "+student_id,styles["Normal"]),Spacer(1,.25*inch),
      Paragraph("LEARNING PROGRESS",styles["Heading2"])
    ]
    pdata=[["Description","Result"],["Completed modules",str(latest.get("completed_count",0))],
           ["Total modules",str(latest.get("total_modules",0))],["Learning progress",str(latest.get("progress_percentage",0))+"%"]]
    table=Table(pdata,colWidths=[3*inch,2*inch]); table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.lightblue),("GRID",(0,0),(-1,-1),1,colors.grey),("PADDING",(0,0),(-1,-1),8)]))
    story += [table,Spacer(1,.25*inch),Paragraph("ASSESSMENT PERFORMANCE",styles["Heading2"])]
    adata=[["Attempt","Score","Percentage"]]
    for i,r in enumerate(assessments,1): adata.append([str(i),f'{r.get("score",0)}/{r.get("total_questions",0)}',str(r.get("percentage",0))+"%"])
    if len(adata)==1: adata.append(["-","No assessment records","-"])
    table=Table(adata,colWidths=[1.3*inch,1.7*inch,2*inch]); table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.lightgreen),("GRID",(0,0),(-1,-1),1,colors.grey),("PADDING",(0,0),(-1,-1),8)]))
    story += [table,Spacer(1,.3*inch),Paragraph("Generated by CyberAware Educational Application.",styles["Italic"])]
    doc.build(story); buffer.seek(0)
    return send_file(buffer,as_attachment=True,download_name=f"CyberAware_{safe}_Report.pdf",mimetype="application/pdf")

if __name__=="__main__":
    app.run(debug=True)
