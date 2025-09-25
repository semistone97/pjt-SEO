import json, sys
import pandas as pd
import streamlit as st
from typing import Dict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from prompts.prompt_preprocess import  relevance_prompt, select_prompt, summarization_prompt, select_count
from schemas.global_state import State
from utils.preprocess_func import clean_keyword_column, filter_by_llm, clean_cp_column, clean_sv_column, scaler_and_score
from utils.config_loader import config

load_dotenv()
# ====================================================================================================
# 키워드 정제
def preprocess_data(state: State):

    with st.status("키워드 정제 진행 중...", expanded=True) as status:

        if not state['data']:
            st.warning("데이터가 없어 키워드 정제를 종료합니다.")
            if st.button("처음으로"):
                st.session_state.current_step = 'input'
                st.rerun()
            return

        
        try:
            st.info('데이터프레임 전체에 대해 정제, 스케일링, 점수 계산을 순차적으로 수행합니다')
            df = pd.DataFrame(state["data"])
            df = clean_keyword_column(df)
            df = filter_by_llm(df)
            df, sv_imputed_mask = clean_sv_column(df)
            df, cp_imputed_mask = clean_cp_column(df)

            df['is_imputed'] = sv_imputed_mask | cp_imputed_mask

            df = scaler_and_score(df)

            df.drop(columns=['is_imputed'], inplace=True, errors='ignore')
            processed_df = df.to_dict(orient='records')

            st.success(f"최종 {len(processed_df)}개 키워드 정제 및 점수 계산 완료.")
            
            status.update(label="데이터 전처리 완료", state="complete", expanded=False)

            return {'data': processed_df}
        
        except Exception as e:
            st.error(f"키워드 정제 중 에러가 발생했습니다: {e}")
            if st.button("처음으로"):
                st.session_state.current_step = 'input'
                st.rerun()
            return



# ====================================================================================================
# 노드 함수 정의

llm = ChatOpenAI(model=config['llm_relevance']['model'], temperature=float(config['llm_keyword']['temperature']))

def relevance_categorize(state: State) -> Dict:
    with st.status("연관성 작업 진행 중...", expanded=True) as status:

        st.info("LLM을 사용하여 각 키워드의 연관성을 4가지 카테고리(직접, 중간, 간접, 없음)로 분류합니다")
        
        product_name = state.get("product_name")
        product_information = state.get("product_information")
        data = state.get("data", [])

        # 데이터가 비어있으면 중단
        if not data:
            st.warning("데이터가 없어 연관성 분류를 건너뜁니다.")
            if st.button("처음으로"):
                st.session_state.current_step = 'input'
                st.rerun()
            return
        
        # DataFrame을 dict 리스트로 변환 (만약 DataFrame으로 들어올 경우)
        if isinstance(data, pd.DataFrame):
            data = data.to_dict(orient='records')

        keywords = [row['keyword'] for row in data if 'keyword' in row]
        if not keywords:
            st.warning("키워드가 없어 연관성 분류를 건너뜁니다.")
            if st.button("처음으로"):
                st.session_state.current_step = 'input'
                st.rerun()
            return
        
        chain = relevance_prompt | llm | StrOutputParser()
                
        try:
            response_str = chain.invoke({
                "product_name": product_name,
                "product_information": product_information,
                "keyword_list_str": json.dumps(keywords, ensure_ascii=False)
            })
            
            
            classifications = json.loads(response_str)
            
            classification_map = {item['keyword']: item['relevance_category'] for item in classifications}
            
            for row in data:
                if 'keyword' in row:
                    row['relevance_category'] = classification_map.get(row['keyword'], '없음')
            
            st.success(f"{len(keywords)}개 키워드에 연관성 카테고리를 부여했습니다")
            status.update(label="연관성 카테고리 부여 완료", state="complete", expanded=False)

            return {"data": data}

        except Exception as e:
            st.error(f"연관성 분류 중 에러가 발생했습니다: {e}")
            if st.button("처음으로"):
                st.session_state.current_step = 'input'
                st.rerun()
            return


# ====================================================================================================
# 상위 키워드 선택

def select_keywords(state: State) -> Dict:

    with st.status("상위 키워드 선택 중...", expanded=True) as status:


        st.info("상위 키워드 선별 및 백엔드 키워드를 저장합니다")
        
        data = state.get("data", [])

        if not data:
            st.warning("데이터가 없어 키워드 선별을 건너뜁니다.")
            if st.button("처음으로"):
                st.session_state.current_step = 'input'
                st.rerun()
            return

        simplified_data = [
            {
                "keyword": row.get("keyword"),
                "relevance_category": row.get("relevance_category"),
                "value_score": row.get("value_score")
            }
            for row in data
        ]

        chain = select_prompt | llm | StrOutputParser()

        max_retries = 3
        retries = 0
        
        while retries < max_retries:
            try:
                st.write(f"{len(simplified_data)}개 후보 중 상위 키워드 선별을 요청합니다(시도 {retries + 1}/{max_retries})")
                
                response_str = chain.invoke({
                    'select_count': select_count,
                    "data_list_str": json.dumps(simplified_data, ensure_ascii=False)
                })
                
                top_keywords_list = json.loads(response_str)
                top_keywords_set = set(top_keywords_list)

                final_data = [row for row in data if row.get("keyword") in top_keywords_set]
                
                all_keywords_set = {row.get("keyword") for row in data}
                backend_keywords_set = all_keywords_set - top_keywords_set
                backend_keywords_list = list(backend_keywords_set)

                st.success(f"\n최종 {len(final_data)}개 키워드를 선별했습니다. 탈락한 키워드 {len(backend_keywords_list)}개를 백엔드 키워드로 저장합니다.")
                status.update(label="키워드 선별 완료", state="complete", expanded=False)

                return {"data": final_data, "backend_keywords": backend_keywords_list}

            # 에러 발생 시
            except Exception as e:
                retries += 1
                st.warning(f"상위 키워드 선별 중 에러가 발생했습니다: {e}")
                if retries < max_retries:
                    st.write(f"재시도합니다({retries}/{max_retries})")
                else:
                    st.warning(f"최대 재시도 횟수({max_retries}회)를 초과했습니다. LLM 호출에 실패했습니다.")
                    break

        # LLM 호출이 최종 실패했을 때 실행되는 대체 로직
        st.write("에러 발생으로 인해, value_score 기준 상위 40개를 대신 선택합니다.")
        
        data_copy = [d for d in data if d.get('relevance_category') in ['직접', '중간']]
        if not data_copy:
            data_copy = data

        sorted_data = sorted(data_copy, key=lambda x: x.get('value_score', 0), reverse=True)
        final_data = sorted_data[:40]

        top_keywords_set = {row.get("keyword") for row in final_data}
        all_keywords_set = {row.get("keyword") for row in data}
        backend_keywords_set = all_keywords_set - top_keywords_set
        backend_keywords_list = list(backend_keywords_set)
        
        st.success(f"\n최종 {len(final_data)}개 키워드를 선별했습니다. 탈락한 키워드 {len(backend_keywords_list)}개를 백엔드 키워드로 저장합니다.")
        status.update(label="키워드 선별 완료", state="complete", expanded=False)

        return {"data": final_data, "backend_keywords": backend_keywords_list}

def information_refine(state: State):
    
    with st.status("PDF 내용을 요약합니다...", expanded=True) as status:
        
        try:
            all_extracted_text = state['product_information']
            
            # LLM을 사용하여 텍스트 요약
            full_text = "\n\n---\n\n".join(all_extracted_text)

            # LLM 초기화 및 요약 체인 구성
            llm = ChatOpenAI(model="gpt-4o", temperature=0)

            summarization_chain = summarization_prompt | llm

            # LLM 호출하여 요약 생성
            response = summarization_chain.invoke({"product_text": full_text})
            product_information = response.content
            st.success('PDF 내용을 요약했습니다.')
            st.write(product_information)
            
            status.update(label="PDF 요약 완료", state="complete", expanded=False)

            # State 업데이트
            return {"product_information": product_information}
        
        except Exception as e:
            st.error(f"PDF 요약 중 에러가 발생했습니다: {e}")
            if st.button("처음으로"):
                st.session_state.current_step = 'input'
                st.rerun()
            return
