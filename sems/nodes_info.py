import os
import json
from typing import List, Dict, Any
from langchain_community.document_loaders import PyPDFLoader, CSVLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from schemas.states import State
from utils.config_loader import config
from dotenv import load_dotenv

load_dotenv()

# 임베딩 모델 로드 (환경 변수에 따라 선택)
def load_embedding_model():
    model_name = config['embedding']['model']
    if "openai" in model_name.lower():
        return OpenAIEmbeddings(model=model_name)
    elif "huggingface" in model_name.lower():
        return HuggingFaceEmbeddings(model_name=model_name)
    else:
        raise ValueError(f"Unsupported embedding model: {model_name}")

embeddings = load_embedding_model()

def load_documents(file_paths: List[str]) -> List[Document]:
    """주어진 파일 경로에서 문서를 로드합니다."""
    all_documents = []
    for file_path in file_paths:
        _, ext = os.path.splitext(file_path)
        if ext.lower() == '.pdf':
            loader = PyPDFLoader(file_path)
            all_documents.extend(loader.load())
        elif ext.lower() == '.csv':
            loader = CSVLoader(file_path)
            all_documents.extend(loader.load())
        elif ext.lower() == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # JSON 데이터를 Document 객체로 변환 (예시)
            if isinstance(data, list):
                for i, item in enumerate(data):
                    all_documents.append(Document(page_content=json.dumps(item, ensure_ascii=False), metadata={"source": file_path, "seq_num": i}))
            else:
                all_documents.append(Document(page_content=json.dumps(data, ensure_ascii=False), metadata={"source": file_path}))

        elif ext.lower() == '.txt' or ext.lower() == '.md':
            loader = TextLoader(file_path)
            all_documents.extend(loader.load())
        else:
            print(f"Unsupported file type: {file_path}")
            continue
    return all_documents

def split_documents(documents: List[Document]) -> List[Document]:
    """문서를 청크로 분할합니다."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=int(config['rag']['chunk_size']),
        chunk_overlap=int(config['rag']['chunk_overlap'])
    )
    return text_splitter.split_documents(documents)

def create_vector_store(documents: List[Document]) -> FAISS:
    """문서로부터 FAISS 벡터 저장소를 생성하거나 로드합니다."""
    vector_store_path = config['rag']['vector_store_path']
    if os.path.exists(vector_store_path):
        print(f"Loading existing vector store from {vector_store_path}")
        return FAISS.load_local(vector_store_path, embeddings, allow_dangerous_deserialization=True)
    else:
        print("Creating new vector store...")
        vector_store = FAISS.from_documents(documents, embeddings)
        vector_store.save_local(vector_store_path)
        print(f"Vector store created and saved to {vector_store_path}")
        return vector_store

def retrieve_documents(state: State) -> State:
    """현재 상태의 정보를 기반으로 관련 문서를 검색합니다."""
    print("Retrieving documents...")
    # Ensure vector store is created/loaded before retrieval
    # This assumes an initial call to create_vector_store with actual documents has happened
    # For a test graph, we might need to explicitly call it first or ensure the path exists
    vector_store_path = config['rag']['vector_store_path']
    if not os.path.exists(vector_store_path):
        print("Vector store not found. Please ensure it's created with documents first.")
        # In a real scenario, you'd handle this by creating it or raising an error.
        # For this test node, we'll just return the state as is if no store.
        return state

    vector_store = FAISS.load_local(vector_store_path, embeddings, allow_dangerous_deserialization=True)
    retriever = vector_store.as_retriever(k=int(config['rag']['k']))

    # Use product_name and product_information from the state for retrieval
    query = f"Product: {state.product_name}\nInformation: {state.product_information}"
    docs = retriever.invoke(query)
    state.retrieved_documents = docs
    print(f"Retrieved {len(docs)} documents.")
    return state

def cross_verify_facts(state: State) -> State:
    """검색된 문서를 기반으로 생성된 콘텐츠의 사실을 교차 검증합니다."""
    print("Cross-verifying facts...")
    llm = ChatOpenAI(model=config['llm']['model'], temperature=config['llm']['temperature'])

    template = """You are a fact-checking assistant. Your task is to verify the factual accuracy of the generated content based on the provided retrieved documents.
    If the generated content contains information that contradicts the documents, or if key facts are missing from the generated content but present in the documents, point them out.
    If the generated content is factually accurate and consistent with the documents, state that it is accurate.

    Retrieved Documents:
    {documents}

    Generated Content:
    Title: {title}
    Bullet Points: {bp}
    Description: {description}

    Fact Check Report:"""

    prompt = PromptTemplate.from_template(template)

    chain = (
        {
            "documents": lambda s: "\n\n".join(doc.page_content for doc in s.retrieved_documents),
            "title": lambda s: s.title,
            "bp": lambda s: "\n".join(s.bp),
            "description": lambda s: s.description
        }
        | prompt
        | llm
    )

    fact_check_report = chain.invoke(state)
    state.fact_check_report = fact_check_report.content
    print("Fact check complete.")
    return state