import streamlit as st

def show_sidebar():
    """모든 단계에서 공통으로 표시되는 사이드바"""
    with st.sidebar:
     
        st.header('에이전트 정보')
        
        # 현재 단계 표시
        step_emoji = {
            '데이터 입력': '📝',
            '초안 생성': '⚙️',
            '피드백': '💬',
            '완료': '✅'
        }
        current_emoji = step_emoji.get(st.session_state.current_step, '📝')
        st.info(f"{current_emoji} 현재 단계: {st.session_state.current_step}")
        
        st.divider()
        
        # 사이드바 메인 컨텐츠를 컨테이너로 관리
        sidebar_container = st.empty()
        
        with sidebar_container.container():
            # 입력 단계에서만 파일 업로드 허용
            if st.session_state.current_step == '데이터 입력':
                # 상품명 입력
                st.subheader('상품 정보')
                
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
                st.subheader("파일 업로드")
                
                # CSV 파일 업로드
                csv_files = st.file_uploader(
                    "키워드 CSV 파일",
                    type=['csv'],
                    accept_multiple_files=True,
                    help="컬럼이 형식에 맞지 않을 경우, 분석할 수 없습니다",
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

                if st.button("🏠 처음으로", use_container_width=True, key="sidebar_home"):
                    # 모든 상태 초기화
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.rerun()                        
            
