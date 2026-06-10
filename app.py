import streamlit as st
import google.generativeai as genai

st.title("🩺 المساعد الطبي (Google Gemini)")

# إدخال API Key
api_key = st.sidebar.text_input("ادخل Google AI Key:", type="password")

if api_key:
    genai.configure(api_key=api_key)
    # استخدام موديل Gemini Pro
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # واجهة المحادثة
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("سولني (Gemini):"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # إرسال السؤال لـ Gemini
            response = model.generate_content(f"أنت مساعد طبي، أجب على: {prompt}")
            ans = response.text
            st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})
