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
        
        # 샘플 데이터 표시

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
        # 분석 실행
        with st.spinner("🔍 데이터를 로드하고 분석 중입니다..."):
            # 입력 정보 표시
            st.subheader("📋 분석 정보")
            info_col1, info_col2 = st.columns(2)
            
            with info_col1:
                st.metric("상품명", product_name)
            
            with info_col2:
                st.metric("카테고리", category)
            
            st.divider()
            
            # 데이터 로드
            st.subheader("📂 데이터 로딩")
            
            with st.status("데이터 로딩 중...", expanded=True) as status:
                # CSV 파일 로드
                st.write("키워드 CSV 파일 처리 중...")
                raw_df, csv_messages, good_csv_files = load_keywords_csv_streamlit(csv_files, product_name)
                
                # CSV 처리 결과 표시
                if raw_df:
                    st.success(f"✅ 키워드 데이터 로드 완료 ({len(raw_df)} rows)")
                    st.write(f"처리된 파일: {', '.join(good_csv_files)}")
                else:
                    st.error("❌ 키워드 데이터 로드 실패")
                    for msg in csv_messages:
                        st.write(msg)
                    return
                
                # PDF 파일 로드
                st.write("상품 정보 PDF 파일 처리 중...")
                product_docs, product_information, pdf_messages = load_information_pdf_streamlit(pdf_files)
                
                # PDF 처리 결과 표시
                if product_docs:
                    st.success(f"✅ 상품 정보 로드 완료 ({len(product_docs)}개 문서)")
                else:
                    st.warning("⚠️ PDF 파일 처리 결과")

                status.update(label="데이터 로딩 완료!", state="complete", expanded=False)
            
                # 그래프 실행
            st.subheader("🔄 초안 작성")

            builder = build_graph()
            builder.invoke({
                'product_name': product_name,
                'category': category,
                'data': raw_df, 
                'product_docs': product_docs,
                'product_information': product_information
            })

if __name__ == "__main__":
    main()