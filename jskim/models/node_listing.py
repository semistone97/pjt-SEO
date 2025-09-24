import os
from typing import List
from langchain_core.documents import Document
from pypdf import PdfReader
from langchain_core.prompts import ChatPromptTemplate
from schemas.global_state import State
from schemas.schema import KeywordDistribute, TitleOutput, BPOutput, DescriptionOutput
from prompts.prompt_listing import keyword_prompt, title_prompt, bp_prompt, description_prompt, verification_prompt
from langchain_openai import ChatOpenAI
from utils.config_loader import config
from dotenv import load_dotenv
from datetime import datetime
import streamlit as st


load_dotenv()

llm = ChatOpenAI(model=config['llm_listing']['model'], temperature=float(config['llm_listing']['temperature']))

# ====================================================================================================
# 키워드 분배 노드
def keyword_distribute(state: State):
    with st.status("키워드 분배 중...", expanded=True) as status:

        if not state['data']:
            st.warning("\n[Skipped] 데이터가 없어 키워드 분배를 종료합니다.")
            return {}
        st.write(f'\n--- 키워드 {len(state['data'])}개에 대해 분배를 시작합니다... ---')
        
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
            
            st.success('키워드 분배를 완료하였습니다')
            
            st.write('\n=== 키워드 분배 결과 ===')
            st.write(f' Title Keyword: {len(res.title_keyword)}개')
            st.write(f' BP Keyword: {len(res.bp_keyword)}개')
            st.write(f' Description Keyword: {len(res.description_keyword)}개')
            st.write(f' Leftover: {len(res.leftover)}개')
            
                        
            status.update(label="키워드 분배 완료", state="complete", expanded=False)
            
            return {
                'title_keyword': res.title_keyword, 
                'bp_keyword': res.bp_keyword, 
                'description_keyword': res.description_keyword, 
                'leftover': res.leftover
            }    

        except Exception as e:
            st.error(f"\n[Error] 키워드 분배 중 에러가 발생했습니다: {e}")
            return {}

# ====================================================================================================
# Title 노드
def generate_title(state: State):
    with st.status("Title 작성 중...", expanded=True) as status:

        if not state['title_keyword']:
            st.write('\n[Skipped] Title 작성용 키워드가 존재하지 않습니다.')
            return {}
        
        st.write(f'\n--- Title 작성을 시작합니다... ---')
        
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
            
            st.success('Title 작성 성공')
            st.write(res.title)
            st.write(f'\n작성된 Title: 총 {len(res.title)}자')
            status.update(label="Title 작성 완료", state="complete", expanded=False)

            return {'title': res.title}

        except Exception as e:
            st.write(f"\n[Error] Title 작성 중 에러가 발생했습니다: {e}")
            return {}

# ====================================================================================================
# BP 노드
def generate_bp(state: State):
    with st.status("BP 작성 중...", expanded=True) as status:
            
        if not state['bp_keyword']:
            st.write('\n[Skipped] Bullet Point 작성용 키워드가 존재하지 않습니다.')
            return {}

        st.write(f'\n--- Bullet Point 작성을 시작합니다... ---')
        
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
            bps = res.bp

            st.success('BP 작성 성공')

            for bp in bps:
                st.write(bp)
                bp_length.append(len(bp))    
                
            st.write(f'\n작성된 Bullet Point: 각 {bp_length}자')
            status.update(label="BP 작성 완료", state="complete", expanded=False)

            return {'bp': bps}
        
        except Exception as e:
            st.write(f"\n[Error] Bullet Point 작성 중 에러가 발생했습니다: {e}")
            return {}

# ====================================================================================================
# Description 노드
def generate_description(state: State):
    with st.status("Description 작성 중...", expanded=True) as status:

        if not state['description_keyword']:
            st.write('\n[Skipped] Description 작성용 키워드가 존재하지 않습니다.')
            return {}
        
        st.write(f'\n--- Description 작성을 시작합니다... ---')
        
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
            
            st.success('Description 작성 성공')
            st.write(res.description)
            st.write(f'\n작성된 Description: 총 {len(res.description)}자')
            
            status.update(label="Description 작성 완료", state="complete", expanded=False)

            return {'description': res.description}

        except Exception as e:
            st.write(f"\n[Error] Description 작성 중 에러가 발생했습니다: {e}")
            return {}
        

# ====================================================================================================
# Listing Verification 노드

def listing_verificate(state: State) -> dict:
    with st.status("리스팅 검증 중...", expanded=True) as status:

        # 1. State에서 현재 리스팅 정보와 제품 사실 정보를 올바른 방식으로 가져옵니다.
        current_title = state["title"]
        current_bp = state["bp"]
        current_description = state["description"]
        product_information = state["product_information"]

        # 2. LLM을 초기화하고 검증 체인을 생성합니다.
        llm = ChatOpenAI(model="gpt-4o", temperature=0)
        verification_chain = verification_prompt | llm

        # 3. API 호출 1: Title 검증
        st.write("Verifying Title...")
        title_response = verification_chain.invoke({
            "product_information": product_information,
            "content_type": "Title",
            "content_to_verify": current_title
        })
        verified_title = title_response.content

        # 4. API 호출 2: Bullet Points 검증
        st.write("Verifying Bullet Points...")
        bp_as_string = "\n".join(current_bp)
        bp_response = verification_chain.invoke({
            "product_information": product_information,
            "content_type": "Bullet Points",
            "content_to_verify": bp_as_string
        })
        # LLM의 문자열 응답을 다시 리스트 형태로 변환합니다.
        verified_bp = bp_response.content.strip().split('\n')

        # 5. API 호출 3: Description 검증
        st.write("Verifying Description...")
        description_response = verification_chain.invoke({
            "product_information": product_information,
            "content_type": "Description",
            "content_to_verify": current_description
        })
        verified_description = description_response.content

        st.success("검증 및 초안 수정 성공")
        status.update(label="검증 작업 완료", state="complete", expanded=False)

        return {
            "title": verified_title,
            "bp": verified_bp,
            "description": verified_description,
        }

  
