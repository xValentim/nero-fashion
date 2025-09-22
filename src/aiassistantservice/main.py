# src/aiassistantservice/main.py
from fastapi import FastAPI
from pydantic import BaseModel
import os

# LangChain (OpenAI)
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set")

# Inicializa LLM via LangChain
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.2,
    api_key=OPENAI_API_KEY
)

# Prompt simples (MVP). Você pode enriquecer depois com contexto / RAG.
prompt = ChatPromptTemplate.from_messages([
    ("system", "Você é um assistente de compras útil e direto."),
    ("human", "{user_message}")
])
chain = prompt | llm | StrOutputParser()

class RequestBody(BaseModel):
    message: str
    image: str | None = None  # Mantemos a assinatura, mesmo que ignoremos por ora

app = FastAPI()

@app.get("/healthz")
def health():
    return {"status": "ok"}

@app.post("/")
def root(body: RequestBody):
    # Para MVP, ignore a imagem; depois podemos analisar base64/URL.
    output_text = chain.invoke({"user_message": body.message})
    # Contrato que o frontend espera: {"content": "..."}
    return {"content": output_text}
