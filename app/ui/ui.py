import streamlit as st
from graph.builder_st import build_initial_graph, build_feedback_graph
from utils.data_loader_st import load_information_pdf_streamlit, load_keywords_csv_streamlit


def show_sidebar():
    """모든 단계에서 공통으로 표시되는 사이드바"""
    with st.sidebar:
        st.header("🔧 설정")
        
        # 현재 단계 표시
        step_emoji = {
            'input': '📝',
            'analysis': '⚙️',
            'feedback': '💬',
            'complete': '✅'
        }
        current_emoji = step_emoji.get(st.session_state.current_step, '📝')
        st.info(f"{current_emoji} 현재 단계: {st.session_state.current_step.upper()}")
        
        st.divider()
        
        # 사이드바 메인 컨텐츠를 컨테이너로 관리
        sidebar_container = st.empty()
        
        with sidebar_container.container():
            # 입력 단계에서만 파일 업로드 허용
            if st.session_state.current_step == 'input':
                # 상품명 입력
                product_name = st.text_input(
                    "상품명",
                    value=getattr(st.session_state, 'product_name', ''),
                    placeholder="분석하고 싶은 상품명을 입력하세요",
                    help="정확한 상품명을 입력하면 더 정확한 분석이 가능합니다",
                    key="sidebar_product_name"
                )
                
                # 카테고리 입력
                categories = [
                    "Amazon Devices & Accessories",
                    "Amazon Renewed",
                    "Appliances",
                    "Apps & Games",
                    "Arts, Crafts & Sewing",
                    "Audible Books & Originals",
                    "Automotive",
                    "Baby",
                    "Beauty & Personal Care",
                    "Books",
                    "Camera & Photo Products",
                    "CDs & Vinyl",
                    "Cell Phones & Accessories",
                    "Clothing, Shoes & Jewelry",
                    "Collectible Coins",
                    "Computers & Accessories",
                    "Digital Educational Resources",
                    "Digital Music",
                    "Electronics",
                    "Entertainment Collectibles",
                    "Gift Cards",
                    "Grocery & Gourmet Food",
                    "Handmade Products",
                    "Health & Household",
                    "Home & Kitchen",
                    "Industrial & Scientific",
                    "Kindle Store",
                    "Kitchen & Dining",
                    "Movies & TV",
                    "Musical Instruments",
                    "Office Products",
                    "Patio, Lawn & Garden",
                    "Pet Supplies",
                    "Software",
                    "Sports & Outdoors",
                    "Sports Collectibles",
                    "Tools & Home Improvement",
                    "Toys & Games",
                    "Unique Finds",
                    "Video Games"
                ]

                placeholder = "카테고리 선택"
                dropdown_options = [placeholder] + categories
                current_value = getattr(st.session_state, 'category', placeholder)

                selected = st.selectbox(
                    "상품 카테고리",
                    options=dropdown_options,
                    index=dropdown_options.index(current_value) if current_value in dropdown_options else 0
                )

                if selected != placeholder:
                    st.session_state.category = selected

                category = st.session_state.get('category', None)

                # 파일 업로드 섹션
                st.subheader("📁 파일 업로드")
                
                # CSV 파일 업로드
                csv_files = st.file_uploader(
                    "키워드 CSV 파일",
                    type=['csv'],
                    accept_multiple_files=True,
                    help="필요한 컬럼: Keywords/Phrase, Search Volume, Competing Products/Keyword Sales",
                    key="sidebar_csv_files"
                )
                
                if csv_files:
                    st.success(f"✅ {len(csv_files)}개의 CSV 파일이 업로드되었습니다.")
                
                pdf_files = st.file_uploader(
                    "상품정보 PDF 파일 (선택사항)",
                    type=['pdf'],
                    accept_multiple_files=True,
                    help="상품 정보가 없으면 리스팅 검증 과정을 생략합니다",
                    key="sidebar_pdf_files"
                )
                
                if pdf_files:
                    st.success(f"✅ {len(pdf_files)}개의 PDF 파일이 업로드되었습니다.")
                
                # 실시간으로 세션 상태 업데이트
                st.session_state.product_name = product_name
                st.session_state.category = category
                st.session_state.csv_files = csv_files
                st.session_state.pdf_files = pdf_files
                
            else:
                # 다른 단계에서는 현재 설정 정보만 표시
                if hasattr(st.session_state, 'product_name'):
                    st.subheader("📋 현재 설정")
                    st.write(f"상품명: {st.session_state.product_name}")
                    st.write(f"카테고리: {st.session_state.category}")
                    
                    if hasattr(st.session_state, 'csv_files'):
                        st.write(f"CSV 파일: {len(st.session_state.csv_files)}개")
                    
                    if hasattr(st.session_state, 'pdf_files') and st.session_state.pdf_files:
                        st.write(f"PDF 파일: {len(st.session_state.pdf_files)}개")
                    
                    if hasattr(st.session_state, 'feedback_count') and st.session_state.feedback_count > 0:
                        st.write(f"피드백 반영: {st.session_state.feedback_count}회")
            
            st.divider()
            
            # 단계 이동 버튼들
            
            if st.button("🏠 처음으로", use_container_width=True, key="sidebar_home"):
                # 모든 상태 초기화
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
            
            
def show_input_form():
    """초기 입력 폼 표시 """
    # 메인 컨텐츠 영역을 컨테이너로 관리
    main_container = st.empty()
    
    with main_container.container():
        # 요구사항 체크
        requirements = []
        if not getattr(st.session_state, 'product_name', None):
            requirements.append("✗ 상품명")
        else:
            requirements.append("✓ 상품명")

        if not getattr(st.session_state, 'category', None):
            requirements.append("✗ 카테고리")
        else:
            requirements.append("✓ 카테고리")

        if not getattr(st.session_state, 'csv_files', None):
            requirements.append("✗ CSV 파일")
        else:
            requirements.append("✓ CSV 파일")

        st.info("사이드바에서 다음 항목들을 완성하고 '분석 시작' 버튼을 클릭하세요:")
        for req in requirements:
            st.write(req)

        st.divider()

        # 업로드된 파일 표시
        st.subheader("업로드된 파일")
        if getattr(st.session_state, 'csv_files', None):
            st.write("CSV 파일:")
            for file in st.session_state.csv_files:
                st.write(f"- {file.name}")

        if getattr(st.session_state, 'pdf_files', None):
            st.write("PDF 파일:")
            for file in st.session_state.pdf_files:
                st.write(f"- {file.name}")

        if (not getattr(st.session_state, 'csv_files', None) and 
            not getattr(st.session_state, 'pdf_files', None)):
            st.info("파일이 업로드되지 않았습니다.")

        # 모든 조건 충족 시 성공 메시지 및 버튼 표시
        if (getattr(st.session_state, 'product_name', None) and
            getattr(st.session_state, 'category', None) and
            getattr(st.session_state, 'csv_files', None)):
            st.success("모든 정보가 입력되었습니다. '분석 시작' 버튼을 클릭해주세요.")
            analyze_button = st.button("분석 시작", type="primary", key="analyze_button")
            if analyze_button:
                # 버튼 클릭 시 즉시 컨테이너 제거하고 다음 단계로
                main_container.empty()
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
    
    main_container = st.empty()
    with main_container.container():
        if 'initial_result' not in st.session_state or st.session_state.initial_result is None:
            st.error("분석 결과를 찾을 수 없습니다.")
            if st.button("재시작"):
                st.session_state.current_step = 'input'
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
                st.session_state.current_step = 'complete'
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

[Title]
{st.session_state.initial_result.get('title', 'N/A')}

[Bullet Points]
{chr(10).join(f'{i}. {bp}' for i, bp in enumerate(st.session_state.initial_result.get('bp', []), 1))}

[Description]
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
