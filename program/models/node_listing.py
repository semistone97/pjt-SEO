import os
from typing import List
from langchain_core.documents import Document
from pypdf import PdfReader # 이 라이브러리는 pip install pypdf 로 설치해야 합니다.
from langchain_core.prompts import ChatPromptTemplate
import json

from schemas.global_state import State
from schemas.schema import KeywordDistribute, TitleOutput, BPOutput, DescriptionOutput
from prompts.prompt_listing import keyword_prompt, title_prompt, bp_prompt, description_prompt, verification_prompt
from langchain_openai import ChatOpenAI
from utils.config_loader import config
from dotenv import load_dotenv



load_dotenv()

llm = ChatOpenAI(model=config['llm_listing']['model'], temperature=float(config['llm_listing']['temperature']))

# ====================================================================================================
# 키워드 분배 노드
def keyword_distribute(state: State):
    
    if not state['data']:
        print("\n데이터가 없어 키워드 분배를 종료합니다.")
        return {}
    
    print(f'\n--- 키워드 {len(state['data'])}개에 대해 분배를 시작합니다... ---')
    
    try:
        prompt = keyword_prompt.invoke(
            {
                'product_name': state['product_name'], 
                'category': state['category'],
                'product_information': state['product_information'], 
                'data': state['data'],
            }
        )
        structured_llm = llm.with_structured_output(KeywordDistribute)
        res = structured_llm.invoke(prompt)
        
        print('\n=== 키워드 분배 결과 ===')
        print(f'Title Keyword: {len(res.title_keyword)}개')
        print(f'BP Keyword: {len(res.bp_keyword)}개')
        print(f'Description Keyword: {len(res.description_keyword)}개')
        print(f'Leftover: {len(res.leftover)}개')
        
        return {
            'title_keyword': res.title_keyword, 
            'bp_keyword': res.bp_keyword, 
            'description_keyword': res.description_keyword, 
            'leftover': res.leftover
        }    

    except Exception as e:
        print(f"\n키워드 분배 중 에러가 발생했습니다: {e}")
        return {}

# ====================================================================================================
# Title 노드
def generate_title(state: State):
    
    if not state['title_keyword']:
        print('\nTitle 작성용 키워드가 존재하지 않습니다.')
        return {}
    
    print(f'\n--- Title 작성을 시작합니다... ---')
    
    try:
        prompt = title_prompt.invoke(
            {
                'product_name': state['product_name'], 
                'category': state['category'],
                'product_information': state['product_information'], 
                'title_keyword': state['title_keyword'],
            }
        )
        structured_llm = llm.with_structured_output(TitleOutput)
        res = structured_llm.invoke(prompt)
        print(f'\n작성된 Title: 총 {len(res.title)}자')
        return {'title': res.title}

    except Exception as e:
        print(f"\nTitle 작성 중 에러가 발생했습니다: {e}")
        return {}

# ====================================================================================================
# BP 노드
def generate_bp(state: State):
    
    if not state['bp_keyword']:
        print('\nBullet Point 작성용 키워드가 존재하지 않습니다.')
        return {}

    print(f'\n--- Bullet Point 작성을 시작합니다... ---')
    
    try:
        prompt = bp_prompt.invoke(
            {
                'product_name': state['product_name'], 
                'category': state['category'],
                'product_information': state['product_information'], 
                'bp_keyword': state['bp_keyword'],
            }
        )
        structured_llm = llm.with_structured_output(BPOutput)
        res = structured_llm.invoke(prompt)
        bp_length = []
        for bp in res.bp:
            bp_length.append(len(bp))    
        print(f'\n작성된 Bullet Point: 각 {bp_length}자')
        return {'bp': res.bp}
    
    except Exception as e:
        print(f"\nBullet Point 작성 중 에러가 발생했습니다: {e}")
        return {}

# ====================================================================================================
# Description 노드
def generate_description(state: State):
    
    if not state['description_keyword']:
        print('\nDescription 작성용 키워드가 존재하지 않습니다.')
        return {}
    
    print(f'\n--- Description 작성을 시작합니다... ---')
    
    try:
        prompt = description_prompt.invoke(
            {
                'bp_result': state['bp'],
                'product_name': state['product_name'], 
                'category': state['category'],
                'product_information': state['product_information'], 
                'description_keyword': state['description_keyword'],
            }
        )
        structured_llm = llm.with_structured_output(DescriptionOutput)
        res = structured_llm.invoke(prompt)
        print(f'\n작성된 Description: 총 {len(res.description)}자')
        return {'description': res.description}

    except Exception as e:
        print(f"\nDescription 작성 중 에러가 발생했습니다: {e}")
        return {}
    
# ====================================================================================================
# Information Extract 노드
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
                print(f"PDF 파일 {filename} 읽기 오류: {e}")

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

# ====================================================================================================
# Listing Verification 노드

def listing_verificate(state: State) -> dict:
    """
    Verifies and corrects the title, bullet points, and description separately based on product information,
    using three distinct LLM calls.

    Args:
        state (State): The current graph state.

    Returns:
        dict: A dictionary containing the verified 'title', 'bp', and 'description'.
    """
    print("---Executing Verification Node---")

    # 1. State에서 현재 리스팅 정보와 제품 사실 정보를 올바른 방식으로 가져옵니다.
    current_title = state["title"]
    current_bp = state["bp"]
    current_description = state["description"]
    product_information = state["product_information"]

    # 2. LLM을 초기화하고 검증 체인을 생성합니다.
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    verification_chain = verification_prompt | llm

    # 3. API 호출 1: Title 검증
    print("Verifying Title...")
    title_response = verification_chain.invoke({
        "product_information": product_information,
        "content_type": "Title",
        "content_to_verify": current_title
    })
    verified_title = title_response.content

    # 4. API 호출 2: Bullet Points 검증
    print("Verifying Bullet Points...")
    bp_as_string = "\n".join(current_bp)
    bp_response = verification_chain.invoke({
        "product_information": product_information,
        "content_type": "Bullet Points",
        "content_to_verify": bp_as_string
    })
    # LLM의 문자열 응답을 다시 리스트 형태로 변환합니다.
    verified_bp = bp_response.content.strip().split('\n')

    # 5. API 호출 3: Description 검증
    print("Verifying Description...")
    description_response = verification_chain.invoke({
        "product_information": product_information,
        "content_type": "Description",
        "content_to_verify": current_description
    })
    verified_description = description_response.content

    print("---Verification Complete---")
    
    # 6. 검증 완료된 콘텐츠를 State 업데이트를 위해 반환합니다.
    return {
        "title": verified_title,
        "bp": verified_bp,
        "description": verified_description,
    }