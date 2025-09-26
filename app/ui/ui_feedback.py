import streamlit as st
from graph.builder_st import build_feedback_graph

def show_feedback_form():
    """피드백 입력 폼 표시"""
    
    main_container = st.empty()
    with main_container.container():
        if 'initial_result' not in st.session_state or st.session_state.initial_result is None:
            st.error("분석 결과를 찾을 수 없습니다.")
            if st.button("재시작"):
                st.session_state.current_step = '데이터 입력'
                st.rerun()
            return
        
        # 피드백 처리 중인 상태 체크
        if st.session_state.get('processing_feedback', False):
            show_feedback_processing()
            return
        
        result = st.session_state.initial_result
        
        # 이전 피드백 표시
        if st.session_state.feedback_history:
            with st.expander("이전 피드백 내역", expanded=True):
                for i, feedback in enumerate(st.session_state.feedback_history, 1):
                    st.info(f"피드백 {i}: {feedback}")
        
        # 결과 표시 (일반 텍스트로)
        with st.expander("결과물 출력", expanded=True):
            
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
                
        # 피드백 입력
        user_feedback = st.text_area(
            '사용자 피드백을 입력해 주세요.',
            value=st.session_state.current_feedback,
            height=150,
            help="결과에 대한 피드백을 입력하시면 개선된 결과를 제공해드립니다.",
            key="feedback_input"
        )
        
        # 버튼들을 나란히 배치
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            # 피드백 제출 버튼
            if st.button('피드백 제출', type="primary"):
                if user_feedback.strip():
                    # 피드백 처리 상태로 전환
                    main_container.empty()
                    st.session_state.processing_feedback = True
                    st.session_state.current_feedback_text = user_feedback.strip()
                    st.rerun()
                else:
                    st.warning('피드백을 입력해주세요.')
        
        with col2:
            if st.button('완료'):
                st.session_state.current_step = '완료'
                st.rerun()
        
        with col3:
            # 결과 다운로드 기능
            if st.session_state.initial_result:
                # 피드백 히스토리 포함한 결과 텍스트
                feedback_history_text = ""
                if st.session_state.feedback_history:
                    feedback_history_text = "\n피드백 내역:\n"
                    for i, feedback in enumerate(st.session_state.feedback_history, 1):
                        feedback_history_text += f"{i}. {feedback}\n"
                
                result_text = f"""
[키워드 기반 리스팅 결과]

상품명: {st.session_state.get('product_name', 'N/A')}
카테고리: {st.session_state.get('category', 'N/A')}
피드백 반영 횟수: {st.session_state.get('feedback_count', 0)}
{feedback_history_text}

[Title]
{st.session_state.initial_result.get('title', 'N/A')}

[Bullet Points]
{chr(10).join(f'{i}. {bp}' for i, bp in enumerate(st.session_state.initial_result.get('bp', []), 1))}

[Description]
{st.session_state.initial_result.get('description', 'N/A')}
                """
                st.download_button(
                    "임시저장",
                    result_text,
                    file_name=f"temp_{'_'.join(st.session_state.initial_result.get('title', 'N/A').split())}_product_listing.txt",
                    mime="text/plain"
                )


def show_feedback_processing():
    """피드백 처리 중 화면 표시"""
    st.subheader("피드백 처리 중")
    
    # 전체 폭으로 피드백 처리 상태 표시
    with st.status("피드백을 반영하여 결과를 개선하고 있습니다...", expanded=True) as status:
        try:
            feedback_builder = build_feedback_graph()
            
            # 피드백 그래프를 위한 상태 준비
            feedback_state = {
                **st.session_state.initial_result,
                'user_feedback': st.session_state.current_feedback_text
            }
            
            st.write("피드백 내용 분석 중...")
            
            # 피드백 그래프 실행
            updated_result = feedback_builder.invoke(feedback_state)
            
            st.write("결과 업데이트 중...")
            
            # 결과 업데이트
            st.session_state.initial_result.update(updated_result)
            st.session_state.feedback_history.append(st.session_state.current_feedback_text)
            st.session_state.feedback_count += 1
            st.session_state.current_feedback = ""
            
            status.update(label="피드백 처리 완료!", state="complete")
            
            st.success("피드백이 성공적으로 반영되었습니다!")
            
        except Exception as e:
            status.update(label="피드백 처리 실패", state="error")
            st.error(f"피드백 처리 중 오류: {str(e)}")
        
        finally:
            # 처리 완료 후 상태 초기화하고 피드백 폼으로 돌아가기
            st.session_state.processing_feedback = False
            if 'current_feedback_text' in st.session_state:
                del st.session_state.current_feedback_text
            
            st.rerun()