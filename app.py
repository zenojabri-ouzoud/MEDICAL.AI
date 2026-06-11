import streamlit as st
import google.generativeai as genai

# إعداد الواجهة
st.set_page_config(page_title="Soufiane Medical AI", layout="centered")
st.title("🩺 المساعد الطبي الذكي")

# خانة إدخال الـ API Key في القائمة الجانبية
api_key = st.sidebar.text_input("أدخل مفتاح Google API الخاص بك:", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # عرض المحادثة
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # خانة السؤال
        if prompt := st.chat_input("اطرح سؤالك الطبي هنا..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                # الاتصال بـ Google Gemini
                response = model.generate_content(f"بصفتك مساعداً طبياً، أجب على: {prompt}")
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"حدث خطأ: {e}. تأكد من صحة الـ API Key.")
else:
    st.info("المرجو إدخال الـ API Key في القائمة الجانبية لبدء المحادثة.")
