import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from PIL import Image
from streamlit_mic_recorder import mic_recorder

# إعداد الواجهة
st.set_page_config(page_title="Soufiane Medical AI", layout="wide")
st.title("🩺 المساعد الطبي المتكامل")

# 1. إعداد الـ API Key
api_key = st.sidebar.text_input("أدخل مفتاح Google API:", type="password")

if api_key:
    genai.configure(api_key=api_key)
    # استخدام الموديل المستقر
    model = genai.GenerativeModel('gemini-1.0-pro')

    # 2. رفع الملفات
    uploaded_file = st.file_uploader("ارفع صورة طبية أو ملف PDF:", type=["png", "jpg", "jpeg", "pdf"])
    
    # 3. تسجيل الصوت
    audio = mic_recorder(start_prompt="سجل سؤالك صوتياً", stop_prompt="أوقف التسجيل")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # عرض الرسائل
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # معالجة المدخلات
    prompt = st.chat_input("اطرح سؤالك الطبي هنا...")
    
    if prompt or uploaded_file:
        user_input = prompt if prompt else "حلل لي هذا الملف"
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            try:
                # معالجة الملفات (تذكير: Gemini 1.0 Pro يدعم النصوص بشكل ممتاز)
                content = user_input
                
                if uploaded_file:
                    if uploaded_file.type == 'application/pdf':
                        pdf = PdfReader(uploaded_file)
                        text = "".join([page.extract_text() for page in pdf.pages])
                        content = f"{user_input} \n\n محتوى الملف الطبي: {text}"
                    else:
                        st.warning("الموديل الحالي يركز على النصوص والتقارير المكتوبة. يرجى رفع ملفات PDF.")
                
                response = model.generate_content(content)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
            except Exception as e:
                st.error(f"حدث خطأ: {e}")
else:
    st.info("المرجو إدخال الـ API Key في القائمة الجانبية.")
