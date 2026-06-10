import streamlit as st
from openai import OpenAI
import pypdf
from duckduckgo_search import DDGS

st.title("🩺 المساعد الطبي (خفيف وسريع)")

api_key = st.sidebar.text_input("ادخل OpenAI API Key:", type="password")

if api_key:
    client = OpenAI(api_key=api_key)
    
    uploaded_file = st.file_uploader("ارفع ملف PDF", type="pdf")
    
    if uploaded_file:
        # قراءة الـ PDF مباشرة
        reader = pypdf.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
            
        user_query = st.text_input("اسألني عن الملف:")
        
        if st.button("إرسال"):
            # إرسال السؤال لـ OpenAI مباشرة بدون LangChain
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "أنت مساعد طبي. أجب بناءً على هذا النص: " + text[:10000]},
                    {"role": "user", "content": user_query}
                ]
            )
            st.write(response.choices[0].message.content)
            
            # بحث صور سريع
            with DDGS() as ddgs:
                results = list(ddgs.images(user_query, max_results=1))
                if results: st.image(results[0]['image'])
