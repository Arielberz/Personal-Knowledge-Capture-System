# תוכנית בנייה מעודכנת — Knowledge Capture Agent עם GitHub Copilot

## המטרה החדשה
לבנות אתר + סוכן AI מקומי שיודע לקחת מידע שנמצא במחשב — גרפים, צילומי מסך, PDF, טבלאות, שיחות AI ופתקים — לנתח אותו, להסביר אותו, ולשייך אותו למקום הנכון במערכת הידע.

במקום שהמשתמש יעלה כל דבר ידנית, יהיה Agent שעובד על תיקיית Inbox מוגדרת בלבד:

```text
~/KnowledgeInbox/
├── images/
├── pdfs/
├── chat_exports/
├── notes/
└── exports/
```

הסוכן לא מקבל גישה לכל המחשב. הוא מקבל הרשאה רק לתיקייה אחת או כמה תיקיות שנבחרו במפורש.

---

## איך הסוכן אמור לעבוד

```text
קובץ חדש נכנס ל־Inbox
↓
Agent מזהה קובץ חדש
↓
בודק סוג קובץ: image / pdf / chat / note
↓
מחלץ מידע ראשוני
↓
שולח ל־AI Vision / Text Model
↓
מקבל JSON מובנה
↓
מחליט לאיזה נושא לשייך
↓
נותן Knowledge Score
↓
מסביר למה הוא החליט כך
↓
שומר כ־pending_review
↓
המשתמש מאשר / מתקן / מעביר לארכיון
```

העיקרון החשוב: הסוכן מציע ומסביר, אבל לא מוחק ולא משנה מקור בלי אישור.

---

## יכולות Agent ב־MVP

### 1. Watch Folder / Scan Folder
הסוכן יכול לסרוק תיקייה לפי בקשה:

```text
POST /api/agent/scan
```

או בהמשך לעבוד כ־watcher שרץ כל כמה דקות.

בשלב ראשון עדיף Scan ידני מתוך האתר, כדי לשלוט בעלויות ובטעויות.

### 2. File Type Router
הסוכן מזהה סוג קובץ:

```text
.png / .jpg / .jpeg / .webp  → image_processor
.pdf                         → pdf_processor
.md / .txt                   → note_processor
.json / .html / .md chats    → chat_processor
.csv / .xlsx                 → table_processor בהמשך
```

### 3. AI Analyzer
לכל סוג קובץ יש פרומפט אחר:

- גרף פיננסי: חילוץ צירים, מספרים, מגמה, טענה מרכזית, שאלה פתוחה.
- צילום מסך מאתר/טוויטר: חילוץ טענה, מקור, אמינות, נושא.
- שיחת AI: חילוץ ידע חוזר, החלטות, הסברים, קוד, שאלות המשך.
- PDF: חילוץ סיכום, נקודות חשובות, טבלאות ועמודים רלוונטיים.

### 4. Topic Router
הסוכן לא פותח נושא חדש מיד. קודם הוא מנסה להתאים לנושאים קיימים:

```text
AI and Automation
AI Infrastructure
Market Valuation
ETF and Market Structure
Private Markets
Portfolio Analytics
Excel and Data Workflows
Real Estate
Health and Nutrition
Programming and Projects
Archive / Low Value
```

### 5. Explanation Layer
לכל החלטה הסוכן שומר:

```text
suggested_topic
confidence
knowledge_score
reason_for_topic
reason_for_score
what_to_learn_from_this
open_questions
```

---

## מבנה פרויקט מומלץ

```text
knowledge-capture-agent/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── routes/
│   │   │   ├── agent.py
│   │   │   ├── captures.py
│   │   │   ├── topics.py
│   │   │   ├── reminders.py
│   │   │   └── exports.py
│   │   ├── services/
│   │   │   ├── agent_service.py
│   │   │   ├── file_scanner.py
│   │   │   ├── file_router.py
│   │   │   ├── ai_service.py
│   │   │   ├── topic_router.py
│   │   │   ├── explanation_service.py
│   │   │   └── export_service.py
│   │   └── processors/
│   │       ├── image_processor.py
│   │       ├── pdf_processor.py
│   │       ├── chat_processor.py
│   │       └── note_processor.py
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   └── React + Vite RTL dashboard
│
├── data/
│   ├── inbox/
│   │   ├── images/
│   │   ├── pdfs/
│   │   ├── chat_exports/
│   │   └── notes/
│   ├── processed/
│   ├── exports/
│   └── originals_backup/
│
├── prompts/
│   ├── analyze_image.md
│   ├── analyze_financial_chart.md
│   ├── analyze_pdf.md
│   ├── analyze_chat.md
│   ├── route_topic.md
│   └── score_knowledge.md
│
├── database/
│   └── knowledge.db
└── README.md
```

---

## טבלאות Database נוספות לסוכן

### agent_runs
```text
id
started_at
finished_at
status
files_found
files_processed
files_failed
estimated_cost
notes
```

### source_files
```text
id
file_path
original_filename
file_type
file_hash
file_size
created_at
last_seen_at
status
```

### agent_decisions
```text
id
source_file_id
capture_id
suggested_topic
suggested_status
knowledge_score
confidence
reason_for_topic
reason_for_score
created_at
approved_by_user
user_correction
```

### processing_logs
```text
id
run_id
file_path
step
status
message
created_at
```

---

## JSON שהסוכן צריך להחזיר לכל פריט

```json
{
  "source_type": "image",
  "file_type": "financial_chart",
  "title": "Forward P/E compression in technology sector",
  "summary": "The chart shows that valuation multiples can compress even when prices are near highs if expected earnings rise.",
  "suggested_topic": "Market Valuation",
  "suggested_subtopic": "Forward P/E",
  "key_claims": [
    "Forward P/E depends on expected earnings, not only price.",
    "Multiple compression can happen through rising earnings estimates."
  ],
  "numbers": [
    {
      "label": "Forward P/E",
      "value": "unknown",
      "unit": "ratio",
      "context": "Need manual check if exact number is not readable"
    }
  ],
  "open_questions": [
    "Did the multiple fall because price fell or because earnings expectations rose?"
  ],
  "suggested_tags": ["Forward P/E", "Valuation", "Earnings", "Market Structure"],
  "knowledge_score": 8,
  "confidence": "medium",
  "reason_for_topic": "The item discusses valuation multiples and earnings expectations.",
  "reason_for_score": "It is reusable knowledge for understanding market valuation.",
  "recommended_action": "pending_review"
}
```

---

## פרומפט ל־GitHub Copilot — בניית הסוכן

```text
Build a local AI agent service for a personal knowledge capture app.

Tech stack:
- Python
- FastAPI
- SQLite
- SQLAlchemy
- Local file system

Goal:
The agent scans a configured local inbox folder, detects new files, analyzes each file, routes it to the right knowledge topic, explains the decision, and saves it as pending_review.

Important safety rules:
1. The agent may only read from configured inbox folders.
2. The agent must never delete original files.
3. The agent must never rename or move original files without explicit user approval.
4. The agent may create output JSON, Markdown and CSV files.
5. Every processed file must be logged.
6. Use file hashes to avoid processing the same file twice.
7. Process one file at a time.
8. Store all AI decisions in agent_decisions.

Implement:
- file_scanner.py to scan inbox folders
- file_router.py to detect file type
- agent_service.py to orchestrate processing
- mock ai_service.py for now
- topic_router.py to map AI results to existing topics
- FastAPI route POST /api/agent/scan
- FastAPI route GET /api/agent/runs
- FastAPI route GET /api/agent/decisions
```

---

## פרומפט ל־Copilot — ניתוח גרפים

```text
Create a prompt file named analyze_financial_chart.md.
The prompt should instruct an AI vision model to analyze financial charts from screenshots.
It must extract:
- chart title
- asset/company/sector if visible
- x-axis and y-axis meaning
- trend direction
- important numbers
- key claims
- possible interpretation
- what is uncertain
- open questions
- suggested topic
- suggested tags
- knowledge_score 1-10
- confidence

The AI must not invent numbers that are not visible.
If the chart is unclear, it should write requires_check.
```

---

## פרומפט ל־Copilot — Frontend למסך סוכן

```text
Add an Agent page to the React RTL frontend.
The page should show:
1. Agent status: running / paused / scanning
2. Configured inbox folders
3. Last scan summary
4. List of files found
5. Agent decisions with suggested topic, score, confidence and explanation
6. Buttons: Approve, Change Topic, Archive, Requires Check
7. Agent console log
8. Safety permissions panel

Use mock data first and connect to API later.
```

---

## סדר בנייה מומלץ

### שלב 1 — דמו Frontend
לבנות מסך Agent עם Mock Data בלבד.

### שלב 2 — Backend Scan ידני
לבנות endpoint שסורק תיקיית Inbox ומחזיר רשימת קבצים.

### שלב 3 — Hash + DB
לשמור source_files ולמנוע כפילויות.

### שלב 4 — Mock Analysis
הסוכן מחזיר JSON דמה לפי שם הקובץ.

### שלב 5 — Review Queue
כל תוצאה נכנסת ל־pending_review.

### שלב 6 — AI אמיתי
לחבר Vision API רק אחרי שכל הזרימה עובדת.

### שלב 7 — Watcher אוטומטי
להוסיף watcher שרץ כל X דקות או כפתור Scan.

---

## למה לא לתת לסוכן שליטה מלאה בהתחלה

סוכן AI על קבצים אישיים יכול לטעות בסיווג, לשלוח מידע רגיש ל־API, או לייצר בלאגן בתיקיות.
לכן ה־MVP צריך להיות שמרני:

```text
Read only originals
Create outputs only
No delete
No rename
No move
Manual approval before core knowledge
```

---

## הגרסה הנכונה בשבילך

הגרסה הכי מתאימה להתחלה:

```text
Local Agent + Manual Review
```

כלומר:
- הסוכן מזהה ומנתח.
- הסוכן מסביר לאן זה שייך.
- אתה מאשר או מתקן.
- רק אחרי כמה שבועות, אם הוא מדייק, נותנים לו יותר אוטומציה.
