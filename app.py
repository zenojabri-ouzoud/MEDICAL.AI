import streamlit as st
from openai import OpenAI
from streamlit_mic_recorder import mic_recorder
import pypdf
from PIL import Image
import io

# إعدادات الواجهة
st.set_page_config(page_title="Soufiane Medical AI Pro", layout="wide")

# CSS لتجميل الواجهة
st.markdown("""
    <style>
    .main {background-color: #f0f2f6;}
    .stChatFloatingInputContainer {border: 2px solid #4CAF50;}
    </style>
    """, unsafe_allow_html=True)

st.title("🩺 المساعد الطبي الرقمي المتطور")
st.subheader("تحليل - استشارة - توجيه")

# إعدادات الـ API
api_key = st.sidebar.text_input("ادخل OpenAI API Key:", type="password")

if api_key:
    client = OpenAI(api_key=api_key)
    
    # القائمة الجانبية للملفات
    with st.sidebar:
        st.header("أدوات التحليل")
        uploaded_file = st.file_uploader("ارفع ملف طبي (PDF أو صور):", type=["pdf", "png", "jpg", "jpeg"])
        st.divider()
        st.write("ملاحظة: المساعد الطبي لا يغني عن زيارة الطبيب.")

    # إعداد ذاكرة المحادثة والشخصية
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "أنت مساعد طبي خبير. حلل المستندات الطبية، أجب على الأسئلة الطبية، وقدم نصائح عامة. دائماً ذكر المستخدم بأنك لست طبيباً بشرياً وأنه يجب استشارة مختص للحالات الحرجة."}
        ]

    # معالجة الملفات المرفوعة
    if uploaded_file and "doc_loaded" not in st.session_state:
        with st.spinner("جاري تحليل الملف..."):
            if uploaded_file.type == "application/pdf":
                reader = pypdf.PdfReader(uploaded_file)
                text = "".join([page.extract_text() for page in reader.pages])
                st.session_state.messages.append({"role": "system", "content": f"المعلومات المرفقة من ملف PDF: {text[:10000]}"})
            else:
                st.image(uploaded_file, caption="تم رفع صورة طبية")
                st.session_state.messages.append({"role": "system", "content": "المستخدم أرفق صورة طبية. إذا سألك عنها، قم بتحليلها بدقة."})
            st.session_state.doc_loaded = True
            st.success("تم تحليل الملف المرفق بنجاح!")

    # واجهة الصوت والكتابة
    st.write("### ابدأ الاستشارة:")
    col1, col2 = st.columns([1, 5])
    with col1:
        audio_data = mic_recorder(start_prompt="🎙️ تحدث", stop_prompt="⏹️ توقف")
    
    user_input = None
    if audio_data:
        audio_file = io.BytesIO(audio_data['bytes'])
        audio_file.name = "audio.wav"
        transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
        user_input = transcript.text
    else:
        user_input = st.chat_input("اكتب سؤالك الطبي هنا...")

    # عرض المحادثة
    for msg in st.session_state.messages:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
            
        with st.chat_message("assistant"):
            with st.spinner("جاري التفكير..."):
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=st.session_state.messages
                )
                ans = response.choices[0].message.content
                st.markdown(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
