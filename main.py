import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from langchain.chains import RetrievalQA
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint
from langchain.prompts import PromptTemplate
from langchain_core.documents import Document
from mangum import Mangum

# ✅ FastAPI App
app = FastAPI()
handler = Mangum(app)

# ✅ Prompt Template
prompt_template = PromptTemplate.from_template("""
You are a helpful assistant. Use the following context to answer the user's question.
If the answer is not in the context, respond with "I'm not sure based on the provided context."

Context:
{context}

Question:
{question}

Answer in a concise and clear manner.
""")


# ✅ Set Hugging Face API Token
os.environ["HUGGINGFACEHUB_API_TOKEN"] = ""

# ✅ Request & Response Models
class QuestionRequest(BaseModel):
    question: str

class Link(BaseModel):
    url: str
    text: str

class AnswerResponse(BaseModel):
    answer: str
    links: List[Link]

# ✅ Embeddings and Vector Store
embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embedding)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# ✅ HuggingFace LLM
llm = HuggingFaceEndpoint(
    repo_id="HuggingFaceH4/zephyr-7b-beta",
    max_new_tokens=512,
    temperature=0.1,
)

# ✅ RAG Chain with Prompt
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": prompt_template}
)

# ✅ POST Endpoint
@app.post("/ask", response_model=AnswerResponse)
def ask_question(req: QuestionRequest):
    try:
        result = qa_chain.invoke({"query": req.question})
        answer = result["result"]
        sources = result.get("source_documents", [])

        links = []
        for doc in sources[:3]:
            url = doc.metadata.get("source") or doc.metadata.get("url", "")
            if url and not url.startswith("http"):
                url = f"https://discourse.onlinedegree.iitm.ac.in/t/{url}"
            links.append(Link(url=url, text=doc.page_content.strip()[:300]))

        return AnswerResponse(answer=answer.strip(), links=links)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
