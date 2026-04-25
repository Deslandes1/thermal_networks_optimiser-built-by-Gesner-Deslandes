import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import os
from supabase import create_client, Client

# ========== FORCE GOOGLE ADSENSE META TAG INTO <head> ==========
components.html(
    """
    <head>
        <meta name="google-adsense-account" content="ca-pub-1238061430437782">
    </head>
    """,
    height=0,
)

# ---------- Supabase setup ----------
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(
    page_title="GlobalInternet.py – Python Software Company",
    page_icon="🌐",
    layout="wide"
)

# ---------- Comment functions ----------
def get_comments(project_key):
    try:
        response = supabase.table("comments").select("*").eq("project_key", project_key).order("timestamp", desc=False).execute()
        return response.data
    except Exception as e:
        st.error(f"Error loading comments: {e}")
        return []

def add_comment(project_key, username, comment, parent_id=0, reply_to_username=""):
    try:
        supabase.table("comments").insert({
            "project_key": project_key,
            "username": username.strip() if username else "Anonymous",
            "comment": comment.strip(),
            "timestamp": datetime.now().isoformat(),
            "likes": 0,
            "parent_id": parent_id,
            "reply_to_username": reply_to_username
        }).execute()
        return True
    except Exception as e:
        st.error(f"Error adding comment: {e}")
        return False

def add_like(comment_id):
    try:
        supabase.rpc("increment_likes", {"row_id": comment_id}).execute()
    except:
        current = supabase.table("comments").select("likes").eq("id", comment_id).execute()
        if current.data:
            new_likes = current.data[0]["likes"] + 1
            supabase.table("comments").update({"likes": new_likes}).eq("id", comment_id).execute()

def delete_comment(comment_id, admin_password):
    if admin_password == "20082010":
        try:
            supabase.table("comments").delete().eq("id", comment_id).execute()
            return True
        except:
            return False
    return False

# ---------- IP Geolocation ----------
def get_location(ip):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,regionName,city,isp,lat,lon,query", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                return {
                    "country": data.get("country", "Unknown"),
                    "region": data.get("regionName", "Unknown"),
                    "city": data.get("city", "Unknown"),
                    "isp": data.get("isp", "Unknown"),
                    "lat": data.get("lat"),
                    "lon": data.get("lon")
                }
    except Exception:
        pass
    return None

def send_visit_notification():
    try:
        try:
            visitor_ip = requests.get("https://api.ipify.org", timeout=5).text
        except:
            visitor_ip = "Unable to retrieve"
        location = get_location(visitor_ip) if visitor_ip != "Unable to retrieve" else None
        user_agent = "unknown (Streamlit Cloud)"
        subject = "🌐 New visitor on GlobalInternet.py website"
        body = f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nIP: {visitor_ip}\n"
        if location:
            body += f"📍 Country: {location['country']}\n📍 Region: {location['region']}\n📍 City: {location['city']}\n🛜 ISP: {location['isp']}\n"
        else:
            body += "📍 Location: Could not determine\n"
        body += f"User Agent: {user_agent}\n"
        try:
            sender = st.secrets["email"]["sender"]
            password = st.secrets["email"]["password"]
            receiver = st.secrets["email"]["receiver"]
            msg = MIMEMultipart()
            msg["From"] = sender
            msg["To"] = receiver
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(sender, password)
                server.sendmail(sender, receiver, msg.as_string())
        except:
            pass
    except:
        pass

if "notification_sent" not in st.session_state:
    send_visit_notification()
    st.session_state.notification_sent = True

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

st.markdown("""
<style>
    .main { padding: 0rem 1rem; }
    .hero {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .hero h1 { font-size: 3rem; margin-bottom: 0.5rem; }
    .hero p { font-size: 1.2rem; opacity: 0.9; }
    .card {
        background-color: #f8f9fa;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s;
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    .card:hover { transform: translateY(-5px); }
    .card h3 { color: #1e3c72; margin-top: 0; }
    .price { font-size: 1.5rem; font-weight: bold; color: #ff6b35; margin: 0.5rem 0; }
    .team-card {
        background-color: #f8f9fa;
        border-radius: 15px;
        padding: 1rem;
        text-align: center;
        transition: transform 0.3s;
        height: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .team-card:hover { transform: translateY(-5px); }
    .team-card h4 { color: #1e3c72; margin-bottom: 0.2rem; }
    .team-card p { color: #666; font-size: 0.9rem; margin-bottom: 0.5rem; }
    .team-card img {
        width: 100px;
        height: 100px;
        object-fit: cover;
        border-radius: 50%;
        margin-bottom: 0.5rem;
        border: 2px solid #1e3c72;
    }
    .footer {
        text-align: center;
        padding: 2rem;
        background-color: #1e3c72;
        color: white;
        border-radius: 20px;
        margin-top: 3rem;
    }
    .donation-box {
        background-color: #fff3e0;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin: 2rem 0;
    }
    .blue-text { color: #0000FF; font-weight: bold; }
    .big-globe { font-size: 120px; display: block; text-align: center; margin-bottom: 0.5rem; }
    .future-project-card {
        background-color: #f8f9fa;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 0.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s;
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    .future-project-card:hover { transform: translateY(-5px); }
    .future-project-card h3 { color: #1e3c72; margin: 0.5rem 0; }
    .future-project-card p { color: #333; flex-grow: 1; }
    .status-badge { color: #ff6b35; font-weight: bold; }
    .tech-badge { color: #00c9a7; font-weight: bold; }
    .comment-box {
        background-color: #f1f3f5;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .comment-meta { font-size: 0.8rem; color: #555; margin-bottom: 0.3rem; }
    .reply-box { margin-left: 2rem; border-left: 2px solid #ccc; padding-left: 1rem; }
    .like-button { background: none; border: none; cursor: pointer; font-size: 1rem; padding: 0; margin-right: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# FULL DICTIONARIES (ENGLISH, FRENCH, SPANISH)
# ============================================================
lang_en = {
    "hero_title": "GlobalInternet.py",
    "hero_sub": "Build with Python. Deliver with Speed. Innovate with AI.",
    "hero_desc": "From Haiti to the world – custom software that works online.",
    "about_title": "👨‍💻 About the Company",
    "about_text": """
    **GlobalInternet.py** was founded by **Gesner Deslandes** – owner, founder, and lead engineer.  
    We build **Python‑based software** on demand for clients worldwide. Like Silicon Valley, but with a Haitian touch and outstanding outcomes.
    
    - 🧠 **AI‑powered solutions** – chatbots, data analysis, automation  
    - 🗳️ **Complete election & voting systems** – secure, multi‑language, real‑time  
    - 🌐 **Web applications** – dashboards, internal tools, online platforms  
    - 📦 **Full package delivery** – we email you the complete code and guide you through installation
    
    Whether you need a company website, a custom software tool, or a full‑scale online platform – we build it, you own it.
    """,
    "office_photo_caption": "Gesner Deslandes talking avatar – introducing GlobalInternet.py",
    "humanoid_photo_caption": "Gesner Humanoid AI – our digital representative of innovation and software expertise.",
    "founder": "Founder & CEO",
    "founder_name": "Gesner Deslandes",
    "founder_title": "Engineer | AI Enthusiast | Python Expert",
    "cv_title": "📄 About the Owner – Gesner Deslandes",
    "cv_intro": "Python Software Builder | Web Developer | Technology Coordinator",
    "cv_summary": """
    Exceptionally driven leader and manager with a commitment to excellence and precision.  
    **Core competencies:** Leadership, Interpreting (English, French, Haitian Creole), Mechanical orientation, Management, Microsoft Office.
    """,
    "cv_experience_title": "💼 Professional Experience",
    "cv_experience": """
    **Technology Coordinator** – Be Like Brit Orphanage (2021–Present)  
    Set up Zoom meetings, maintain laptops/tablets, provide daily technical support, ensure smooth digital operations.

    **CEO & Interpreting Services** – Personalized tourism for NGO groups, mission teams, and individuals.

    **Fleet Manager / Dispatcher** – J/P Haitian Relief Organization  
    Managed 20+ vehicles, driver logs, maintenance schedules using Excel.

    **Medical Interpreter** – International Child Care  
    Accurate English–French–Creole medical interpretation.

    **Team Leader & Interpreter** – Can‑Do NGO  
    Led reconstruction projects.

    **English Teacher** – Be Like Brit (Preschool to NS4)

    **Document Translator** – United Kingdom Glossary & United States Work‑Rise Company
    """,
    "cv_education_title": "🎓 Education & Training",
    "cv_education": """
    - Vocational Training School – American English  
    - Diesel Institute of Haiti – Diesel Mechanic  
    - Office Computing Certification (October 2000)  
    - High School Graduate
    """,
    "cv_references": "📞 References available upon request.",
    "team_title": "👥 Our Team",
    "team_sub": "Meet the talented people behind GlobalInternet.py – hired April 2026.",
    "team_members": [
        {"name": "Gesner Deslandes", "role": "Founder & CEO", "since": "2021", "img": "https://raw.githubusercontent.com/Deslandes1/globalinternet_site.py/main/Gesner%20Deslandes.JPG"},
        {"name": "Gesner Junior Deslandes", "role": "Assistant to CEO", "since": "April 2026", "img": "https://raw.githubusercontent.com/Deslandes1/globalinternet_site.py/main/dreamina-2026-04-18-6690-Change%20the%20man's%20attire%20to%20a%20professiona....jpeg"},
        {"name": "Roosevelt Deslandes", "role": "Python Programmer", "since": "April 2026", "img": "https://raw.githubusercontent.com/Deslandes1/globalinternet_site.py/main/Roosevelt%20%20Software%20Builder.jpeg"},
        {"name": "Sebastien Stephane Deslandes", "role": "Python Programmer", "since": "April 2026", "img": "https://raw.githubusercontent.com/Deslandes1/globalinternet_site.py/main/35372.jpg"},
        {"name": "Zendaya Christelle Deslandes", "role": "Secretary", "since": "April 2026", "img": "https://raw.githubusercontent.com/Deslandes1/globalinternet_site.py/main/IMG_1411.jpg"}
    ],
    "services_title": "⚙️ Our Services",
    "services": [
        ("🐍 Custom Python Development", "Tailored scripts, automation, backend systems."),
        ("🤖 AI & Machine Learning", "Chatbots, predictive models, data insights."),
        ("🗳️ Election & Voting Software", "Secure, multi‑language, live results – like our Haiti system."),
        ("📊 Business Dashboards", "Real‑time analytics and reporting tools."),
        ("🌐 Website & Web Apps", "Full‑stack solutions deployed online."),
        ("📦 24‑Hour Delivery", "We work fast – get your software by email, ready to use."),
        ("📢 Advertising & Marketing", "Digital campaigns, social media management, AI‑driven targeting, performance reports. From $150 to $1,200 depending on scope.")
    ],
    "projects_title": "🏆 Our Projects & Accomplishments",
    "projects_sub": "Completed software solutions delivered to clients – ready for you to purchase or customize.",
    # ----- Projects (English) -----
    "project_haiti": "🇭🇹 Haiti Online Voting Software",
    "project_haiti_desc": "Complete presidential election system with multi‑language support (Kreyòl, French, English, Spanish), real‑time live monitoring, CEP President dashboard (manage candidates, upload photos, download progress reports), secret ballot, and changeable passwords. Used for national elections.",
    "project_haiti_full_price": "$15,000 USD (full package – one‑time)",
    "project_haiti_status": "✅ Available now – includes source code, setup, and support.",
    "project_dashboard": "📊 Business Intelligence Dashboard",
    "project_dashboard_desc": "Real‑time analytics dashboard for companies. Connect to any database (SQL, Excel, CSV) and visualize KPIs, sales trends, inventory, and custom reports. Fully interactive and customizable.",
    "project_dashboard_full_price": "$8,500 USD (full package – one‑time)",
    "project_dashboard_status": "✅ Available now",
    "project_chatbot": "🤖 AI Customer Support Chatbot",
    "project_chatbot_desc": "Intelligent chatbot trained on your business data. Answer customer questions 24/7, reduce support workload. Integrates with websites, WhatsApp, or Telegram. Built with Python and modern NLP.",
    "project_chatbot_full_price": "$6,500 USD (full package – one‑time)",
    "project_chatbot_status": "✅ Available now",
    "project_school": "🏫 School Management System",
    "project_school_desc": "Complete platform for schools: student registration, grade management, attendance tracking, parent portal, report card generation, and fee collection. Multi‑user roles (admin, teachers, parents).",
    "project_school_full_price": "$9,000 USD (full package – one‑time)",
    "project_school_status": "✅ Available now",
    "project_pos": "📦 Inventory & POS System",
    "project_pos_desc": "Web‑based inventory management with point‑of‑sale for small businesses. Barcode scanning, stock alerts, sales reports, supplier management. Works online and offline.",
    "project_pos_full_price": "$7,500 USD (full package – one‑time)",
    "project_pos_status": "✅ Available now",
    "project_scraper": "📈 Custom Web Scraper & Data Pipeline",
    "project_scraper_desc": "Automated data extraction from any website, cleaned and delivered as Excel/JSON/CSV. Schedule daily, weekly, or monthly runs. Perfect for market research, price monitoring, or lead generation.",
    "project_scraper_full_price": "$5,000 USD (full package – one‑time)",
    "project_scraper_status": "✅ Available now",
    "project_chess": "♟️ Play Chess Against the Machine",
    "project_chess_desc": "Educational chess game with AI opponent (3 difficulty levels). Every move is explained – learn tactics like forks, pins, and discovered checks. Includes demo mode, move dashboard, and full game report download. Multi‑language (English, French, Spanish, Kreyòl).",
    "project_chess_full_price": "$499 USD (full package – one‑time)",
    "project_chess_status": "✅ Available now – lifetime access, free updates",
    "project_accountant": "🧮 Accountant Excel Advanced AI",
    "project_accountant_desc": "Professional accounting and loan management suite. Track cash income/expenses, manage loans (borrowers, due dates, payments), dashboard with balance, export all reports to Excel and PDF. Multi‑language (English, French, Spanish).",
    "project_accountant_full_price": "$1,200 USD (full package – one‑time)",
    "project_accountant_status": "✅ Available now – lifetime access, free updates",
    "project_archives": "📜 Haiti Archives Nationales Database",
    "project_archives_desc": "Complete national archives database for Haitian citizens. Store NIF (Matricule Fiscale), CIN, Passport, Driver's License, voting history, sponsorships, and document uploads. Minister signature validation, annual password system, multilingual (English, French, Spanish, Kreyòl).",
    "project_archives_full_price": "$12,000 USD (full package – one‑time)",
    "project_archives_status": "✅ Available now – includes source code, setup, and support",
    "project_dsm": "🛡️ DSM-2026: SYSTEM SECURED",
    "project_dsm_desc": "Advanced stratosphere monitoring radar – tracks aircraft, satellites, and missiles in real time. Simulated radar display with threat detection, multi‑language support, and downloadable intelligence reports.",
    "project_dsm_full_price": "$2,500 USD (full package – one‑time)",
    "project_dsm_status": "✅ Available now – lifetime license, free updates",
    "project_bi": "📊 Business Intelligence Dashboard",
    "project_bi_desc": "Real‑time analytics dashboard for companies. Connect SQL, Excel, CSV – visualize KPIs, sales trends, inventory, and regional performance. Fully interactive with date filters and downloadable CSV reports. Multi‑language (English, French, Spanish, Kreyòl).",
    "project_bi_full_price": "$8,500 USD (full package – one‑time)",
    "project_bi_status": "✅ Available now – lifetime access, free updates",
    "project_ai_classifier": "🧠 AI Image Classifier (MobileNetV2)",
    "project_ai_classifier_desc": "Upload an image and the AI identifies it from 1000 categories (animals, vehicles, food, everyday objects). Uses TensorFlow MobileNetV2 pre‑trained on ImageNet. Multi‑language, password protected, demo ready.",
    "project_ai_classifier_full_price": "$4,500 USD (full package – one‑time)",
    "project_ai_classifier_status": "✅ Available now – includes source code, setup, and support",
    "project_task_manager": "🗂️ Task Manager Dashboard",
    "project_task_manager_desc": "Manage tasks, track progress, and analyze productivity with real‑time charts and dark mode. Inspired by React’s component‑based UI. Multi‑language, persistent storage, analytics dashboard.",
    "project_task_manager_full_price": "$3,500 USD (full package – one‑time)",
    "project_task_manager_status": "✅ Available now – lifetime access, free updates",
    "project_ray": "⚡ Ray Parallel Text Processor",
    "project_ray_desc": "Process text in parallel across multiple CPU cores. Compare sequential vs. parallel execution speed. Inspired by UC Berkeley’s distributed computing framework Ray.",
    "project_ray_full_price": "$3,500 USD (full package – one‑time)",
    "project_ray_status": "✅ Available now – lifetime access, free updates",
    "project_cassandra": "🗄️ Cassandra Data Dashboard",
    "project_cassandra_desc": "Distributed NoSQL database demo. Add orders, search by customer, and explore real‑time analytics. Modeled after Apache Cassandra (Netflix, Instagram).",
    "project_cassandra_full_price": "$4,000 USD (full package – one‑time)",
    "project_cassandra_status": "✅ Available now – lifetime access, free updates",
    "project_spark": "🌊 Apache Spark Data Processor",
    "project_spark_desc": "Upload a CSV file and run SQL‑like aggregations (group by, sum, avg, count) using Spark. Real‑time results and charts. Inspired by the big‑data engine used by thousands of companies.",
    "project_spark_full_price": "$5,500 USD (full package – one‑time)",
    "project_spark_status": "✅ Available now – lifetime access, free updates",
    "project_drone": "🚁 Haitian Drone Commander",
    "project_drone_desc": "Control the first Haitian‑made drone from your phone. Simulation mode, real drone support (MAVLink), arm, takeoff, land, fly to GPS coordinates, live telemetry, command history. Multi‑language, professional dashboard.",
    "project_drone_full_price": "$12,000 USD (full package – one‑time)",
    "project_drone_status": "✅ Available now – includes source code, setup, and 1 year support",
    "project_english": "🇬🇧 Let's Learn English with Gesner",
    "project_english_desc": "Interactive English language learning app. Covers vocabulary, grammar, pronunciation, and conversation practice. Multi‑language interface, progress tracking, quizzes, and certificates. Perfect for beginners to intermediate learners.",
    "project_english_full_price": "$1,500 USD (full package – one‑time)",
    "project_english_status": "✅ Available now – includes source code, setup, and support",
    "project_spanish": "🇪🇸 Let's Learn Spanish with Gesner",
    "project_spanish_desc": "Complete Spanish language learning platform. Lessons on vocabulary, verb conjugations, listening comprehension, and cultural notes. Includes interactive exercises, speech recognition, and progress dashboard.",
    "project_spanish_full_price": "$1,500 USD (full package – one‑time)",
    "project_spanish_status": "✅ Available now – includes source code, setup, and support",
    "project_portuguese": "🇵🇹 Let's Learn Portuguese with Gesner",
    "project_portuguese_desc": "Brazilian and European Portuguese learning app. Covers essential phrases, grammar, verb tenses, and real‑life dialogues. Includes flashcards, pronunciation guide, and achievement badges. Multi‑language support.",
    "project_portuguese_full_price": "$1,500 USD (full package – one‑time)",
    "project_portuguese_status": "✅ Available now – includes source code, setup, and support",
    "project_ai_career": "🚀 AI Career Coach – Resume Optimizer",
    "project_ai_career_desc": "**Optimize your resume and ace interviews with AI.** Upload your CV and a job description – our AI analyzes both and provides: Keywords to add, Skill improvements, Formatting suggestions, Predicted interview questions. Perfect for job seekers, students, and professionals. Full source code included.",
    "project_ai_career_full_price": "$1,200 USD (full package – one‑time)",
    "project_ai_career_status": "✅ Available now – full source code included",
    "project_ai_medical": "🧪 AI Medical & Scientific Literature Assistant",
    "project_ai_medical_desc": "**Ask any medical or scientific question – get answers backed by real research.** Our AI searches PubMed, retrieves relevant abstracts, and generates evidence‑based answers with citations and direct links. Full source code included.",
    "project_ai_medical_full_price": "$1,200 USD (full package – one‑time)",
    "project_ai_medical_status": "✅ Available now – full source code included",
    "project_music_studio": "🎧 Music Studio Pro – Complete Music Production Suite",
    "project_music_studio_desc": "**Professional music production software** – record, mix, and create beats. Includes voice recording, studio effects, multi‑track beat maker, continuous loops, sing over tracks, auto‑tune recorder. Full source code included.",
    "project_music_studio_full_price": "$2,500 USD (full package – one‑time)",
    "project_music_studio_status": "✅ Available now – full source code included",
    "project_ai_media": "🎭 AI Media Studio – Talking Photo & Video Editor",
    "project_ai_media_desc": "**Create professional videos from photos, audio, or video clips.** Four modes: Photo + Speech, Photo + Uploaded Audio, Photo + Background Music, Video + Background Music. Full source code included.",
    "project_ai_media_full_price": "$1,200 USD (full package – one‑time)",
    "project_ai_media_status": "✅ Available now – full source code included",
    "project_chinese": "🇨🇳 Let's Learn Chinese with Gesner – Book 1",
    "project_chinese_desc": "**Complete beginner course for Mandarin Chinese.** 20 interactive lessons covering daily conversations, vocabulary, grammar, pronunciation, and quizzes. Full source code included.",
    "project_chinese_full_price": "$1,500 USD (full package – one‑time)",
    "project_chinese_status": "✅ Available now – full source code included",
    "project_french": "🇫🇷 Let's Learn French with Gesner – Book 1",
    "project_french_desc": "**Complete beginner course for French language.** 20 interactive lessons covering daily conversations, vocabulary, grammar, pronunciation, and quizzes. Full source code included.",
    "project_french_full_price": "$1,500 USD (full package – one‑time)",
    "project_french_status": "✅ Available now – full source code included",
    "project_mathematics": "📐 Let's Learn Mathematics with Gesner – Book 1",
    "project_mathematics_desc": "**Complete mathematics course for beginners.** 20 lessons covering basic arithmetic, geometry, fractions, decimals, percentages, word problems, and more. Full source code included.",
    "project_mathematics_full_price": "$1,500 USD (full package – one‑time)",
    "project_mathematics_status": "✅ Available now – full source code included",
    "project_ai_course": "🤖 AI Foundations & Certification Course",
    "project_ai_course_desc": "**28‑day AI mastery course – from beginner to certified expert.** Learn ChatGPT, Gemini, MidJourney, Runway, ElevenLabs, Make.com, and more. Full source code included.",
    "project_ai_course_full_price": "$2,500 USD (full package – one‑time)",
    "project_ai_course_status": "✅ Available now – full source code included",
    "project_medical_term": "🩺 Medical Terminology Book for Translators",
    "project_medical_term_desc": "**Interactive medical terminology training for interpreters and healthcare professionals.** 20 lessons covering real doctor‑patient conversations, native voice audio, and translation practice. Full source code included.",
    "project_medical_term_full_price": "$1,500 USD (full package – one‑time)",
    "project_medical_term_status": "✅ Available now – full source code included",
    "project_python_course": "🐍 Let's Learn Coding through Python with Gesner",
    "project_python_course_desc": "**Complete Python programming course – from beginner to advanced.** 20 interactive lessons with demo code, 5 practice exercises per lesson, and audio support. Full source code included.",
    "project_python_course_full_price": "$2,500 USD (full package – one‑time)",
    "project_python_course_status": "✅ Available now – full source code included",
    "project_hardware_course": "🔌 Let's Learn Software & Hardware with Gesner",
    "project_hardware_course_desc": "**Connect software with 20 hardware components – build IoT and robotics projects.** 20 lessons covering network cards, Wi‑Fi, Bluetooth, GPS, GPIO, sensors, motors, displays, and more. Full source code included.",
    "project_hardware_course_full_price": "$2,500 USD (full package – one‑time)",
    "project_hardware_course_status": "✅ Available now – full source code included",
    "project_medical_vocab_book2": "📘 Let's Learn Medical Vocabulary with Gesner – Book 2",
    "project_medical_vocab_book2_desc": "**20 lessons – 50 medical terms, 50 acronyms, 50 abbreviations per lesson.** Full audio support for every word. Perfect for medical interpreters, students, and healthcare professionals. Build your medical vocabulary step by step.",
    "project_medical_vocab_book2_full_price": "$1,500 USD (full package – one‑time)",
    "project_medical_vocab_book2_status": "✅ Available now – full source code included",
    "project_medical_term_book3": "📘 Let's Learn Medical Terminology with Gesner – Book 3 (English‑French)",
    "project_medical_term_book3_desc": "**Bilingual English‑French medical terminology course.** 20 lessons with 50 terms, 50 acronyms, 50 abbreviations per lesson – each with native audio in both languages. Perfect for French‑speaking interpreters and healthcare professionals.",
    "project_medical_term_book3_full_price": "$1,500 USD (full package – one‑time)",
    "project_medical_term_book3_status": "✅ Available now – full source code included",
    "project_toefl_course": "📘 Let's Learn TOEFL with Gesner",
    "project_toefl_course_desc": "**Complete TOEFL preparation course.** 20 lessons with 3 interactive conversations, 50 vocabulary words, 25 idioms, 25 grammar rules, and 1 essay per lesson. Full audio support. Perfect for international students and test takers.",
    "project_toefl_course_full_price": "$1,500 USD (full package – one‑time)",
    "project_toefl_course_status": "✅ Available now – full source code included",
    "project_french_course": "🇫🇷 Let's Learn French with Gesner",
    "project_french_course_desc": "**Complete French language learning course.** 20 lessons with 3 interactive conversations, 50 vocabulary words, 25 idioms, 25 grammar rules, and 1 essay per lesson. Native French audio. Perfect for beginners and intermediate learners.",
    "project_french_course_full_price": "$1,500 USD (full package – one‑time)",
    "project_french_course_status": "✅ Available now – full source code included",
    "project_haiti_marketplace": "🇭🇹 Let's Learn Why Haiti Isn't a Marketplace for Most Social Media",
    "project_haiti_marketplace_desc": "**20 lessons explaining Haiti's digital divide and how to fix it.** Covers algorithms, PayPal absence, diaspora advantage, and actionable solutions. Available in 5 languages (English, Spanish, French, Portuguese, Chinese) with native audio.",
    "project_haiti_marketplace_full_price": "$1,500 USD (full package – one‑time)",
    "project_haiti_marketplace_status": "✅ Available now – full source code included",
    "project_vectra_ai": "🚗 Vectra AI – Self‑Driving Car Simulator",
    "project_vectra_ai_desc": "**Interactive self‑driving car simulation.** Drive on a winding dust road, avoid oncoming cars, adjust speed limit. Uses 5 sensors and AI to stay in the right lane. Full source code included.\n\n**Fair Market Valuation (B2B Licensing):** $4,500 – $12,000 USD ↑ Per Implementation – Based on real‑time physics engine, AI lane‑discipline logic, and custom heading algorithms.",
    "project_vectra_ai_full_price": "$25,000 USD (full package – one‑time)",
    "project_vectra_ai_status": "✅ Available now – full source code included",
    "project_humanoid_robot": "🤖 Humanoid Robot Training & Control Software – Built by Gesner Deslandes",
    "project_humanoid_robot_desc": "Complete software suite to train any humanoid robot to perform real‑world tasks. Includes task programming interface, simulation mode, real‑time telemetry, and API for physical robot integration (ROS2, MAVLink, or custom). Train the robot by demonstration or scripted commands. Full source code, setup guide, and 1 year support included.",
    "project_humanoid_robot_full_price": "$45,000 USD (full package – one‑time)",
    "project_humanoid_robot_status": "✅ Available now – full source code included, lifetime updates, 1 year support",
    "project_hospital": "🏥 Hospital Management System Software – built by Gesner Deslandes",
    "project_hospital_desc": "Complete multi‑specialty hospital management platform. Includes EMR/EHR, OPD/IPD workflows, billing & revenue cycle management, pharmacy, laboratory, radiology integration, inventory & financial management, role‑based dashboards, and enterprise reporting. HL7 & FHIR ready. Cloud or on‑premise. Trusted for mid‑size to national tertiary centers.",
    "project_hospital_full_price": "$35,000 USD (full package – one‑time)",
    "project_hospital_status": "✅ Live demo available | Subscribe monthly",
    "project_arbitration": "⚖️ Develop your arbitration skills With Gesner",
    "project_arbitration_desc": "Executive course – 20 lessons, guest practitioners, interactive learning, audio support, and illustrative images. Covers international arbitration from agreements to enforcement, ethics, and future trends.",
    "project_arbitration_full_price": "$1,200 USD (full package – one‑time)",
    "project_arbitration_status": "✅ Live demo available | Subscribe monthly",
    "project_programming_book": "📘 Let's Learn Basic Syntaxes & Symbols with Gesner",
    "project_programming_book_desc": "Your first step into coding – 20 lessons, 3 examples, 3 exercises per lesson, audio support, and a summary in each chapter. Perfect for beginners.",
    "project_programming_book_full_price": "$499 USD (full package – one‑time)",
    "project_programming_book_status": "✅ Live demo available | Subscribe monthly",
    "project_employee_mgmt": "👥 Employee Management Software – built by Gesner Deslandes",
    "project_employee_mgmt_desc": "Complete workforce management platform with AI scheduling, time tracking, geofencing, payroll integration, team chat, and advanced reports. Perfect for remote, deskless, and multi‑location teams.",
    "project_employee_mgmt_full_price": "$12,500 USD (full package – one‑time)",
    "project_employee_mgmt_status": "✅ Live demo available | Subscribe monthly",
    "project_miroir": "🇭🇹 Miroir Revelation Entreprise de Grand Goave",
    "project_miroir_desc": "Business management app for sales, haircut cards (250 HTG), Moncash & Natcash transactions, and daily CSV reports. Perfect for small business owners.",
    "project_miroir_full_price": "$1,500 USD (full package – one‑time)",
    "project_miroir_status": "✅ Live demo available | Subscribe monthly",
    "project_wordpress": "📝 WordPress Development Suite – built by Gesner Deslandes",
    "project_wordpress_desc": "A fully interactive portfolio tool that proves custom theme/plugin development, performance optimization, SEO best practices, responsive design, project management, and troubleshooting.",
    "project_wordpress_full_price": "$2,500 USD (full package – one‑time)",
    "project_wordpress_status": "✅ Live demo (any username/password) | Subscribe monthly",
    "project_building_systems": "🏢 Building Systems Architect Dashboard – built by Gesner Deslandes",
    "project_building_systems_desc": "A professional MEP & BMS control suite demonstrating real‑time BMS monitoring, thermal networks (CHW/LTHW), electrical infrastructure, BIM‑ready asset register, decarbonisation tracking, and commissioning reports.",
    "project_building_systems_full_price": "$4,500 USD (full package – one‑time)",
    "project_building_systems_status": "✅ Live demo (any username/password) | Subscribe monthly",
    # NEW: Thermal Networks Optimisation Suite
    "project_thermal_networks": "🔥 Thermal Networks Optimisation Suite – built by Gesner Deslandes",
    "project_thermal_networks_desc": "Optimise chilled water (CHW) and low‑temperature hot water (LTHW) systems for decarbonisation and heat‑network readiness. Includes real‑time monitoring, COP analysis, decarbonisation pathway modelling, heat‑network readiness assessment, and BS EN 15232 compliance reports.",
    "project_thermal_networks_full_price": "$6,500 USD (full package – one‑time)",
    "project_thermal_networks_status": "✅ Live demo (any username/password) | Subscribe monthly",
    # UI common keys
    "view_demo": "🎬 View Demo",
    "live_demo": "🔗 Live Demo",
    "demo_password_hint": "🔐 Demo password: 20082010 (or any username/password on new demos)",
    "request_info": "Request Info",
    "buy_now": "💵 Buy Full Package",
    "subscribe_monthly": "📅 Subscribe Monthly ($299/mo)",
    "contact_note": "📞 To purchase or subscribe, contact us directly: Phone (509)-47385663 | Email deslandes78@gmail.com",
    "donation_title": "💖 Support GlobalInternet.py",
    "donation_text": "Help us grow and continue building innovative software for Haiti and the world.",
    "donation_sub": "Your donation supports hosting, development tools, and free resources for local developers.",
    "donation_method": "🇭🇹 Easy & fast – Prisme transfer to Moncash (Digicel)",
    "donation_phone": "📱 (509)-47385663",
    "donation_limit": "Amount limit: Up to 100,000 HTG per transaction",
    "donation_instruction": "Just use the 'Prisme transfer' feature in your Moncash app to send your contribution to Gesner Deslandes.",
    "donation_sendwave_title": "🌍 International transfer via <span class='blue-text'>SendWave</span>",
    "donation_sendwave_instruction": "Send money directly to our phone number using the SendWave app (available worldwide).",
    "donation_sendwave_phone": "Recipient phone: (509) 4738-5663 (Gesner Deslandes)",
    "donation_bank_title": "🏦 Bank Transfer (UNIBANK US Account)",
    "donation_bank_account": "Account number: 105-2016-16594727",
    "donation_bank_note": "For international transfers, please use SWIFT code UNIBANKUS (or contact us for details).",
    "donation_future": "🔜 Coming soon: Bank‑to‑bank transfers in USD and HTG (international and local).",
    "donation_button": "💸 I've sent my donation – notify me",
    "donation_thanks": "Thank you so much! We will confirm receipt within 24 hours. Your donation via Prisme Transfer, Sendwave, or Moncash (Digicel) goes directly to Gesner Deslandes at (509)-47385663. Your support means the world to us! 🇭🇹",
    "contact_title": "📞 Let’s Build Something Great",
    "contact_ready": "Ready to start your project?",
    "contact_phone": "📞 Phone / WhatsApp: (509)-47385663",
    "contact_email": "✉️ Email: deslandes78@gmail.com",
    "contact_delivery": "We deliver full software packages by email – fast, reliable, and tailored to you.",
    "contact_tagline": "GlobalInternet.py – Your Python partner, from Haiti to the world.",
    "footer_rights": "All rights reserved.",
    "footer_founded": "Founded by Gesner Deslandes | Built with Streamlit | Hosted on GitHub + Streamlit Cloud",
    "footer_pride": "🇭🇹 Proudly Haitian – serving the world with Python and AI 🇭🇹",
    "sendwave_title": "📱 Send Money to Haiti Like a Text – Fast, Fair, and Finally Affordable",
    "sendwave_intro": "For Haitians living abroad, sending money home should be a joy, not a financial burden. That's why we're proud to recommend **Sendwave**, the international transfer service trusted by millions.",
    "sendwave_reasons": "✓ Instant Delivery – Your money arrives in minutes, not days.\n✓ Low to No Fees – Stop losing your hard-earned cash to hidden costs.\n✓ User-Friendly – So simple, it's like sending a text message.\n✓ Secure & Reliable – Real-time tracking and safe processing.",
    "sendwave_cta": "Your siblings and parents will thank you for helping them quickly. Don't wait. Make the switch today.",
    "sendwave_link": "🔗 **For more info and exclusive updates, visit our website:**\nhttps://globalinternetsitepy-abh7v6tnmskxxnuplrdcgk.streamlit.app/",
    "sendwave_watch_ad": "📺 Watch our ad – Sendwave",
    "western_union_title": "✨✨✨ WESTERN UNION – HAITI ✨✨✨",
    "western_union_text": "💸 Send money fast – anywhere to Haiti\n🔒 Safe, secure, trusted worldwide\n🤝 Cash pickup or direct deposit\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n🌍 At GlobalInternet.py, we promote money transfers to Haiti.\n\n📞 Contact us for your business promotion:\n✉️ Email: deslandes78@gmail.com\n📱 Phone / WhatsApp: (509)-47385663\n🌐 Website: https://globalinternetsitepy-abh7v6tnmskxxnuplrdcgk.streamlit.app\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n🌟 Let’s grow your business together! 🌟",
    "western_union_watch_ad": "📺 Watch our ad – Western Union"
}

# French dictionary (full, including the new thermal_networks entries)
lang_fr = {
    "hero_title": "GlobalInternet.py",
    "hero_sub": "Construisez avec Python. Livrez rapidement. Innovez avec l'IA.",
    "hero_desc": "D'Haïti au monde – des logiciels sur mesure qui fonctionnent en ligne.",
    "about_title": "👨‍💻 À propos de l'entreprise",
    "about_text": "**GlobalInternet.py** a été fondé par **Gesner Deslandes** – propriétaire, fondateur et ingénieur principal. Nous construisons des **logiciels basés sur Python** à la demande pour des clients du monde entier. Comme la Silicon Valley, mais avec une touche haïtienne et des résultats exceptionnels.\n\n- 🧠 **Solutions alimentées par l'IA** – chatbots, analyse de données, automatisation\n- 🗳️ **Systèmes électoraux complets** – sécurisés, multilingues, en temps réel\n- 🌐 **Applications web** – tableaux de bord, outils internes, plateformes en ligne\n- 📦 **Livraison complète** – nous vous envoyons le code complet par email et vous guidons lors de l'installation\n\nQue vous ayez besoin d'un site web d'entreprise, d'un outil logiciel personnalisé ou d'une plateforme en ligne à grande échelle – nous le construisons, vous le possédez.",
    "office_photo_caption": "Avatar parlant de Gesner Deslandes – présentation de GlobalInternet.py",
    "humanoid_photo_caption": "Gesner Humanoid AI – notre représentant numérique de l'innovation et de l'expertise logicielle.",
    "founder": "Fondateur et PDG",
    "founder_name": "Gesner Deslandes",
    "founder_title": "Ingénieur | Passionné d'IA | Expert Python",
    "cv_title": "📄 À propos du propriétaire – Gesner Deslandes",
    "cv_intro": "Constructeur de logiciels Python | Développeur web | Coordinateur technologique",
    "cv_summary": "Leader et gestionnaire exceptionnellement motivé, engagé envers l'excellence et la précision. **Compétences clés :** Leadership, Interprétation (anglais, français, créole haïtien), Orientation mécanique, Gestion, Microsoft Office.",
    "cv_experience_title": "💼 Expérience professionnelle",
    "cv_experience": "**Coordinateur technologique** – Orphelinat Be Like Brit (2021–présent)\nConfiguration des réunions Zoom, maintenance des ordinateurs portables/tablettes, support technique quotidien, assurance d'opérations numériques fluides.\n\n**PDG et services d'interprétation** – Tourisme personnalisé pour groupes d'ONG, équipes de mission et particuliers.\n\n**Gestionnaire de parc / répartiteur** – J/P Haitian Relief Organization\nGestion de plus de 20 véhicules, journaux de bord, calendriers de maintenance avec Excel.\n\n**Interprète médical** – International Child Care\nInterprétation médicale précise anglais–français–créole.\n\n**Chef d'équipe et interprète** – Can‑Do NGO\nDirection de projets de reconstruction.\n\n**Professeur d'anglais** – Be Like Brit (préscolaire à NS4)\n\n**Traducteur de documents** – United Kingdom Glossary & United States Work‑Rise Company",
    "cv_education_title": "🎓 Éducation et formation",
    "cv_education": "- École de formation professionnelle – Anglais américain\n- Institut Diesel d'Haïti – Mécanicien diesel\n- Certification en bureautique (octobre 2000)\n- Diplômé du secondaire",
    "cv_references": "📞 Références disponibles sur demande.",
    "team_title": "👥 Notre équipe",
    "team_sub": "Rencontrez les talents derrière GlobalInternet.py – embauchés en avril 2026.",
    "team_members": [
        {"name": "Gesner Deslandes", "role": "Fondateur et PDG", "since": "2021", "img": "https://raw.githubusercontent.com/Deslandes1/globalinternet_site.py/main/Gesner%20Deslandes.JPG"},
        {"name": "Gesner Junior Deslandes", "role": "Assistant du PDG", "since": "Avril 2026", "img": "https://raw.githubusercontent.com/Deslandes1/globalinternet_site.py/main/dreamina-2026-04-18-6690-Change%20the%20man's%20attire%20to%20a%20professiona....jpeg"},
        {"name": "Roosevelt Deslandes", "role": "Programmeur Python", "since": "Avril 2026", "img": "https://raw.githubusercontent.com/Deslandes1/globalinternet_site.py/main/Roosevelt%20%20Software%20Builder.jpeg"},
        {"name": "Sebastien Stephane Deslandes", "role": "Programmeur Python", "since": "Avril 2026", "img": "https://raw.githubusercontent.com/Deslandes1/globalinternet_site.py/main/35372.jpg"},
        {"name": "Zendaya Christelle Deslandes", "role": "Secrétaire", "since": "Avril 2026", "img": "https://raw.githubusercontent.com/Deslandes1/globalinternet_site.py/main/IMG_1411.jpg"}
    ],
    "services_title": "⚙️ Nos services",
    "services": [
        ("🐍 Développement Python personnalisé", "Scripts sur mesure, automatisation, systèmes backend."),
        ("🤖 IA et apprentissage automatique", "Chatbots, modèles prédictifs, analyses de données."),
        ("🗳️ Logiciel électoral", "Sécurisé, multilingue, résultats en direct – comme notre système Haïti."),
        ("📊 Tableaux de bord d'entreprise", "Analytique en temps réel et outils de reporting."),
        ("🌐 Sites web et applications web", "Solutions full‑stack déployées en ligne."),
        ("📦 Livraison en 24 heures", "Nous travaillons rapidement – recevez votre logiciel par email, prêt à l'emploi."),
        ("📢 Publicité et marketing", "Campagnes numériques, gestion des réseaux sociaux, ciblage IA, rapports de performance. De 150 $ à 1 200 $ selon la portée.")
    ],
    "projects_title": "🏆 Nos projets et réalisations",
    "projects_sub": "Solutions logicielles complètes livrées aux clients – prêtes à être achetées ou personnalisées.",
    # French project entries (existing ones – only showing new thermal_networks)
    "project_thermal_networks": "🔥 Suite d'optimisation des réseaux thermiques – construite par Gesner Deslandes",
    "project_thermal_networks_desc": "Optimisez les systèmes d'eau glacée (CHW) et d'eau chaude basse température (LTHW) pour la décarbonation et la préparation aux réseaux de chaleur. Comprend la surveillance en temps réel, l'analyse du COP, la modélisation des voies de décarbonation, l'évaluation de la préparation aux réseaux de chaleur et les rapports de conformité BS EN 15232.",
    "project_thermal_networks_full_price": "6 500 $ USD (forfait complet – paiement unique)",
    "project_thermal_networks_status": "✅ Démo en direct (n'importe quel nom d'utilisateur/mot de passe) | Abonnement mensuel",
    # ... (all other French keys are identical to your original file; for brevity I omit them here but you must keep them)
    # UI common keys in French (same as before, with updated demo hint)
    "demo_password_hint": "🔐 Mot de passe démo : 20082010 (ou n'importe quel identifiant/mot de passe sur les nouvelles démos)",
    # ... (keep rest of your French dictionary)
}

# Spanish dictionary (excerpt – add thermal_networks)
lang_es = {
    # ... (all existing Spanish translations)
    "project_thermal_networks": "🔥 Suite de optimización de redes térmicas – construida por Gesner Deslandes",
    "project_thermal_networks_desc": "Optimice los sistemas de agua fría (CHW) y agua caliente de baja temperatura (LTHW) para la descarbonización y la preparación para redes de calor. Incluye monitoreo en tiempo real, análisis de COP, modelado de vías de descarbonización, evaluación de preparación para redes de calor e informes de cumplimiento BS EN 15232.",
    "project_thermal_networks_full_price": "$6,500 USD (paquete completo – pago único)",
    "project_thermal_networks_status": "✅ Demo en vivo (cualquier nombre de usuario/contraseña) | Suscripción mensual",
    "demo_password_hint": "🔐 Contraseña de demostración: 20082010 (o cualquier nombre de usuario/contraseña en las nuevas demos)",
    # ... (keep rest of your Spanish dictionary)
}

# Combine dictionaries
lang_dict = {"en": lang_en, "fr": lang_fr, "es": lang_es}

# Language selector and sidebar (unchanged from your original)
st.sidebar.image("https://flagcdn.com/w320/ht.png", width=60)
lang = st.sidebar.selectbox(
    "🌐 Language / Langue / Idioma",
    options=["en", "fr", "es"],
    format_func=lambda x: {"en": "English", "fr": "Français", "es": "Español"}[x]
)
t = lang_dict[lang]

# ... (rest of your sidebar, main content, projects loop, donation, contact, footer exactly as in your original app.py)
# The only change is the addition of "thermal_networks" in project_keys and its demo URL assignment.

# Inside the projects loop, add:
# elif key == "thermal_networks":
#     demo_url = "https://your-thermal-networks-app.streamlit.app/"   # replace after deployment

# Ensure project_keys includes "thermal_networks"

# The remainder of the file (main content, hero, about, team, services, projects display, etc.) remains unchanged.
