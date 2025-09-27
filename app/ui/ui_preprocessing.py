import streamlit as st
from graph.builder_st import build_initial_graph
from utils.data_loader_js import load_information_pdf_streamlit, load_keywords_csv_streamlit


def show_analysis_progress():
    """분석 진행 상황 표시"""
    st.subheader("📋 분석 정보")
    info_col1, info_col2 = st.columns(2)
    
    with info_col1:
        st.metric("상품명", st.session_state.product_name)
    
    with info_col2:
        st.metric("카테고리", st.session_state.category)
    
    st.divider()
    
    # 분석이 아직 시작되지 않았다면 시작
    if not st.session_state.analysis_started:
        with st.spinner("🔍 데이터를 로드하고 분석 중입니다..."):
            # 데이터 로드
            st.subheader("📂 데이터 로딩")
            
            with st.status("데이터 로딩 중...", expanded=True) as status:
                # CSV 파일 로드
                st.write("키워드 CSV 파일 처리 중...")
                raw_df, csv_messages, good_csv_files = load_keywords_csv_streamlit(
                    st.session_state.csv_files
                )
                
                # CSV 처리 결과 표시
                if raw_df is not None:
                    st.success(f"✅ 키워드 데이터 로드 완료 ({len(raw_df)} rows)")
                    st.write(f"처리된 파일: {', '.join(good_csv_files)}")
                else:
                    st.error("❌ 키워드 데이터 로드 실패")
                    for msg in csv_messages:
                        st.write(msg)
                    if st.button("다시 시도"):
                        st.session_state.current_step = '데이터 입력'
                        st.rerun()
                    return
                
                # PDF 파일 로드
                st.write("상품 정보 PDF 파일 처리 중...")
                product_docs, product_information, pdf_messages = load_information_pdf_streamlit(
                    st.session_state.pdf_files
                )
                
                # PDF 처리 결과 표시
                if product_docs:
                    st.success(f"✅ 상품 정보 로드 완료 ({len(product_docs)}개 문서)")
                else:
                    st.warning("⚠️ PDF 파일이 없거나 처리되지 않음")

                status.update(label="데이터 로딩 완료!", state="complete", expanded=False)
            
            # 초기 그래프 실행
            st.subheader("🔄 초안 작성")
            
            try:
                initial_builder = build_initial_graph()
                result = initial_builder.invoke({
                    'product_name': st.session_state.product_name,
                    'category': st.session_state.category,
                    'data': raw_df, 
                    'product_docs': product_docs,
                    'product_information': product_information
                })
                
                # 결과를 session state에 저장
                st.session_state.initial_result = result
                st.session_state.analysis_started = True
                st.session_state.current_step = '피드백'
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ 분석 중 오류 발생: {str(e)}")
                if st.button("다시 시도"):
                    st.session_state.current_step = '데이터 입력'
                    st.session_state.analysis_started = False
                    st.rerun()