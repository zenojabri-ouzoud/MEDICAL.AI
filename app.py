import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from duckduckgo_search import DDGS

st.set_page_config(page_title="AI Medical Assistant", layout="wide")
st.title("🩺 المساعد الطبي المتكامل")

# 1. إعداد الذاكرة
if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. رفع الملفات
uploaded_files = st.sidebar.file_uploader("ارفع الملفات الطبية (PDF):", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    docs = []
    for file in uploaded_files:
        with open(f"temp_{file.name}", "wb") as f: f.write(file.getbuffer())
        loader = PyPDFLoader(f"temp_{file.name}")
        docs.extend(loader.load())
    
    # تحويل الملفات لقاعدة بيانات
    vectorstore = Chroma.from_documents(docs, OpenAIEmbeddings())
    retriever = vectorstore.as_retriever()
    llm = ChatOpenAI(model="gpt-4o")
    
    # إعداد الـ Chain الحديثة
    prompt = ChatPromptTemplate.from_template("""أجب بناءً على هذه السياقات: {context}
    سؤال المستخدم: {input}""")
    
    combine_docs_chain = create_stuff_documents_chain(llm, prompt)
    st.session_state.chain = create_retrieval_chain(retriever, combine_docs_chain)

# 3. واجهة المحادثة
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("اسألني أي سؤال طبي..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        if "chain" in st.session_state:
            response = st.session_state.chain.invoke({"input": prompt})
            ans = response["answer"]
            st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})
            
            # بحث عن صورة
            with DDGS() as ddgs:
                imgs = list(ddgs.images(prompt, max_results=1))
                if imgs: st.image(imgs[0]['image'], caption="صورة توضيحية")
        else:
            st.warning("يرجى رفع ملف PDF أولاً.")
