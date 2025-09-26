import streamlit as st
from dotenv import load_dotenv
from ui.ui_input import show_sidebar, show_input_form
from ui.ui_preprocessing import show_analysis_progress
from ui.ui_feedback import show_feedback_form
from ui.ui_results import show_final_results

# 환경 변수 로드
load_dotenv()

def main():
    # Streamlit 페이지 설정
    st.set_page_config(
        page_title="아마존 리스팅 최적화 에이전트",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("아마존 리스팅 최적화 에이전트")
    
    # Session state 초기화
    
    init_session_state()
    
    # 프로그램 설명 및 약관
    with st.expander("사용 시 주의사항", expanded=True):
        st.markdown("""
        ### 프로그램 개요
        - 이 에이전트는 상품명과 카테고리, 키워드를 입력받아 사용할 키워드를 선정하고, Amazon 규격에 맞는 리스팅을 생성합니다.
        - 사용자의 피드백을 반영해 리스팅을 수정할 수 있습니다.
        
        ### 지원되는 csv 형식
        대/소문자 구분 없음
        - keywords / search volume / competing products
        - phrase / search volume / keyword sales

        ### 사용방법
        1. 사이드바에 상품명, 카테고리를 입력하고, 키워드가 포함된 csv파일을 업로드해 주세요. csv파일은 형식에 맞다면, 여러 파일을 넣는 것도 지원합니다.
        2. (선택사항)정확한 리스팅 생성을 위해, 상품정보가 담긴 pdf 파일을 업로드해 주세요.
        3. [분석 시작] 버튼을 클릭해 주세요.
        4. 결과물이 출력되면, 사용자 피드백을 입력할 수 있습니다.
        5. 피드백을 입력 후, [피드백 제출] 버튼을 누르면 피드백을 적용해 리스팅을 재작성합니다.
        6. [임시저장] 버튼을 누르면, 현재 출력된 리스팅 버전을 텍스트 파일로 저장합니다.
        7. [완료] 버튼을 누르면, 현재 과정을 종료합니다. [최종 결과 다운로드] 버튼으로 Title, Bullet Points, Description, Backend Keywords가 포함된 파일을 텍스트 파일로 저장할 수 있습니다.
        8. [새로운 분석 시작] 버튼을 통해 새로운 리스팅을 생성할 수도 있습니다.
        
        ### 경고
        리스팅 결과는 AI가 생성한 문서입니다. 책임감 있는 사용을 위해서는 인간의 감독이 필수적입니다. 결과는 참고용으로만 사용하시기 바랍니다.
        """)
    
    # 사이드바 - 모든 단계에서 공통으로 표시
    show_sidebar()
    
    # 현재 단계에 따른 화면 표시
    step = st.session_state.current_step
    if step == '데이터 입력':
        show_input_form()
    elif step == '초안 생성':
        show_analysis_progress()
    elif step == '피드백':
        show_feedback_form()
    elif step == '완료':
        show_final_results()

def init_session_state():
    defaults = {
        'analysis_started': False,
        'initial_result': None,
        'current_step': '데이터 입력',
        'feedback_count': 0,
        'feedback_history': [],
        'current_feedback': "",
        'processing_feedback': False,
        'current_feedback_text': ""
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

if __name__ == "__main__":
    main()