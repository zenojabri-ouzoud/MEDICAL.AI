import streamlit as st
import google.generativeai as genai

# إعداد الواجهة
st.set_page_config(page_title="Soufiane Medical AI", layout="wide")
st.title("🩺 المساعد الطبي المتكامل")

api_key = st.sidebar.text_input("أدخل مفتاح Google API:", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # هاد السطر هو اللي كيخلي الموديل يخدم بلا وجع راس ديال v1beta
        model = genai.GenerativeModel(model_name="gemini-pro")
        
        prompt = st.chat_input("سولني أي سؤال...")
        
        if prompt:
            st.chat_message("user").markdown(prompt)
            with st.chat_message("assistant"):
                # محاولة توليد المحتوى
                response = model.generate_content(prompt)
                st.markdown(response.text)
                
    except Exception as e:
        st.error(f"خطأ: {e}")
        st.write("نصيحة: تأكد أن مفتاح الـ API الخاص بك مفعل في Google AI Studio.")
