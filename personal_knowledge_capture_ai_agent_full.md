# Personal Knowledge Capture System
## מערכת אישית לרכישת ידע מתמונות, גרפים, שיחות AI ותזכורות חזרה

**גרסה:** אפיון מלא עם שתי אפשרויות עבודה  
**תאריך:** 2026-05-26  
**מטרה:** לבנות מערכת אישית שמצליחה להפוך חשיפה יומיומית לגרפים, צילומי מסך, שיחות AI, רעיונות וקטעי מידע — לידע מסודר, מתויג, מחובר, ניתן לחיפוש, וניתן לחזרה לאורך זמן.

---

# 1. הרעיון המרכזי

המערכת מיועדת להיות “מוח ידע אישי” שמתווך בין מידע גולמי לבין ידע שימושי.

הקלטים:

- תמונות שאני מצלם ביום־יום.
- גרפים פיננסיים.
- טבלאות.
- צילומי מסך מטוויטר / אתרים / דוחות / מצגות.
- קבצי PDF.
- קטעי טקסט.
- היסטוריית שיחות מצ׳אטבוטים כמו ChatGPT, Claude, Gemini וכו׳.
- רעיונות שעלו תוך כדי עבודה.

הפלטים:

- סיכומים לפי נושאים.
- מיון תמונות לפי תחומי ידע.
- שאלות פתוחות.
- תזכורות חזרה.
- מפות ידע.
- קשרים בין נושאים.
- סיכום שבועי / חודשי.
- אינדקס תמונות וידע.
- בסיס נתונים או קבצי Markdown/CSV שמאפשרים חיפוש ועיון לאורך זמן.

המטרה היא לא רק “לשמור דברים”, אלא ליצור תהליך למידה מתמשך.

```text
חשיפה יומית אקראית
↓
צילום / שמירה / ייבוא שיחות
↓
ניתוח AI
↓
סינון רעש
↓
מיון לפי נושאים
↓
סיכום ותובנות
↓
שאלות חזרה
↓
ידע מצטבר
```

---

# 2. שתי אפשרויות עבודה מרכזיות

יש שתי דרכים עיקריות לבנות את המערכת.

## אפשרות א׳ — מוצר מובנה עם Claude Cowork

זו אפשרות שבה משתמשים ב־Claude Cowork כמוצר עבודה מוכן יחסית.

הרעיון:

```text
תיקיית תמונות / קבצים
↓
Claude Cowork Project
↓
הוראות קבועות
↓
Claude ממיין, מסכם, שואל, מסדר
↓
קבצי Markdown / CSV / תיקיות נושאיות
```

זוהי האפשרות המתאימה כאשר רוצים להתחיל מהר, בלי לבנות Backend, API, Database, Worker, UI וכו׳.

Cowork מתאים במיוחד ל־MVP ידני וחכם: נותנים לו תיקיית תמונות, כללים, תוצרי פלט, והוא עוזר לנהל את הידע.

## אפשרות ב׳ — מערכת עצמאית עם Claude Code + Backend + API

זו אפשרות שבה בונים אפליקציה מקומית או פנימית.

הרעיון:

```text
תיקיית Inbox
↓
Python Worker / FastAPI
↓
AI Vision API
↓
JSON מובנה
↓
SQLite / Database
↓
Dashboard בדפדפן
↓
תזכורות, חיפוש, נושאים, דוחות
```

כאן Claude Code משמש לבניית הקוד, אבל המערכת עצמה רצה בצורה עצמאית.

זו האפשרות המתאימה אם רוצים שליטה גבוהה, ריצה חוזרת, Schema קבוע, Audit Log, חיפוש, דאטהבייס, הרשאות ועלויות נשלטות.

---

# 3. השוואה בין שתי האפשרויות

| נושא | אפשרות א׳: Claude Cowork | אפשרות ב׳: Backend + API |
|---|---|---|
| מהירות התחלה | גבוהה מאוד | בינונית / איטית יותר |
| צורך בקוד | נמוך | גבוה יותר |
| שליטה במבנה הנתונים | בינונית | גבוהה מאוד |
| נוחות למשתמש לא טכני | גבוהה | תלוי באפליקציה שתיבנה |
| אוטומציה מלאה | מוגבלת | גבוהה |
| עלויות | עלולות להיות פחות צפויות | יותר ניתנות למדידה לפי קריאות API |
| התאמה לניסוי ראשון | מצוינת | טובה, אבל דורשת בנייה |
| התאמה למוצר סופי יציב | בינונית | גבוהה |
| שקיפות Audit / Logs | חלקית | מלאה אם בונים נכון |
| ניהול קונטקסט | דרך Cowork Project | דרך DB / prompts / vector search |
| סיכון פעולה לא רצויה | צריך להגדיר גבולות | אפשר לבנות הרשאות קשיחות |
| מתאים ל־Finance/Client Data | רק בזהירות ובתיקיית ניסוי | מתאים יותר אם מאובטח נכון |

---

# 4. ההמלצה הכללית

המסלול המומלץ הוא היברידי:

```text
שלב 1 — Cowork כמוצר מובנה לניסוי
↓
שלב 2 — יצירת קבצי Markdown/CSV מסודרים
↓
שלב 3 — Claude Code בונה Dashboard שקורא את הקבצים
↓
שלב 4 — מעבר ל־Backend + API אם צריך אוטומציה מלאה
```

כלומר:

- לא להתחיל ישר ממערכת מורכבת.
- לא לתת לסוכן אוטונומי שליטה מלאה על תיקיות מקוריות.
- להתחיל מ־Cowork כדי להבין את מבנה הידע הרצוי.
- להפוך את תוצרי Cowork ל־Schema.
- לבנות אפליקציה רק אחרי שיש דוגמת עבודה טובה.

---

# 5. אפשרות א׳ בפירוט — Claude Cowork כמוצר מובנה

## 5.1 מה Cowork עושה בפרויקט הזה

Cowork ישמש כעוזר ידע אישי שמקבל משימות כמו:

- עבור על תיקיית תמונות.
- זהה מה יש בכל תמונה.
- חלץ טענות, מספרים, רעיונות ושאלות.
- מיין לפי נושאים קיימים.
- אל תפתח נושא חדש על כל דבר קטן.
- צור סיכום שבועי.
- צור קובץ שאלות פתוחות.
- צור תזכורות חזרה.
- צור אינדקס תמונות.

## 5.2 מבנה תיקיות לעבודה עם Cowork

```text
KnowledgeCapture_Cowork/
│
├── 00_inbox_images/
│   ├── image_001.png
│   ├── image_002.jpg
│   └── image_003.jpeg
│
├── 01_inbox_chat_exports/
│   ├── chatgpt_export.json
│   ├── claude_export.md
│   └── selected_conversations.md
│
├── 02_processed/
│   ├── processed_images/
│   └── processed_chats/
│
├── 03_outputs/
│   ├── image_index.csv
│   ├── topic_map.md
│   ├── weekly_summary.md
│   ├── open_questions.md
│   ├── reminders.md
│   └── low_value_archive.md
│
├── 04_topic_folders/
│   ├── AI_Infrastructure/
│   ├── Market_Valuation/
│   ├── Private_Credit/
│   ├── Portfolio_Analytics/
│   ├── Automation_and_AI_Agents/
│   └── Real_Estate/
│
└── 99_originals_backup/
```

## 5.3 כלל בטיחות בסיסי

```text
אל תמחק קבצים מקוריים.
אל תשנה שמות קבצים מקוריים בלי אישור.
אל תעביר קבצים מקוריים בלי אישור.
מותר ליצור קבצי פלט חדשים.
מותר ליצור אינדקסים.
מותר ליצור עותקים.
כל פעולה הרסנית מחייבת אישור מפורש.
```

## 5.4 הוראות קבועות ל־Cowork Project

אפשר לשים את זה כהוראות קבועות בפרויקט:

```text
אתה מנהל מערכת ידע אישית מתוך תמונות, גרפים, צילומי מסך, קבצי PDF ושיחות AI.

המטרה:
להפוך חומר יומיומי לידע מסודר לפי נושאים, רעיונות, שאלות ותזכורות.

עקרונות:
1. אל תמחק קבצים מקוריים.
2. אל תשנה שמות קבצים מקוריים בלי אישור מפורש.
3. אל תעביר קבצים מקוריים בלי אישור מפורש.
4. צור רק קבצי פלט חדשים: Markdown, CSV, JSON או תיקיות מוצעות.
5. לכל תמונה או שיחה צור סיכום קצר.
6. מיין כל פריט לנושא קיים אם אפשר.
7. אל תפתח נושא חדש על כל פרט איזוטרי.
8. תן לכל פריט Knowledge Score מ־1 עד 10.
9. פריטים עם ציון נמוך מ־4 יסווגו כ־archive_only ולא כידע מרכזי.
10. בסוף כל ריצה צור דוח פעולה.

תוצרי חובה בסוף ריצה:
- image_index.csv
- topic_map.md
- weekly_summary.md או batch_summary.md
- open_questions.md
- reminders.md
- low_value_archive.md
- unresolved_items.md

הגדרה של ידע חשוב:
ידע חשוב הוא פריט שיש בו טענה עקרונית, נתון משמעותי, מושג שחוזר, קשר בין רעיונות, שאלה פתוחה חשובה, או שימוש חוזר בעבודה.

הגדרה של רעש:
רעש הוא פריט חד־פעמי, איזוטרי, לא ברור, לא קשור לתחומי הליבה, או כזה שאין בו רעיון ניתן לשימוש חוזר.
```

## 5.5 פרומפט ריצה ראשון ל־Cowork

```text
אני רוצה להתחיל Batch ראשון של מערכת ידע אישית.

עבוד רק על התיקייה:
KnowledgeCapture_Cowork/00_inbox_images

מטרה:
לנתח את התמונות, להבין מה הנושא שלהן, לסכם רעיונות חשובים, ולמיין אותן לפי נושאים.

כללים:
- אל תמחק כלום.
- אל תשנה שמות קבצים.
- אל תעביר קבצים.
- צור רק קבצי פלט חדשים בתיקיית 03_outputs.
- אם אתה לא בטוח, כתוב "דורש בדיקה".
- אל תמציא נתונים שלא מופיעים בתמונה.

פלטים נדרשים:
1. image_index.csv
2. batch_summary.md
3. topic_map.md
4. open_questions.md
5. reminders.md
6. low_value_archive.md
7. unresolved_items.md

לכל תמונה תחלץ:
- filename
- title
- main_topic
- subtopics
- summary
- key_claims
- numbers
- open_questions
- suggested_tags
- knowledge_score
- confidence
- reason_for_score
```

## 5.6 תוצר CSV רצוי מ־Cowork

```csv
filename,title,main_topic,subtopics,summary,key_claims,numbers,open_questions,tags,knowledge_score,confidence,reason_for_score
image_001.png,Cloud AI backlog concentration,AI Infrastructure,"cloud, backlog, OpenAI, Anthropic","The chart shows concentration of cloud backlog in AI customers.","AI demand supports cloud growth; concentration risk exists","Microsoft 627B; Oracle 553B","How binding are these commitments?","AI, Cloud, Capex",9,medium,"Important link between AI infrastructure and cloud revenue visibility"
```

## 5.7 תזכורות בתוך Cowork

בשלב Cowork, אין צורך בהתחלה לחבר ל־Calendar או Windows Notifications. מספיק קובץ `reminders.md`.

דוגמה:

```markdown
# Reminders

## השבוע
- לבדוק מחדש את הקשר בין AI capex לבין ביקוש לחשמל.
- לחזור לגרף Forward P/E ולבדוק האם הירידה במכפיל נובעת מעליית רווחים או מירידת מחיר.

## עוד שבועיים
- לסכם את כל התמונות בנושא AI Infrastructure.
- לבדוק האם מופיעים שוב מושגים כמו backlog, capex, data centers, GPUs.

## עוד חודש
- ליצור דוח נושא: AI Infrastructure — מה למדתי החודש?
```

## 5.8 יתרונות Cowork

- התחלה מהירה.
- לא דורש בניית מערכת.
- טוב לעבודה עם תיקיות וקבצים.
- טוב לסיכומים, מיון, יצירת Markdown/CSV.
- מתאים ל־MVP.
- מאפשר להבין איך אתה רוצה שהמערכת תיראה לפני שבונים אותה.

## 5.9 חסרונות Cowork

- פחות שליטה ב־Schema.
- פחות שליטה בעלויות לעומת API מנוהל.
- פחות מתאים לריצה אוטומטית קבועה.
- קשה יותר לקבל Audit Log מדויק.
- לא אידיאלי אם צריך חיפוש סמנטי, DB, API endpoints ודשבורד קבוע.
- צריך להיזהר בהרשאות לקבצים רגישים.

---

# 6. אפשרות ב׳ בפירוט — אפליקציה עצמאית עם Claude Code + API

## 6.1 מה הרעיון

במקום לתת ל־Cowork לעשות את העבודה, בונים אפליקציה משלך.

Claude Code עוזר לבנות את הקוד, אבל האפליקציה עצמה מבצעת את התהליך באופן קבוע.

```text
תמונה חדשה בתיקייה
↓
File watcher מזהה אותה
↓
Worker שולח אותה ל־AI Vision API
↓
מתקבל JSON מובנה
↓
הנתונים נשמרים ב־SQLite
↓
הדשבורד מציג נושאים, תמונות, סיכומים ותזכורות
```

## 6.2 ארכיטקטורה מומלצת

```text
Local Computer / Internal Server
│
├── KnowledgeCapture/inbox
│   ├── images
│   ├── chat_exports
│   ├── pdfs
│   └── notes
│
├── Python Backend
│   ├── FastAPI
│   ├── SQLite
│   ├── SQLAlchemy
│   ├── file watcher
│   ├── AI API client
│   ├── OCR / PDF parser
│   └── reminders engine
│
├── AI Layer
│   ├── Claude API
│   ├── Gemini API
│   └── OpenAI API
│
└── Browser Dashboard
    ├── latest captures
    ├── topics
    ├── search
    ├── source previews
    ├── open questions
    ├── reminders
    └── weekly reports
```

## 6.3 סטאק מומלץ

```text
Python
FastAPI
SQLite
SQLAlchemy
Jinja2 או React פשוט
Local folders
AI Vision API
Markdown export
CSV export
```

בשלב ראשון עדיף לא להשתמש ב־Supabase / MongoDB / Cloud Hosting.  
המערכת יכולה לרוץ מקומית על מחשב או שרת פנימי.

## 6.4 מבנה תיקיות לאפליקציה

```text
KnowledgeCapture_App/
│
├── data/
│   ├── inbox/
│   │   ├── images/
│   │   ├── pdfs/
│   │   ├── chat_exports/
│   │   └── notes/
│   │
│   ├── processed/
│   ├── originals_backup/
│   └── exports/
│
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── ai_client.py
│   ├── processors/
│   │   ├── image_processor.py
│   │   ├── chat_processor.py
│   │   ├── pdf_processor.py
│   │   └── topic_classifier.py
│   ├── routes/
│   │   ├── captures.py
│   │   ├── topics.py
│   │   ├── reminders.py
│   │   └── search.py
│   └── templates/
│       ├── dashboard.html
│       ├── capture_detail.html
│       ├── topic_detail.html
│       └── reminders.html
│
├── prompts/
│   ├── analyze_image.md
│   ├── classify_topic.md
│   ├── score_knowledge.md
│   ├── summarize_chat.md
│   └── create_reminders.md
│
├── database/
│   └── knowledge.db
│
├── requirements.txt
└── README.md
```

## 6.5 טבלאות בסיס נתונים

### captures

```text
id
source_type
file_path
original_filename
created_at
processed_at
title
summary
main_topic_id
knowledge_score
confidence
status
raw_ai_json
```

### topics

```text
id
name
description
parent_topic_id
created_at
last_updated
importance_score
```

### tags

```text
id
name
normalized_name
```

### capture_tags

```text
capture_id
tag_id
```

### claims

```text
id
capture_id
claim_text
claim_type
confidence
```

### numbers

```text
id
capture_id
label
value
unit
context
```

### open_questions

```text
id
capture_id
topic_id
question
importance_score
status
created_at
```

### reminders

```text
id
topic_id
capture_id
question
due_date
status
reminder_type
created_at
completed_at
```

### chat_messages

```text
id
conversation_id
role
content
created_at
knowledge_score
is_relevant
```

### conversations

```text
id
source_platform
title
created_at
imported_at
summary
main_topic_id
relevance_score
status
```

## 6.6 JSON אחיד לניתוח תמונה

```json
{
  "source_type": "image",
  "title": "Cloud AI backlog concentration",
  "main_topic": "AI Infrastructure",
  "subtopics": [
    "Cloud revenue backlog",
    "OpenAI",
    "Anthropic",
    "Data center demand",
    "Customer concentration"
  ],
  "summary": "The chart shows that a large share of cloud providers' revenue backlog is linked to OpenAI and Anthropic commitments.",
  "key_claims": [
    "AI companies are becoming major cloud customers.",
    "Cloud backlog may be concentrated in a few AI clients.",
    "The market may be pricing future AI infrastructure demand aggressively."
  ],
  "numbers": [
    {
      "label": "Microsoft backlog",
      "value": "627",
      "unit": "USD billions",
      "context": "Total backlog shown in chart"
    }
  ],
  "open_questions": [
    "How binding are these cloud commitments?",
    "How much of this backlog will convert into recognized revenue?",
    "Is there circular financing between cloud providers and AI companies?"
  ],
  "suggested_tags": [
    "AI",
    "Cloud",
    "Big Tech",
    "Capex",
    "Backlog",
    "Customer Concentration"
  ],
  "knowledge_score": 9,
  "confidence": "medium",
  "reason_for_score": "The image connects AI infrastructure demand, cloud revenue visibility and concentration risk."
}
```

## 6.7 פרומפט ל־Claude Code לבניית האפליקציה

```text
Build a local web app for personal knowledge capture.

Core goal:
The app should ingest images, chat exports, PDFs and notes, analyze them with an AI model, classify them into topics, score their knowledge value, and create reminders/questions for future review.

Tech stack:
- Python
- FastAPI
- SQLite
- SQLAlchemy
- Jinja2 templates for simple browser UI
- Local file storage

Core requirements:
1. Watch or scan a local folder called data/inbox/images.
2. For each new image, send it to an AI vision model.
3. Extract structured JSON with:
   - title
   - summary
   - main_topic
   - subtopics
   - key_claims
   - numbers
   - open_questions
   - suggested_tags
   - knowledge_score
   - confidence
   - reason_for_score
4. Store all results in SQLite.
5. Show a dashboard with:
   - latest captures
   - topic list
   - source image preview
   - summaries
   - open questions
   - reminders
6. Add manual review states:
   - pending_review
   - approved
   - archived
   - low_value
7. Never delete or modify original files.
8. Create exports:
   - topic_map.md
   - weekly_summary.md
   - open_questions.md
   - reminders.md
   - image_index.csv
9. Include a .env.example file but never commit real API keys.
10. Add a README with setup instructions for Windows.

Security constraints:
- Do not store API keys in source code.
- Use .env for local development.
- Add .gitignore for .env, database files and local images.
- Do not send entire folders blindly to the AI API.
- Process one file at a time.
- Log every file processed.
```

## 6.8 יתרונות האפליקציה העצמאית

- שליטה מלאה בדאטה.
- אפשר למדוד עלויות לפי קריאות API.
- אפשר לבנות Search.
- אפשר לבנות Audit Log.
- אפשר לבנות דשבורד מותאם.
- אפשר להוסיף תזכורות אמיתיות.
- אפשר לחבר בעתיד ל־Calendar / Gmail / Drive.
- מתאים יותר אם המערכת הופכת לכלי עבודה קבוע.

## 6.9 חסרונות האפליקציה העצמאית

- דורש פיתוח.
- דורש תחזוקה.
- דורש ניהול אבטחה.
- דורש עיצוב טוב של prompts ו־schema.
- איטי יותר להתחלה.
- יש יותר נקודות כשל טכניות.

---

# 7. ייבוא היסטוריית שיחות מצ׳אטבוטים

## 7.1 למה לייבא שיחות AI

חלק משמעותי מהידע האמיתי נוצר דווקא בשיחות עם AI:

- הסברים פיננסיים.
- נוסחאות Excel.
- רעיונות לאוטומציה.
- ניתוחים של שוק ההון.
- אפיוני מערכות.
- שאלות חוזרות.
- תיקוני טעויות.
- תובנות שנבנות לאורך זמן.

לכן כדאי להוסיף למערכת מקור מידע בשם `chat_exports`.

## 7.2 סוגי שיחות שרוצים לשמור

לא כל שיחה שווה שמירה.

שיחות עם ערך גבוה:

- הסבר עקרוני.
- ניתוח פיננסי.
- תהליך עבודה.
- קוד או נוסחה שימושית.
- אפיון מערכת.
- החלטה ארכיטקטונית.
- רעיון שחוזר בכמה הקשרים.
- שאלות פתוחות ללמידה.

שיחות עם ערך נמוך:

- חיפוש חד־פעמי.
- טריוויה.
- נושא איזוטרי שלא קשור ללמידה.
- שיחה קצרה בלי מסקנה.
- ניסוח טקסט חד־פעמי ללא ערך עתידי.
- מידע שכבר לא רלוונטי.

## 7.3 מבנה תיקיות לייבוא שיחות

```text
chat_exports/
│
├── raw/
│   ├── chatgpt_export.zip
│   ├── claude_export.md
│   └── gemini_export.json
│
├── extracted/
│   ├── conversations.json
│   ├── conversation_001.md
│   └── conversation_002.md
│
├── filtered/
│   ├── high_value.md
│   ├── medium_value.md
│   └── low_value_archive.md
│
└── summaries/
    ├── chat_topics.md
    ├── recurring_questions.md
    └── reusable_knowledge.md
```

## 7.4 פייפליין לייבוא שיחות

```text
Export history from chatbot
↓
Extract conversations
↓
Split by conversation
↓
Summarize each conversation
↓
Assign topic
↓
Assign knowledge score
↓
Filter low-value content
↓
Save high-value insights to knowledge base
```

## 7.5 JSON לשיחה מיובאת

```json
{
  "source_type": "chat_export",
  "platform": "ChatGPT",
  "conversation_title": "ETF index tracking and rebalancing",
  "date_range": "2026-05",
  "main_topic": "ETF Mechanics",
  "subtopics": [
    "Index weights",
    "ETF tracking",
    "Rebalancing",
    "Creation-redemption",
    "Market cap weighting"
  ],
  "summary": "The conversation clarified how an ETF can track an index even though individual stock weights drift between rebalances.",
  "reusable_knowledge": [
    "In market-cap weighted indexes, weights drift naturally as prices move.",
    "ETF tracking is maintained through holding the basket and arbitrage mechanisms.",
    "Rebalancing dates do not mean weights are fixed between rebalances."
  ],
  "open_questions": [
    "How exactly do authorized participants arbitrage ETF deviations in stressed markets?"
  ],
  "suggested_tags": [
    "ETF",
    "Indexing",
    "Rebalancing",
    "Market Structure"
  ],
  "knowledge_score": 8,
  "should_keep": true,
  "reason_for_score": "The conversation produced reusable understanding of ETF mechanics."
}
```

---

# 8. מנגנון סינון ידע מול רעש

## 8.1 למה צריך סינון

אם שומרים כל דבר, המערכת נהיית זבל דיגיטלי.

המטרה היא לא לאסוף כמה שיותר מידע, אלא לשמר ידע אמיתי.

ידע אמיתי הוא מידע שיש לו שימוש חוזר, עומק מושגי, קשר לנושאי ליבה, או יכולת לשפר הבנה עתידית.

## 8.2 תחומי ליבה אישיים

המערכת צריכה לתת עדיפות לנושאים כמו:

```text
פיננסים
שוק ההון
מדדים ו־ETF
קרנות השקעה
Private Equity
Private Credit
BDC
נדל״ן
AI
אוטומציה
Claude / GPT / Gemini
פיתוח אפליקציות פנימיות
Excel וניתוחי ביצועים
Make.com
מערכות ידע
רגולציה פיננסית
תזונה ובריאות שימושית
מתמטיקה / כלכלה / קוואנט
```

## 8.3 מה נחשב ידע איכותי

פריט מקבל ציון גבוה אם הוא כולל:

1. טענה עקרונית.
2. גרף או נתון משמעותי.
3. מושג שחוזר בכמה מקורות.
4. קשר בין רעיונות.
5. שאלה פתוחה טובה.
6. שימוש חוזר בעבודה.
7. הסבר טכני שאפשר לחזור אליו.
8. נוסחה, קוד, תהליך או מתודולוגיה.
9. החלטה ארכיטקטונית.
10. נושא שמתחבר לתמונה רחבה יותר.

## 8.4 מה נחשב רעש

פריט מקבל ציון נמוך אם הוא:

- חד־פעמי.
- איזוטרי.
- לא קשור לתחומי הליבה.
- לא ברור.
- חסר מסקנה.
- חיפוש מקרי.
- ניסוח הודעה חד־פעמי.
- תמונה בלי רעיון ברור.
- שיחה שלא מייצרת ידע עתידי.

## 8.5 Knowledge Score

```text
1-3  = רעש / ארכיון בלבד
4-5  = אולי שימושי, אבל לא מרכזי
6-7  = ידע שימושי
8-9  = ידע חשוב שצריך לחזור אליו
10   = רעיון יסודי / נושא ליבה / דורש מעקב
```

## 8.6 נוסחת דירוג רעיונית

```text
knowledge_score =
  relevance_to_core_topics
+ conceptual_depth
+ numeric_or_visual_value
+ recurrence_across_sources
+ actionability
+ open_questions_value
- randomness_penalty
- one_off_penalty
- unclear_source_penalty
```

## 8.7 החלטת שמירה

```text
score >= 8:
  Save as core knowledge
  Create reminder
  Add to topic map

score 6-7:
  Save as useful knowledge
  Add to topic page

score 4-5:
  Save to archive only
  No reminder unless manually approved

score <= 3:
  Low-value archive
  Do not include in main summaries
```

---

# 9. מפת נושאים מוצעת

```text
AI and Automation
├── Claude Code
├── Claude Cowork
├── AI Agents
├── Gemini API
├── OpenAI API
├── Make.com
├── Internal Apps
└── Knowledge Systems

AI Infrastructure
├── Cloud Backlog
├── Data Centers
├── GPU Demand
├── Electricity Demand
├── Capex Cycle
└── Circular Financing Risk

Market Valuation
├── Forward P/E
├── Trailing P/E
├── Earnings Revisions
├── Multiple Compression
├── Tech Sector Valuation
└── S&P 500 Concentration

ETF and Market Structure
├── Index Weights
├── ETF Tracking
├── Creation Redemption
├── Rebalancing
└── Arbitrage Mechanisms

Private Markets
├── Private Equity
├── Private Credit
├── BDCs
├── NAV Discounts
├── Tender Offers
├── PIK Income
└── Non-Accruals

Portfolio Analytics
├── MTD
├── YTD
├── Weighted Returns
├── MOIC
├── TVPI
├── DPI
└── IRR

Excel and Data Workflows
├── Dynamic Formulas
├── Portfolio Tables
├── Data Validation
├── Power Query
├── VBA / Office Scripts
└── Reporting Automation

Real Estate
├── Urban Renewal
├── Parcel / Subparcel
├── Planning Data
├── Rent and Prices
└── Israel Real Estate Market
```

---

# 10. תזכורות ושאלות חזרה

## 10.1 תפקיד התזכורות

התזכורות לא מיועדות רק להזכיר “לעשות משהו”.  
הן מיועדות להפוך ידע פסיבי לידע פעיל.

דוגמאות:

```text
חזור לגרף Forward P/E ושאל:
האם המכפיל ירד בגלל ירידת מחיר או בגלל עליית תחזיות רווח?

חזור לנושא AI Infrastructure ושאל:
האם הביקוש לחשמל הוא צוואר בקבוק אמיתי או נרטיב שוק?

חזור לנושא BDC ושאל:
האם דיסקאונט ל־NAV משקף בעיית אשראי אמיתית או רק פחד נזילות?
```

## 10.2 סוגי תזכורות

```text
review_question
follow_up_research
weekly_summary
monthly_topic_review
compare_sources
update_numbers
```

## 10.3 טבלת תזכורות

```text
id
topic
question
source_item
due_date
status
importance
```

## 10.4 דוגמת reminders.md

```markdown
# Reminders

## להיום
- לבדוק מחדש את הגרף על Tech Forward P/E ולנסח את ההבדל בין Forward P/E ל־Trailing P/E.

## השבוע
- לסכם את כל התמונות בנושא AI Infrastructure.
- לבדוק אילו נושאים חזרו לפחות 3 פעמים.

## החודש
- ליצור דוח עומק על הקשר בין AI, ענן, חשמל, GPU ו־Capex.
```

---

# 11. תוצרי פלט קבועים

## 11.1 image_index.csv

טבלה של כל התמונות שנותחו.

עמודות:

```text
filename
created_at
processed_at
title
main_topic
subtopics
summary
key_claims
numbers
open_questions
tags
knowledge_score
confidence
status
```

## 11.2 topic_map.md

מפת נושאים מתעדכנת.

```markdown
# Topic Map

## AI Infrastructure

### רעיונות מרכזיים
- AI מגדיל ביקוש לענן, GPU ודאטה סנטרים.
- חלק מהביקוש עשוי להיות קשור להתחייבויות גדולות של חברות AI.
- יש סיכון ריכוזיות אם מעט לקוחות אחראים לחלק גדול מה־backlog.

### שאלות פתוחות
- כמה מה־backlog מחייב חוזית?
- כמה מזה יתורגם להכנסות אמיתיות?
- האם יש מעגליות מימונית בין ספקי ענן לחברות AI?
```

## 11.3 weekly_summary.md

```markdown
# Weekly Knowledge Summary

## נושאים שחזרו השבוע
1. AI Infrastructure
2. Market Valuation
3. Claude Cowork / AI Agents

## רעיונות חשובים
- Forward P/E יכול לרדת גם כשהמחיר קרוב לשיא, אם תחזיות הרווח עולות.
- Cowork מתאים ל־MVP מובנה, אבל Backend + API מתאים יותר למערכת סופית.

## שאלות לחזרה
- מתי עדיף Cowork ומתי עדיף API?
- איך למדוד האם תמונה היא ידע חשוב או רעש?
```

## 11.4 open_questions.md

```markdown
# Open Questions

## AI Infrastructure
- האם התחייבויות הענן של חברות AI הן חוזיות ומחייבות או הצהרות מסגרת?
- האם Capex בענן יוצר מחזור השקעות מסוכן?

## Market Valuation
- האם ירידת Forward P/E בסקטור הטכנולוגיה נובעת בעיקר מעליית תחזיות רווח?

## Knowledge System
- האם Cowork מספיק לניהול אישי לאורך זמן או שצריך DB עצמאי?
```

---

# 12. אבטחה והרשאות

## 12.1 כללים כלליים

```text
לא עובדים על תיקיית מקור רגישה.
לא נותנים גישה לכל המחשב.
לא נותנים גישה לתיקיות לקוחות אמיתיות בשלב הראשון.
לא שולחים קבצים פיננסיים רגישים ל־API בלי בדיקה.
לא שומרים API keys בקוד.
לא עושים commit לקבצי .env.
```

## 12.2 עבודה בטוחה עם Cowork

```text
תיקיית ניסוי בלבד.
עותקים בלבד.
אין מחיקה.
אין שינוי שמות בלי אישור.
אין גישה לבנק, מערכות השקעות, Gmail מלא או Drive מלא.
כל Batch קטן: 20-50 פריטים.
```

## 12.3 עבודה בטוחה עם API

```text
API key בסביבת Secret / .env בלבד.
Spend limit.
Logging לכל קריאה.
Processing file-by-file.
No bulk upload blindly.
Manual review before saving as core knowledge.
```

---

# 13. עלויות ושליטה בתקציב

## 13.1 Cowork

Cowork יכול להיות נוח, אבל העלות פחות צפויה כי הוא עושה משימות מרובות שלבים.

כדי לשלוט:

```text
להתחיל ב־20 תמונות.
לבקש קודם תוכנית פעולה.
לא לבקש ממנו “תעבור על הכול” בלי הגבלה.
להגדיר פלטים ברורים.
לעבוד ב־Batch.
לבדוק Usage / Credits.
לא לעבוד על אלפי קבצים בבת אחת.
```

## 13.2 API

ב־API קל יותר למדוד:

```text
כמה קבצים נותחו
כמה טוקנים נצרכו
כמה עלתה כל ריצה
כמה עלה כל Batch
```

אפשר להוסיף טבלת cost_log:

```text
id
run_id
model
input_tokens
output_tokens
estimated_cost
created_at
```

---

# 14. תוכנית עבודה מעשית

## שלב 1 — Cowork MVP

משך: יום עד כמה ימים.

מטרה:
לראות אם Cowork יודע להפוך תמונות ושיחות לידע מסודר.

פעולות:

1. ליצור תיקיית `KnowledgeCapture_Cowork`.
2. לשים 20-50 תמונות.
3. להוסיף 5-10 שיחות AI נבחרות.
4. לפתוח Cowork Project.
5. להדביק הוראות קבועות.
6. להריץ Batch ראשון.
7. לבדוק את הפלט.
8. לשפר את הפרומפט.

תוצר:

```text
image_index.csv
topic_map.md
batch_summary.md
open_questions.md
reminders.md
low_value_archive.md
```

## שלב 2 — פורמט קבוע

משך: כמה ימים.

מטרה:
לקבע את מבנה התוצר.

פעולות:

1. להחליט אילו עמודות יש ב־CSV.
2. להחליט אילו קבצי Markdown נדרשים.
3. להחליט מהו Knowledge Score טוב.
4. לבנות רשימת נושאי ליבה.
5. לבנות כללי סינון.

## שלב 3 — Dashboard פשוט עם Claude Code

משך: כמה ימים עד שבוע.

מטרה:
לבנות אפליקציה שקוראת את קבצי ה־CSV/Markdown ומציגה אותם בדפדפן.

פעולות:

1. Claude Code בונה FastAPI app.
2. קוראים את `image_index.csv`.
3. מציגים תמונות, נושאים וסיכומים.
4. מציגים תזכורות ושאלות פתוחות.
5. מוסיפים חיפוש בסיסי.

## שלב 4 — מעבר ל־API מלא

משך: שבועות.

מטרה:
להפוך את המערכת לאוטומטית באמת.

פעולות:

1. להוסיף SQLite.
2. להוסיף file watcher.
3. להוסיף AI API client.
4. לעבד תמונות אוטומטית.
5. להוסיף Manual Review.
6. להוסיף reminders engine.
7. להוסיף Export.

---

# 15. מתי לבחור Cowork ומתי API

## לבחור Cowork אם:

- רוצים להתחיל מהר.
- לא רוצים לכתוב קוד עכשיו.
- רוצים מוצר מובנה.
- רוצים לבדוק אם הקונספט עובד.
- רוצים ש־AI יעבוד על תיקייה ויחזיר קבצי Markdown/CSV.
- רוצים תהליך חצי־ידני עם הרבה גמישות.

## לבחור Backend + API אם:

- רוצים מערכת קבועה.
- רוצים דשבורד אמיתי.
- רוצים DB וחיפוש.
- רוצים שליטה מלאה בעלויות.
- רוצים Audit Log.
- רוצים לעבד מאות/אלפי קבצים לאורך זמן.
- רוצים אינטגרציות עתידיות ל־Drive/Gmail/Calendar.

## הבחירה המעשית

```text
עכשיו:
Cowork

אחרי שהפורמט ברור:
Claude Code לבניית Dashboard

בהמשך:
Backend + API לעיבוד אוטומטי מלא
```

---

# 16. סיכום קצר

המערכת הרצויה היא מערכת אישית לרכישת ידע.

יש שתי דרכים:

1. **Cowork** — מוצר מובנה, מהיר, טוב לניסוי ולניהול ידני־חכם של תיקיות, תמונות ושיחות.
2. **Backend + API** — מערכת עצמאית, יותר חזקה, יותר נשלטת, מתאימה לדשבורד ואוטומציה לאורך זמן.

הדרך הנכונה היא לא לבחור מיד אחת ולזרוק את השנייה, אלא להשתמש בהן בשלבים:

```text
Cowork = להבין ולחדד את שיטת העבודה
Claude Code = לבנות את האפליקציה
API = להריץ מערכת אוטומטית מלאה
```

השורה התחתונה:

> להתחיל עם Cowork כמוצר מובנה, להפיק ממנו קבצי Markdown/CSV מסודרים, ואז להשתמש ב־Claude Code כדי לבנות סביב זה דשבורד. רק אם זה מוכיח את עצמו — לעבור ל־Backend + API מלא.

---

# 17. נספח: פרומפט מלא ל־Batch עבודה ב־Cowork

```text
אתה מנהל מערכת ידע אישית.

עבוד על התיקייה:
KnowledgeCapture_Cowork/00_inbox_images

מטרה:
לנתח תמונות, גרפים וצילומי מסך, לסכם אותם, למיין לפי נושאים, וליצור שאלות חזרה ותזכורות.

אל תעשה:
- אל תמחק קבצים.
- אל תשנה שמות קבצים.
- אל תעביר קבצים.
- אל תמציא נתונים.

כן תעשה:
- צור image_index.csv.
- צור topic_map.md.
- צור batch_summary.md.
- צור open_questions.md.
- צור reminders.md.
- צור low_value_archive.md.
- צור unresolved_items.md.

לכל תמונה חלץ:
1. filename
2. title
3. main_topic
4. subtopics
5. summary
6. key_claims
7. numbers
8. open_questions
9. suggested_tags
10. knowledge_score 1-10
11. confidence
12. reason_for_score

כללי סינון:
- אם הפריט קשור לנושא ליבה ויש בו רעיון חוזר או עקרוני, תן ציון גבוה.
- אם הפריט חד־פעמי, איזוטרי או לא ברור, תן ציון נמוך.
- אל תפתח נושא חדש אם אפשר לשייך לנושא קיים.
- בסוף תן לי סיכום של הנושאים החשובים ביותר ומה כדאי ללמוד בהמשך.
```

---

# 18. נספח: פרומפט מלא ל־Claude Code לבניית Dashboard

```text
Build a local FastAPI dashboard for a personal knowledge capture system.

Input files:
- image_index.csv
- topic_map.md
- open_questions.md
- reminders.md

App requirements:
1. Show dashboard homepage with latest captures.
2. Show list of topics.
3. Show topic detail page with related images and summaries.
4. Show open questions.
5. Show reminders.
6. Allow filtering by knowledge_score.
7. Allow filtering by main_topic.
8. Do not modify source files.
9. Add README with Windows setup instructions.
10. Use SQLite only if needed; otherwise start by reading CSV/Markdown.

Tech stack:
- Python
- FastAPI
- Jinja2
- Pandas optional
- Local static files for images

Security:
- No external hosting.
- Localhost only.
- No API keys in code.
- Add .gitignore.
```
