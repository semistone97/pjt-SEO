import os
import streamlit as st
import pandas as pd
import builtins
from dotenv import load_dotenv
from graph.builder import build_graph

from utils.data_loader_st import load_information_pdf_streamlit, load_keywords_csv_streamlit

# 환경 변수 로드
load_dotenv()

def main():
    # Streamlit 페이지 설정
    st.set_page_config(
        page_title="상품 분석 도구",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 상품 분석 도구")
    
    # Session state 초기화
    if 'analysis_started' not in st.session_state:
        st.session_state.analysis_started = False
    if 'graph_state' not in st.session_state:
        st.session_state.graph_state = None
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 'input'  # input, analysis, feedback, complete
    
    # 프로그램 설명 및 약관
    with st.expander("📋 프로그램 설명 및 약관", expanded=False):
        st.markdown("""
        ### 프로그램 설명
        이 도구는 상품명과 카테고리를 입력받아 키워드 데이터와 상품 정보를 분석합니다.
        
        ### 사용 약관
        - 정확한 상품명을 입력해주세요
        - 카테고리는 구체적으로 작성해주세요
        - 분석 결과는 참고용으로만 사용하시기 바랍니다
        """)
    
    # 현재 단계에 따른 화면 표시
    if st.session_state.current_step == 'input':
        show_input_form()
    elif st.session_state.current_step == 'analysis':
        show_analysis_progress()
    elif st.session_state.current_step == 'feedback':
        show_feedback_form()
    elif st.session_state.current_step == 'complete':
        show_final_results()

def show_input_form():
    """초기 입력 폼 표시"""
    # 사이드바에 입력 폼 생성
    with st.sidebar:
        st.header("🔧 설정")
        
        # 상품명 입력
        product_name = st.text_input(
            "상품명",
            placeholder="분석하고 싶은 상품명을 입력하세요",
            help="정확한 상품명을 입력하면 더 정확한 분석이 가능합니다"
        )
        
        # 카테고리 입력
        category = st.text_input(
            "상품 카테고리",
            placeholder="예: 전자제품, 의류, 화장품 등",
            help="상품이 속하는 카테고리를 입력하세요"
        )
        
        st.divider()
        
        # 파일 업로드 섹션
        st.subheader("📁 파일 업로드")
        
        # CSV 파일 업로드
        csv_files = st.file_uploader(
            "**키워드 CSV 파일**",
            type=['csv'],
            accept_multiple_files=True,
            help="필요한 컬럼: Keywords/Phrase, Search Volume, Competing Products/Keyword Sales"
        )
        
        if csv_files:
            st.success(f"✅ {len(csv_files)}개의 CSV 파일이 업로드되었습니다.")
        
        pdf_files = st.file_uploader(
            "**상품정보 PDF 파일 (선택사항)**",
            type=['pdf'],
            accept_multiple_files=True,
            help="상품 정보가 없으면 리스팅 검증 과정을 생략합니다"
        )
        
        if pdf_files:
            st.success(f"✅ {len(pdf_files)}개의 PDF 파일이 업로드되었습니다.")
        
        st.divider()
        
        # 분석 시작 버튼
        analyze_button = st.button("분석 시작", type="primary")
    
    # 메인 컨텐츠 영역
    if not product_name or not category or not csv_files:
        # 요구사항 체크
        requirements = []
        if not product_name:
            requirements.append("✗ 상품명")
        else:
            requirements.append("✓ 상품명")
            
        if not category:
            requirements.append("✗ 카테고리")
        else:
            requirements.append("✓ 카테고리")
            
        if not csv_files:
            requirements.append("✗ CSV 파일")
        else:
            requirements.append("✓ CSV 파일")
        
        st.info("👈 다음 항목들을 완성하고 '분석 시작' 버튼을 클릭하세요:")
        for req in requirements:
            st.write(req)
        
        st.divider()
        
        # 업로드된 파일 표시
        st.subheader("📋 업로드된 파일")
        if csv_files:
            st.write("**CSV 파일:**")
            for file in csv_files:
                st.write(f"- {file.name}")
        
        if pdf_files:
            st.write("**PDF 파일:**")
            for file in pdf_files:
                st.write(f"- {file.name}")
        
        if not csv_files and not pdf_files:
            st.info("파일이 업로드되지 않았습니다.")
    
    elif analyze_button:
        # 분석 준비 - session state에 저장
        st.session_state.product_name = product_name
        st.session_state.category = category
        st.session_state.csv_files = csv_files
        st.session_state.pdf_files = pdf_files
        st.session_state.current_step = 'analysis'
        st.rerun()

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
                    st.session_state.csv_files, 
                    st.session_state.product_name
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
                        st.session_state.current_step = 'input'
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
            
            # 그래프 실행
            st.subheader("🔄 초안 작성")
            
            try:
                builder = build_graph()
                result = builder.invoke({
                    'product_name': st.session_state.product_name,
                    'category': st.session_state.category,
                    'data': raw_df, 
                    'product_docs': product_docs,
                    'product_information': product_information
                })
                
                # 결과를 session state에 저장
                st.session_state.graph_result = result
                st.session_state.analysis_started = True
                st.session_state.current_step = 'feedback'
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ 분석 중 오류 발생: {str(e)}")
                if st.button("다시 시도"):
                    st.session_state.current_step = 'input'
                    st.session_state.analysis_started = False
                    st.rerun()

def show_feedback_form():
    """피드백 입력 폼 표시"""
    if 'graph_result' not in st.session_state:
        st.error("분석 결과를 찾을 수 없습니다.")
        if st.button("처음으로"):
            st.session_state.current_step = 'input'
            st.rerun()
        return
    
    result = st.session_state.graph_result
    
    # 결과 표시
    st.write("=== 결과물 출력 ===")
    
    if 'title' in result:
        st.write(f'**Title:**\n{result["title"]}')
    
    if 'bp' in result:
        st.write('**BP:**')
        for bp in result['bp']:
            st.write(f"• {bp}")
    
    if 'description' in result:
        st.write(f'**Description:**\n{result["description"]}')
    
    st.divider()
    
    # 피드백 입력
    user_feedback = st.text_area(
        '### 사용자 피드백을 입력해 주세요. ###',
        height=150,
        help="결과에 대한 피드백을 입력하시면 개선된 결과를 제공해드립니다."
    )
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button('피드백 제출', type="primary"):
            if user_feedback.strip():
                # 피드백을 포함하여 그래프 재실행
                with st.spinner("피드백을 반영하여 결과를 개선하고 있습니다..."):
                    try:
                        builder = build_graph()
                        # 피드백을 포함한 새로운 실행
                        updated_result = builder.invoke({
                            **st.session_state.graph_result,
                            'user_feedback': user_feedback.strip(),
                            'status': 'ONGOING'
                        })
                        st.session_state.graph_result = updated_result
                        st.success("✅ 피드백이 반영되었습니다!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 피드백 처리 중 오류: {str(e)}")
            else:
                st.warning('피드백을 입력해주세요.')
    
    with col2:
        if st.button('완료'):
            st.session_state.current_step = 'complete'
            st.rerun()
    
    with col3:
        if st.button('처음으로'):
            st.session_state.current_step = 'input'
            st.session_state.analysis_started = False
            st.session_state.graph_result = None
            st.rerun()

def show_final_results():
    """최종 결과 표시"""
    st.success("🎉 분석이 완료되었습니다!")
    
    if 'graph_result' in st.session_state:
        result = st.session_state.graph_result
        
        st.write("=== 최종 결과 ===")
        
        if 'title' in result:
            st.write(f'**Title:**\n{result["title"]}')
        
        if 'bp' in result:
            st.write('**BP:**')
            for bp in result['bp']:
                st.write(f"• {bp}")
        
        if 'description' in result:
            st.write(f'**Description:**\n{result["description"]}')
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button('새로운 분석 시작', type="primary"):
            # 모든 상태 초기화
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    with col2:
        # 결과 다운로드 기능 (선택사항)
        if 'graph_result' in st.session_state:
            result_text = f"""
상품 분석 결과

상품명: {st.session_state.get('product_name', 'N/A')}
카테고리: {st.session_state.get('category', 'N/A')}

Title:
{st.session_state.graph_result.get('title', 'N/A')}

BP:
{chr(10).join(f'• {bp}' for bp in st.session_state.graph_result.get('bp', []))}

Description:
{st.session_state.graph_result.get('description', 'N/A')}
            """
            st.download_button(
                "결과 다운로드",
                result_text,
                file_name="product_analysis_result.txt",
                mime="text/plain"
            )

if __name__ == "__main__":
    main()