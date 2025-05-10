import streamlit as st
import requests

# Page Config
st.set_page_config(
    page_title="Gender Affirmation Surgery Assistant",
    layout="centered"
)

# --- Custom CSS for Dark Theme and Chat Styling ---
st.markdown("""
    <style>
    body {
        background-color: #1e1e1e;
        color: white;
    }

    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin-bottom: 10px;
    }

    .chat-message {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        padding: 10px;
        border-radius: 12px;
        max-width: 80%;
        font-size: 16px;
        line-height: 1.5;
        word-wrap: break-word;
        box-shadow: 1px 1px 5px rgba(0,0,0,0.3);
    }

    .chat-message.user {
        background-color: #2b2b2b;
        color: #e1e1e1;
        align-self: flex-end;
        margin-left: auto;
        flex-direction: row-reverse;
    }

    .chat-message.assistant {
        background-color: #3a3a3a;
        color: #f5f5f5;
        align-self: flex-start;
        margin-right: auto;
    }

    .avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        object-fit: cover;
    }

    .stChatInput input {
        background-color: #2b2b2b !important;
        color: #fff !important;
        border: 1px solid #444 !important;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.title("🏥 TransCare Navigator")

# --- Form Section ---
with st.form("patient_form"):
    age       = st.number_input("Age", min_value=10, max_value=100)
    gender    = st.selectbox("Gender Identity", ["Trans Woman", "Trans Man", "Non-Binary"])
    surgery   = st.selectbox("Surgery Type", ["Phalloplasty", "Top Surgery"])
    hormone   = st.number_input("Hormone Therapy Duration (months)", min_value=0)
    comorb    = st.selectbox("Comorbidities", ["None", "One", "Multiple"])
    family    = st.selectbox("Family Support", ["Yes", "No", "Partial"])
    smoke     = st.selectbox("Smoking", ["Yes", "No"])
    insurance = st.selectbox("Insurance Status", ["Private", "Public", "None"])
    mental    = st.selectbox("Mental Health (Pre-Op)", ["None", "Mild", "Severe"])
    mh_score  = st.slider("Mental Health Score (0.0 = worst, 1.0 = best)", 0.0, 1.0, step=0.01)

    surgeon   = st.slider("Surgeon Experience (years)", 0, 40)
    days      = st.number_input("Days Since Surgery", min_value=0)
    diabetes  = st.selectbox("Diabetes", [0, 1])
    hiv       = st.selectbox("HIV", [0, 1])
    other_mh  = st.selectbox("Other Mental Health Condition", [0, 1])
    submitted = st.form_submit_button("Get Prediction")

if submitted:
    input_data = {
        "Age": age,
        "Gender_Identity": gender,
        "Surgery_Type": surgery,
        "Hormone_Therapy_Duration_Months": hormone,
        "Comorbidities": comorb,
        "Family_Support": family,
        "Smoking": smoke,
        "Insurance_Status": insurance,
        "Mental_Health_PreOp": mental,
        "Mental_Health_Score": mh_score, 
        "Surgeon_Experience_Years": surgeon,
        "Time_Since_Surgery_Days": days,
        "Diabetes": diabetes,
        "HIV": hiv,
        "Other_Mental_Health": other_mh
    }

    with st.spinner("Analyzing..."):
        try:
            resp = requests.post("http://127.0.0.1:8000/predict", json=input_data, timeout=5)
            resp.raise_for_status()
        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. Is the backend running?")
        except requests.exceptions.ConnectionError as ce:
            st.error(f"🔌 Connection error: {ce}")
        except requests.exceptions.HTTPError:
            st.error(f"❌ API error {resp.status_code}: {resp.text}")
        except Exception as e:
            st.error(f"⚠️ Unexpected error: {e}")
        else:
            result = resp.json()
            st.success(f"🩺 PostOp Risk Level: **{result['PostOp Risk Level']}**")
            st.warning(f"⚠️ Complications Likely: **{result['Complications']}**")
            if result['PostOp Risk Level'] == 'High':
                st.info("💡 Tip: Consult a mental health professional for check-ins.")
            else:
                st.info("✅ You’re on a stable recovery path—keep following guidance.")

# --- Chatbot Assistant Section ---
st.divider()
st.subheader("🤖 Mental Health Chat Assistant")

chat_history = st.session_state.setdefault("chat_history", [])
last_question_key = st.session_state.setdefault("last_question_key", None)

# Response mapping
chat_responses = {
    "hi": "Hello! How are you? How can I assist you today?",
    "anxious": "That's completely normal. Recovery can bring many emotions. Would you like calming exercises or a motivational article?",
    "mood": "Mood swings can happen post-op. You're not alone. Would you like to talk to a counselor or read stories from others?",
    "isolated": "I'm here for you. Community support can make a big difference. Would you like links to safe support groups?",
    "mental health": "Try deep breathing, journaling, or music. Want a 5-minute guided meditation or contact to a helpline?",
    "regret": "It’s okay to have mixed feelings. Processing them is part of healing. Would you like to read a blog from someone who’s been through it?",
    "high-risk": "A high-risk prediction suggests closer follow-up is needed. Please consult your doctor for personalized care.",
    "complication": "Following medical advice, checkups, and mental wellness routines can help reduce complications.",
    "low-risk": "That’s great news! Still, keep up regular checkups and mental health support.",
    "swelling": "Some swelling is expected. If it’s severe or painful, contact your care provider immediately.",
    "exercise": "It depends on your recovery stage. Have you checked with your surgeon yet?",
    "eat": "Balanced meals with protein, veggies, and fluids will help. Avoid processed foods and sugary drinks.",
    "alone": "Try asking a trusted friend to check in regularly. Want suggestions for local home-care services?",
    "meds": "Using a pill box or phone reminders can help. Want me to generate a sample medication reminder schedule?",
    "fear": "That fear is real—but your journey is valid. You’re brave, and you’re not alone.",
    "better": "Many report greater comfort and joy post-surgery. Healing takes time, but you’re on a meaningful path.",
    "burden": "You’re not a burden. You matter, and your feelings are valid.",
    "sleep": "Try calming tea, a relaxing routine, and screen time limits. Want a personalized sleep checklist?",
    "support": "I can help you find a therapist or a transgender-friendly support line. Want that info now?",
    "how to use": "Just fill in the form with your health details, and I’ll provide a personalized risk prediction and support plan.",
    "top surgery": "Top surgery reshapes or removes breast tissue. Want me to show you FAQs or real-life stories?",
    "check in": "I recommend weekly check-ins or anytime you feel unsure or overwhelmed. Do you want to schedule reminders?",
    "doing right": "Everyone’s healing journey is unique. You're doing your best—that’s what matters.",
    "life after": "Life post-surgery can be liberating, but healing takes time. Would you like to read inspiring recovery stories?",
    "insurance": "Insurance access varies. I can help find public or sliding-scale options. Want me to look that up for you?"
}

# HTML clickable links for follow-up
follow_up_map = {
    "anxious": "Here’s a calming guide: <a href='https://www.headspace.com/' target='_blank'>Mindful Recovery Techniques</a>.",
    "mood": "Check out this real-life story: <a href='https://transcare.ucsf.edu/transition-guide/emotional' target='_blank'>Healing After Surgery</a>.",
    "regret": "This blog might help you feel less alone: <a href='https://www.hrc.org/resources/transgender-visibility-guide' target='_blank'>Transgender Voices</a>.",
    "support": "You can reach out to Trans Lifeline at <strong>877-565-8860</strong> (US). Would you like me to help find local therapists?",
    "mental health": "Here’s a helpline: <strong>LGBT National Help Center: 888-843-4564</strong>. Would you like guided meditation audio?",
    "life after": "Here's a story that might uplift you: <a href='https://www.glaad.org/transgender/resources' target='_blank'>Life After Transition</a>.",
    "top surgery": "Here's a FAQ resource: <a href='https://www.plasticsurgery.org/reconstructive-procedures/transgender-top-surgery' target='_blank'>Top Surgery Explained</a>."
}

# Function to show chat messages
def show_chat(role, message):
    css_class = "user" if role == "user" else "assistant"
    avatar_url = "https://cdn-icons-png.flaticon.com/512/4086/4086679.png" if role == "assistant" else "https://cdn-icons-png.flaticon.com/512/149/149071.png"
    st.markdown(f"""
        <div class="chat-container">
            <div class="chat-message {css_class}">
                <img src="{avatar_url}" class="avatar"/>
                <div>{message}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- Chat Input Logic ---
user_prompt = st.chat_input("Ask me anything about your recovery, risk, or mental health...")

if user_prompt:
    show_chat("user", user_prompt)
    chat_history.append(("user", user_prompt))

    sent = False

    if user_prompt.strip().lower() == "yes" and last_question_key:
        follow_up = follow_up_map.get(last_question_key)
        if follow_up:
            show_chat("assistant", follow_up)
            chat_history.append(("assistant", follow_up))
            st.session_state["last_question_key"] = None
            sent = True

    if not sent:
        for key, reply in chat_responses.items():
            if key in user_prompt.lower():
                show_chat("assistant", reply)
                chat_history.append(("assistant", reply))
                st.session_state["last_question_key"] = key if key in follow_up_map else None
                sent = True
                break

    if not sent:
        fallback = "I can't provide detailed info on that, but I can help with these topics. Please choose one:"
        show_chat("assistant", fallback)
        chat_history.append(("assistant", fallback))

        available_topics = list(follow_up_map.keys())
        topic_message = "Here are some topics I can help with:<br>" + "<br>".join(
            [f"<strong>{topic}</strong>" for topic in available_topics]
        )
        show_chat("assistant", topic_message)
        chat_history.append(("assistant", topic_message))

        st.session_state["last_question_key"] = None
