import streamlit as st
from langchain_openai import ChatOpenAI
from schemas.global_state import State
from schemas.schema import KeywordDistribute
from prompts.prompt_listing import keyword_prompt, verification_prompt
from utils.config_loader import config
from utils.listing_func import generate_title, generate_bp, generate_description
from dotenv import load_dotenv


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
# 노드 작성
def generate_listing(state: State):
    """
    Title, Bullet Points, Description을 순차적으로 생성하기 위해
    기존의 개별 생성 함수들을 호출하는 메인 함수.
    """
    
    # 1. Title 생성 함수 호출
    title_update = generate_title(state)
    
    # 2. BP 생성 함수 호출
    bp_update = generate_bp(state)
    
    # 3. Description 생성을 위해 state를 임시로 업데이트
    # (generate_description 함수는 state에서 'bp' 결과를 필요로 함)
    temp_state = state.copy()
    temp_state.update(bp_update) # bp_update 딕셔너리 {'bp': [...]} 를 추가
        
    description_update = generate_description(temp_state)
    
    # 4. 모든 결과를 취합하여 최종 업데이트 딕셔너리 생xw성
    final_update = {}
    final_update.update(title_update)
    final_update.update(bp_update)
    final_update.update(description_update)
    
    return final_update

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

  
