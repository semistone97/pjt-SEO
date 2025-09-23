import os
from typing import List
from langchain_core.documents import Document
from pypdf import PdfReader # 이 라이브러리는 pip install pypdf 로 설치해야 합니다.

# KeywordResearchState는 schemas/states.py에 정의되어 있다고 가정합니다.
from schemas.global_state import State

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from prompts.prompt_listing import verification_prompt
import json


# input_data 디렉토리가 존재하는지 확인하고 없으면 생성합니다.
# node_info.py는 program/models 에 있고, input_data는 program 에 있으므로,
# program/models 에서 .. (program) 로 이동 후 input_data 로 들어갑니다.
INPUT_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "input_data")
os.makedirs(INPUT_DATA_DIR, exist_ok=True)

def information_extract(state: State) -> dict:
    """
    정보 추출 노드 (information_extract)

    목적:
    - `program/input_data` 디렉토리 내의 모든 PDF 파일을 찾아 내용을 읽어옵니다.
    - 읽어온 PDF 내용을 `State`의 `product_docs: List[Document]`에 저장합니다.
    - LLM을 사용하여 `product_docs`의 내용을 요약하고, 핵심 제품 정보를 추출하여 `State`의 `product_information: str`에 저장합니다.

    입력 (State에서 가져올 정보):
    - (없음)

    출력 (State에 업데이트할 정보):
    - product_docs (List[Document]): PDF에서 읽어온 문서 객체들의 목록.
    - product_information (str): 추출 및 요약된 핵심 제품 정보.
    """
    print("---정보 추출 노드 실행 중---")

    product_docs: List[Document] = []
    all_extracted_text = []

    # PDF 파일 찾기 및 읽기
    for filename in os.listdir(INPUT_DATA_DIR):
        if filename.endswith(".pdf"):
            filepath = os.path.join(INPUT_DATA_DIR, filename)
            try:
                reader = PdfReader(filepath)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                
                product_docs.append(Document(page_content=text, metadata={"source": filename}))
                all_extracted_text.append(text)
                print(f'읽어온 PDF 파일 : {filename}')

            except Exception as e:
                print(f"[Error] PDF 파일 {filename} 읽기 오류: {e}")

    # LLM을 사용하여 텍스트 요약
    if all_extracted_text:
        # 모든 PDF 내용을 하나의 문자열로 결합
        full_text = "\n\n---\n\n".join(all_extracted_text)

        # LLM 초기화 및 요약 체인 구성
        llm = ChatOpenAI(model="gpt-4o", temperature=0)
        
        summarization_template = ChatPromptTemplate.from_messages([
            ("system", "You are an expert at summarizing product information. Please extract the key features, specifications, and purpose of the product from the following text in a concise manner. The summary should be in Korean."),
            ("human", "Product Text:\n```\n{product_text}\n```")
        ])
        
        summarization_chain = summarization_template | llm

        print("---PDF 내용 요약 중---")
        # LLM 호출하여 요약 생성
        response = summarization_chain.invoke({"product_text": full_text})
        product_information = response.content
        print("---요약 완료---")
        print(f"요약된 제품 정보: {product_information}")

    else:
        product_information = "제품 정보를 찾을 수 없습니다."

    # State 업데이트
    return {
        "product_docs": product_docs,
        "product_information": product_information
    }

# verification 노드는 나중에 구현
def listing_verificate(state: State) -> dict:
    """
    검증 노드 (verification_node)

    목적:
    - `State`의 `product_docs` 및 `product_information`을 활용하여 `title`, `bp`, `description`을 교차 검증합니다.
    - 검증 결과에 따라 `title`, `bp`, `description`을 수정하고 `State`에 반영합니다.

    입력 (State에서 가져올 정보):
    - title (str)
    - bp (List[str])
    - description (str)
    - product_information (str)

    출력 (State에 업데이트할 정보):
    - title (str)
    - bp (List[str])
    - description (str)
    """
    print("---검증 노드 실행 중---")

    # LLM 초기화
    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    # LLM 체인 구성
    verification_chain = verification_prompt | llm

    # State에서 필요한 정보 가져오기
    current_title = state.get("title", "")
    current_bp = state.get("bp", [])
    current_description = state.get("description", "")
    product_information = state.get("product_information", "")

    # LLM 호출
    response = verification_chain.invoke({
        "product_information": product_information,
        "title": current_title,
        "bullet_points": "\n".join(current_bp),
        "description": current_description
    })

    # LLM 응답 파싱
    try:
        verified_listing = json.loads(response.content)
        verified_title = verified_listing.get("title", current_title)
        verified_bp = verified_listing.get("bullet_points", current_bp)
        verified_description = verified_listing.get("description", current_description)
    except json.JSONDecodeError as e:
        print(f"[Error] LLM 응답 파싱 오류: {e}")
        print(f"응답 내용: {response.content}")
        # 오류 발생 시 기존 값 유지
        verified_title = current_title
        verified_bp = current_bp
        verified_description = current_description

    # State 업데이트
    return {
        "title": verified_title,
        "bp": verified_bp,
        "description": verified_description,
    }