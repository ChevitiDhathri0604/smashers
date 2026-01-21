import streamlit as st
import pandas as pd
import ollama
import requests
from streamlit_lottie import st_lottie

# --- 1. SETTINGS & STYLES ---
st.set_page_config(page_title="SkillBridge AI", layout="wide", page_icon="🎓")

def inject_styles():
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }
        .job-card {
            background: rgba(255, 255, 255, 0.85);
            backdrop-filter: blur(12px);
            padding: 25px;
            border-radius: 20px;
            border: 1px solid rgba(255,255,255,0.3);
            margin-bottom: 20px;
            transition: transform 0.3s ease;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }
        .job-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 20px rgba(0,0,0,0.1);
            border-color: #4A90E2;
        }
        .badge {
            padding: 4px 12px; border-radius: 8px; font-size: 11px;
            font-weight: 600; margin-right: 8px; display: inline-block;
            margin-top: 5px; text-transform: uppercase;
        }
        .tech-badge { background: #E3F2FD; color: #1976D2; border: 1px solid #BBDEFB; }
        .soft-badge { background: #E8F5E9; color: #2E7D32; border: 1px solid #C8E6C9; }
        .mode-badge { background: #F3E5F5; color: #7B1FA2; border: 1px solid #E1BEE7; }
        .match-pct { color: #2E7D32; font-weight: bold; font-size: 1.1em; }
        </style>
    """, unsafe_allow_html=True)

inject_styles()

# --- 2. ASSETS & MOCK DATA ---
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else None
    except: return None

lottie_rocket = load_lottieurl("https://lottie.host/80862002-3f1d-4881-807d-531e21b0255c/J94M8W17J0.json")
lottie_ai = load_lottieurl("https://lottie.host/6ad395f3-5290-449e-87a4-068d37c569f7/YyY2t0zG5D.json")

def get_job_database():
    return [
        {"role": "Backend Intern", "company": "Stripe", "tech": ["Python", "API Design"], "soft": ["Logic", "Problem Solving"], "mode": "Remote", "stipend": "₹45k"},
        {"role": "Frontend Developer", "company": "Notion", "tech": ["React", "Typescript"], "soft": ["Design", "Communication"], "mode": "Hybrid", "stipend": "₹35k"},
        {"role": "Data Analyst", "company": "Zomato", "tech": ["SQL", "Tableau"], "soft": ["Logic", "Writing"], "mode": "In-Office", "stipend": "₹25k"},
        {"role": "Fullstack Intern", "company": "Razorpay", "tech": ["React", "Python"], "soft": ["Communication", "Logic"], "mode": "Hybrid", "stipend": "₹50k"},
        {"role": "ML Research", "company": "OpenAI", "tech": ["Python", "SQL"], "soft": ["Problem Solving", "Logic"], "mode": "Remote", "stipend": "₹80k"}
    ]

# --- 3. SESSION STATE ---
if "messages" not in st.session_state: st.session_state.messages = []
if "profile" not in st.session_state: 
    st.session_state.profile = {
        "name": "Guest", "phone": "", "email": "",
        "tech": [], "soft": [], 
        "work_systems": ["Remote", "Hybrid", "In-Office"]
    }

# --- 4. SIDEBAR NAVIGATION ---
with st.sidebar:
    if lottie_ai: st_lottie(lottie_ai, height=120, key="ai_anim")
    st.title("SkillBridge AI")
    model_choice = st.selectbox("LLM Brain", ["phi3", "mistral", "llama3"])
    st.divider()
    page = st.radio("Navigation", ["🏠 Home", "👤 Profile", "🎯 Matches", "🤖 Career Chatbot"])
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# --- 5. PAGE: HOME ---
if page == "🏠 Home":
    left, mid, right = st.columns([1, 2, 1])
    with mid:
        if lottie_rocket:
            st_lottie(lottie_rocket, height=300, key="rocket_anim")
    
    st.markdown("<h1 style='text-align: center;'>Your Potential, Optimized.</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Bridging the Tier-2/3 college gap with local AI-powered mentorship.</p>", unsafe_allow_html=True)
    
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.info("**Local LLM**\nPrivacy-first career coaching running on your PC.")
    c2.info("**Hybrid Ready**\nFilter opportunities by Remote, Hybrid, or Office.")
    c3.info("**Job Ready**\nWeighted matching based on Tech and Soft skills.")

# --- 6. PAGE: PROFILE ---
elif page == "👤 Profile":
    st.title("Skill Profile & Contact Info")
    with st.form("p_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name", value=st.session_state.profile['name'])
            email = st.text_input("Email", value=st.session_state.profile['email'])
        with col2:
            phone = st.text_input("Phone", value=st.session_state.profile['phone'])
            work_pref = st.multiselect("Work Systems", ["Remote", "Hybrid", "In-Office"], 
                                      default=st.session_state.profile['work_systems'])

        st.divider()
        tech = st.multiselect("Tech Skills", ["Python", "SQL", "React", "Tableau", "API Design", "Typescript", "Java"], 
                             default=st.session_state.profile['tech'])
        soft = st.multiselect("Soft Skills", ["Logic", "Design", "Communication", "Writing", "Problem Solving"],
                             default=st.session_state.profile['soft'])
        
        if st.form_submit_button("Save Profile"):
            st.session_state.profile.update({
                "name": name, "phone": phone, "email": email,
                "tech": tech, "soft": soft, "work_systems": work_pref
            })
            st.success("Profile Updated!")

# --- 7. PAGE: SMART MATCHES ---
elif page == "🎯 Matches":
    st.title("Smart Recommendations")
    p = st.session_state.profile
    if not p['tech']:
        st.warning("Please fill your profile first.")
    else:
        db = get_job_database()
        # Filter by Work System preference
        filtered_jobs = [j for j in db if j['mode'] in p['work_systems']]
        
        for job in filtered_jobs:
            t_match = len(set(p['tech']) & set(job['tech'])) / len(job['tech']) if job['tech'] else 0
            s_match = len(set(p['soft']) & set(job['soft'])) / len(job['soft']) if job['soft'] else 0
            
            # Weighted Score: 70% Tech, 30% Soft
            score_pct = int(((t_match * 0.7) + (s_match * 0.3)) * 100)
            
            if score_pct > 0:
                st.markdown(f"""
                <div class="job-card">
                    <div style="display: flex; justify-content: space-between;">
                        <div>
                            <span class="badge mode-badge">{job['mode']}</span>
                            <h3>{job['role']}</h3>
                            <p style="color:#4A90E2;">{job['company']} | {job['stipend']}</p>
                        </div>
                        <div class="match-pct">{score_pct}% Match</div>
                    </div>
                    {" ".join([f'<span class="badge tech-badge">{t}</span>' for t in job['tech']])}
                    {" ".join([f'<span class="badge soft-badge">{s}</span>' for s in job['soft']])}
                </div>
                """, unsafe_allow_html=True)

# --- 8. PAGE: CAREER CHATBOT ---
elif page == "🤖 Career Chatbot":
    st.title("AI Career Architect")
    st.caption(f"Currently using: {model_choice}")

    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Ask about interviews, skills, or projects..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_res = ""
            sys_prompt = f"You are a career mentor for {st.session_state.profile['name']}. Technical skills: {st.session_state.profile['tech']}. Soft skills: {st.session_state.profile['soft']}."
            
            try:
                for chunk in ollama.chat(model=model_choice, messages=[{'role': 'system', 'content': sys_prompt}] + st.session_state.messages[-5:], stream=True):
                    full_res += chunk['message']['content']
                    placeholder.markdown(full_res + "▌")
                placeholder.markdown(full_res)
                st.session_state.messages.append({"role": "assistant", "content": full_res})
            except:
                st.error("Error: Check if Ollama is running (`ollama serve`).")