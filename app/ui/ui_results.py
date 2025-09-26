import streamlit as st

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
            # 피드백 히스토리 포함한 결과 텍스트
            feedback_history_text = ""
            if st.session_state.feedback_history:
                feedback_history_text = "\n반영된 피드백 내역:\n"
                for i, feedback in enumerate(st.session_state.feedback_history, 1):
                    feedback_history_text += f"{i}. {feedback}\n"
            
            result_text = f"""
[키워드 기반 리스팅 결과]

상품명: {st.session_state.get('product_name', 'N/A')}
카테고리: {st.session_state.get('category', 'N/A')}
피드백 반영 횟수: {st.session_state.get('feedback_count', 0)}
{feedback_history_text}

[Title] - {len(st.session_state.initial_result.get('title', 'N/A'))}자
{st.session_state.initial_result.get('title', 'N/A')}

[Bullet Points]
{chr(10).join(f'{i}. {bp}' for i, bp in enumerate(st.session_state.initial_result.get('bp', []), 1))}

[Description] - {(st.session_state.initial_result.get('description', 'N/A'))}자
{st.session_state.initial_result.get('description', 'N/A')}

미사용 키워드:
{", ".join(
    st.session_state.initial_result.get('leftover', []) + 
    st.session_state.initial_result.get('backend_keywords', [])
    )
}

            """
            st.download_button(
                "최종 결과 다운로드",
                result_text,
                file_name=f"{'_'.join(st.session_state.initial_result.get('title', 'N/A').split())}_product_listing_final.txt",
                mime="text/plain"
            )
