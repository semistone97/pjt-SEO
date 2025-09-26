import streamlit as st
from utils.result_format import result_format

def show_final_results():
    """최종 결과 표시"""
    st.success("분석이 완료되었습니다!")
    
    if 'initial_result' in st.session_state:
        result = st.session_state.initial_result
        
        # 반영된 피드백 내역 표시
        if st.session_state.feedback_history:
            with st.expander("=== 반영된 피드백 내역 ===", expanded=False):
                for i, feedback in enumerate(st.session_state.feedback_history, 1):
                    st.info(f"피드백 {i}: {feedback}")
        
        # 최종 결과 표시 (일반 텍스트로)
        
        if 'title' in result:
            st.write("Title:")
            st.write(result["title"])
            st.write("")
        
        if 'bp' in result:
            st.write("BP:")
            for i, bp in enumerate(result['bp'], 1):
                st.write(f"{i}. {bp}")
            st.write("")
        
        if 'description' in result:
            st.write("Description:")
            st.write(result["description"])
        
        if st.session_state.feedback_count > 0:
            st.info(f"총 {st.session_state.feedback_count}번의 피드백이 반영되었습니다.")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button('새로운 분석 시작', type="primary"):
            # 모든 상태 초기화
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    with col2:
        # 결과 다운로드 기능
        if 'initial_result' in st.session_state:
        
            result_text = result_format()

            st.download_button(
                "최종 결과 다운로드",
                result_text,
                file_name=f"{'_'.join(st.session_state.initial_result.get('title', 'N/A').split())}_product_listing_final.txt",
                mime="text/plain"
            )
