import streamlit as st
            
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
                st.session_state.current_step = '초안 생성'
                st.rerun()
