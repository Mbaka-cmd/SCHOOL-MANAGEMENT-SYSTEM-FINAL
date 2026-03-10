# 🏫 SchoolSaaS — School Management System
> Built for Kenyan Secondary Schools · Powered by Django · M-Pesa Ready

![Python](https://img.shields.io/badge/Python-3.11-blue) ![Django](https://img.shields.io/badge/Django-5.1-green) ![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue) ![M-Pesa](https://img.shields.io/badge/Payments-M--Pesa-brightgreen)

---

## 🌟 Live Demo
**School:** St. Bakhita Chuka Girls High School  
**URL:** *(deploy to get live link)*  
**Admin:** `/admin/` · **Portal:** `/portal/` · **Parent:** `/portal/parent/`

---

## 📦 What's Inside

| Module | Features |
|--------|----------|
| 🌐 **Public Website** | Home, About, Academics, Gallery, KCSE Results, Contact |
| 👩‍🎓 **Student Management** | Enroll, bulk import, streams, profiles |
| 💰 **Fee Management** | Fee structures, payments, balances, receipts |
| 📱 **M-Pesa STK Push** | Safaricom Daraja API, webhook reconciliation |
| 📝 **Exams & Results** | Enter marks, auto-grade, report cards |
| 📚 **Library** | Books, borrowing, returns, KES 50/day fines |
| 🗓️ **Timetable** | Class schedules per stream |
| ✅ **Attendance** | Daily per-stream, present/absent/late/excused |
| 📢 **Notice Board** | Post notices by audience & priority |
| 👨‍👩‍👧 **Parent Portal** | Fee status, results, notices, comments |
| 🎓 **Student Portal** | Timetable, results, library status |
| 📲 **Bulk SMS** | Africa's Talking integration |
| 📊 **Analytics Dashboard** | School-wide stats and insights |
| 👨‍💼 **Staff Management** | Staff profiles, roles |

---

## 🚀 Quick Start (New School Setup)

### 1. Clone & Install
```bash
git clone https://github.com/Mbaka-cmd/SCHOOL-MANAGEMENT-SYSTEM-FINAL.git
cd SCHOOL-MANAGEMENT-SYSTEM-FINAL
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
```
Edit `.env` with your school's credentials:
```env
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
AT_USERNAME=your-africastalking-username
AT_API_KEY=your-africastalking-api-key
```

### 3. Database Setup
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### 4. First Login
- Go to `http://127.0.0.1:8000/admin/`
- Create your School record
- Add streams, fee structures, staff
- Start enrolling students

---

## 💳 M-Pesa Integration

This system uses **Safaricom Daraja API STK Push** for fee payments.

**Setup:**
1. Register at [developer.safaricom.co.ke](https://developer.safaricom.co.ke)
2. Get Consumer Key, Consumer Secret, Shortcode, Passkey
3. Add to `.env`
4. Set callback URL: `https://yourdomain.com/fees/mpesa/callback/`

---

## 📲 SMS Notifications (Africa's Talking)

Automatic SMS sent for:
- Fee payment confirmation
- Exam results release
- Notice board announcements

**Setup:**
1. Register at [africastalking.com](https://africastalking.com)
2. Add `AT_USERNAME` and `AT_API_KEY` to `.env`

---

## 🏫 Deploying for a New School

This system is designed to be **cloned per school**. Each school gets their own instance.

**What to change per school:**
```
1. School name, logo, motto → Admin panel → Schools
2. Colors → templates/base.html (search #C0392B)
3. Background photo → static/ folder
4. Fee structures → Admin panel → Fees
5. Streams/classes → Admin panel → Academics
6. .env credentials → per school email, M-Pesa, SMS
```

**Time to set up a new school: 1–3 days**

---

## 🔒 Security

- JWT-based authentication
- Role-based access (Admin, Teacher, Student, Parent)
- `.env` for all secrets — never committed to git
- Student data protected — `db.sqlite3` excluded from git
- CSRF protection on all forms
- Password hashing via Django's built-in system

---

## 🛠️ Tech Stack

```
Backend:     Python 3.11, Django 5.1, SQLAlchemy
Database:    SQLite (dev) → PostgreSQL (production)
Payments:    M-Pesa STK Push (Safaricom Daraja API)
SMS:         Africa's Talking
Frontend:    HTML5, CSS3, Bootstrap 5, Vanilla JS
Deployment:  Gunicorn + Nginx + Docker (ready)
Static:      WhiteNoise
```

---

## 📁 Project Structure

```
├── academics/          # Streams, subjects, timetable logic
├── accounts/           # Auth, roles, user management
├── attendance/         # Daily attendance per stream
├── communications/     # SMS + email notifications
├── exams/              # Marks, grades, report cards
├── fees/               # Fee structures, payments, M-Pesa
├── library/            # Books, borrowing, fines
├── notices/            # Announcement board
├── portal/             # Student & parent portals
├── schools/            # School profile, admin dashboard
├── staff/              # Staff management
├── students/           # Student enrollment, profiles
├── timetable/          # Class schedules
├── website/            # Public-facing school website
├── templates/          # All HTML templates
├── static/             # CSS, JS, images
├── config/             # Django settings, URLs
├── .env.example        # Environment variables template
└── requirements.txt    # Python dependencies
```

---

## 📞 Support & Licensing

**Built by:** Mercy Mbaka  
**Contact:** official.mercymbaka@gmail.com  
**License:** Commercial — each school requires a separate license  

> ⚡ Built with a deployment-first philosophy. Working demo over perfect documentation.

---

*SchoolSaaS — Fast, practical, integration-heavy, built for real users, real payments, and real deployment.*