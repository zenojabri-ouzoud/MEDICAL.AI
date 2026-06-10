import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from duckduckgo_search import DDGS

# إعدادات الواجهة
st.set_page_config(page_title="Medical AI Assistant", layout="wide")
st.title("🩺 المساعد الطبي المتكامل")

# 1. نظام رفع الملفات المتعددة
st.sidebar.title("إدارة المصادر")
uploaded_files = st.sidebar.file_uploader("ارفع الملفات الطبية (PDF):", type=["pdf"], accept_multiple_files=True)

# تهيئة الذاكرة (Chat History)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. معالجة الملفات في الخلفية
if uploaded_files:
    documents = []
    for uploaded_file in uploaded_files:
        with open(f"temp_{uploaded_file.name}", "wb") as f:
            f.write(uploaded_file.getbuffer())
        loader = PyPDFLoader(f"temp_{uploaded_file.name}")
        documents.extend(loader.load())
    
    # تحويل الملفات لقاعدة بيانات
    vectorstore = Chroma.from_documents(documents, OpenAIEmbeddings())
    chain = RetrievalQA.from_chain_type(llm=ChatOpenAI(model="gpt-4"), retriever=vectorstore.as_retriever())
    st.session_state.chain = chain

# 3. واجهة المحادثة (Chat Interface)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. إمكانية المحادثة والبحث
if prompt := st.chat_input("اسألني عن أي شيء طبي..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if "chain" in st.session_state:
            response = st.session_state.chain.invoke(prompt)
            result = response['result']
            st.markdown(result)
            
            # البحث عن صورة توضيحية تلقائياً
            with DDGS() as ddgs:
                img_res = list(ddgs.images(prompt, max_results=1))
                if img_res:
                    st.image(img_res[0]['image'], caption="صورة توضيحية من الويب")
            
            st.session_state.messages.append({"role": "assistant", "content": result})
        else:
            st.warning("يرجى رفع ملف طبي أولاً!")