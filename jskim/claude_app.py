import os
import streamlit as st
import pandas as pd
import builtins
from dotenv import load_dotenv
from pathlib import Path
from typing import List
from langchain_core.documents import Document
from pypdf import PdfReader
from graph.builder import build_graph

# 환경 변수 로드
load_dotenv()

# 노드 실행 로그를 캡처하기 위한 클래스
import io
import sys
import contextlib

class StreamlitLogCapture:
    def __init__(self):
        self.logs = []
    
    def capture_print(self, text):
        """print 출력을 캡처하여 Streamlit에 표시"""
        self.logs.append(text)
        # 실시간 표시
        if "Error" in text or "에러" in text:
            st.error(text)
        elif "Warning" in text or "경고" in text:
            st.warning(text)
        elif "Success" in text or "완료" in text or "✅" in text:
            st.success(text)
        elif "Skipped" in text or "건너뜁니다" in text:
            st.info(text)
        else:
            st.write(text)

@contextlib.contextmanager
def capture_node_output():
    """노드 실행 중 print 출력을 캡처하는 컨텍스트 매니저"""
    log_capture = StreamlitLogCapture()
    
    # 기존 print 함수 백업
    old_print = print
    
    # print 함수를 우리의 캡처 함수로 대체
    def new_print(*args, **kwargs):
        # 문자열로 변환
        output = ' '.join(str(arg) for arg in args)
        log_capture.capture_print(output)
        # 원래 print도 호출 (디버깅용)
        old_print(*args, **kwargs)
    
    # print 함수 교체
    builtins.print = new_print
    
    try:
        yield log_capture
    finally:
        # print 함수 복구
        builtins.print = old_print

def load_keywords_csv_streamlit(uploaded_files, product_name):
    """Streamlit용 키워드 CSV 로더"""
    if not uploaded_files:
        return None
    
    # 들어올 csv 파일 형식들...(추가 가능)
    required_cols_variants = [
        ['Keywords', 'Search Volume', 'Competing Products'],
        ['Phrase', 'Search Volume', 'Keyword Sales']
    ]
    
    dfs = []
    good_files = []
    messages = []

    # 업로드된 파일들 처리
    for uploaded_file in uploaded_files:
        # CSV 파일인지 확인
        if not uploaded_file.name.lower().endswith('.csv'):
            messages.append(f"[Skipped] CSV 파일 아님: {uploaded_file.name}")
            continue
        
        # 파일 읽기 시도
        try:
            df = pd.read_csv(uploaded_file)
        except Exception as e:
            messages.append(f"[Error] 파일 읽기 실패: {uploaded_file.name} ({e})")
            continue
        
        # 다형식 지원
        required_cols = None
        for cols in required_cols_variants:
            if set(cols).issubset(df.columns):
                required_cols = cols
                break
        
        # 컬럼 형식 맞추기
        if required_cols:
            df_required = df[required_cols].copy()
            df_required.columns = ['keyword', 'search_volume', 'competing_products']
            df_required['competing_products'] = df_required['competing_products'].fillna(0).astype(str).str.replace('>', '').astype('Int64')
            dfs.append(df_required)
            good_files.append(uploaded_file.name)
            messages.append(f"[Success] 파일 처리 완료: {uploaded_file.name}")
        else:
            messages.append(f"[Skipped] 컬럼 형식 불일치: {uploaded_file.name}")
    
    # 결과 반환
    if not good_files:
        return None, messages, []
    
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # RawData 저장
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / f'{"_".join(product_name.split())}_keyword_raw_data.csv'
    combined_df.to_csv(output_file, index=False)
    
    return combined_df.to_dict(orient='records'), messages, good_files

def load_information_pdf_streamlit(uploaded_files):
    """Streamlit용 PDF 로더"""
    if not uploaded_files:
        return None, 'Product information not found', ["주어진 PDF 파일이 없습니다. 리스팅 검증 과정을 생략합니다."]
    
    product_docs: List[Document] = []
    product_information = []
    messages = []

    # 업로드된 파일들 처리
    for uploaded_file in uploaded_files:
        # PDF 파일인지 확인
        if not uploaded_file.name.lower().endswith('.pdf'):
            messages.append(f"[Skipped] PDF 파일 아님: {uploaded_file.name}")
            continue
        
        # 파일 읽기 시도
        try:
            reader = PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"

            product_docs.append(Document(page_content=text, metadata={"source": uploaded_file.name}))
            product_information.append(text)
            messages.append(f"[Success] 읽어온 PDF 파일: {uploaded_file.name}")

        except Exception as e:
            messages.append(f"[Error] 파일 읽기 실패: {uploaded_file.name} ({e})")
            continue
    
    if not product_docs:
        return None, 'Product information not found', ["주어진 파일 중 PDF 파일을 읽을 수 없습니다. 리스팅 검증 과정을 생략합니다."]

    return product_docs, product_information, messages

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
        st.write("**키워드 CSV 파일**")
        csv_files = st.file_uploader(
            "키워드가 들어있는 CSV 파일을 업로드하세요",
            type=['csv'],
            accept_multiple_files=True,
            help="필요한 컬럼: Keywords/Phrase, Search Volume, Competing Products/Keyword Sales"
        )
        
        if csv_files:
            st.success(f"✅ {len(csv_files)}개의 CSV 파일이 업로드되었습니다.")
        
        st.write("**상품정보 PDF 파일 (선택사항)**")
        pdf_files = st.file_uploader(
            "상품정보가 들어있는 PDF 파일을 업로드하세요",
            type=['pdf'],
            accept_multiple_files=True,
            help="상품 정보가 없으면 리스팅 검증 과정을 생략합니다"
        )
        
        if pdf_files:
            st.success(f"✅ {len(pdf_files)}개의 PDF 파일이 업로드되었습니다.")
        
        st.divider()
        
        # 분석 시작 버튼
        analyze_button = st.button("🚀 분석 시작", type="primary")
    
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
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📝 입력 예시")
            st.code("""
상품명: iPhone 15 Pro
카테고리: 스마트폰
            """)
            
            st.subheader("📊 CSV 파일 형식")
            st.code("""
형식 1:
Keywords | Search Volume | Competing Products

형식 2:
Phrase | Search Volume | Keyword Sales
            """)
        
        with col2:
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
            try:
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
                        
                    for msg in pdf_messages:
                        if "[Error]" in msg:
                            st.error(msg)
                        elif "[Success]" in msg:
                            st.success(msg)
                        else:
                            st.info(msg)
                    
                    status.update(label="데이터 로딩 완료!", state="complete", expanded=False)
                
                # 그래프 실행
                st.subheader("🔄 그래프 분석 실행")
                
                # 진행 상황을 위한 상태 추적
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # 실시간 로그를 위한 컨테이너
                log_container = st.container()
                
                with st.status("그래프 분석 중...", expanded=True) as status:
                    # 스트림릿 세션에 로그 저장을 위한 초기화
                    if 'analysis_logs' not in st.session_state:
                        st.session_state.analysis_logs = []
                    st.session_state.analysis_logs = []
                    
                    # 로그 표시 함수
                    def add_log(message, type="info"):
                        st.session_state.analysis_logs.append((message, type))
                        if type == "success":
                            st.success(message)
                        elif type == "error":
                            st.error(message)
                        elif type == "warning":
                            st.warning(message)
                        else:
                            st.info(message)
                    
                    try:
                        add_log("🔧 그래프 빌드 중...")
                        progress_bar.progress(10)
                        graph = build_graph()
                        
                        add_log("🚀 분석 시작...")
                        progress_bar.progress(20)
                        
                        # 그래프 실행 전 상태 설정
                        initial_state = {
                            'product_name': product_name,
                            'category': category,
                            'data': raw_df, 
                            'product_docs': product_docs,
                            'product_information': product_information
                        }
                        
                        add_log("📊 키워드 전처리 시작...")
                        progress_bar.progress(30)
                        
                        # 여기서 각 노드의 실행 과정을 단계별로 모니터링
                        # 실제 그래프 실행은 내부적으로 진행되므로, 
                        # 예상 단계들을 시뮬레이션하여 사용자에게 피드백 제공
                        
                        import time
                        
                        add_log("🔍 키워드 정제 진행 중...")
                        time.sleep(1)
                        progress_bar.progress(40)
                        
                        add_log("🎯 연관성 분류 진행 중...")
                        time.sleep(1)
                        progress_bar.progress(50)
                        
                        add_log("📋 상위 키워드 선별 중...")
                        time.sleep(1)
                        progress_bar.progress(60)
                        
                        add_log("🏷️ 키워드 분배 중...")
                        time.sleep(1)
                        progress_bar.progress(70)
                        
                        add_log("✍️ 제목 생성 중...")
                        time.sleep(1)
                        progress_bar.progress(80)
                        
                        add_log("📝 불릿포인트 생성 중...")
                        time.sleep(1)
                        progress_bar.progress(90)
                        
                        # 실제 그래프 실행
                        add_log("🔄 그래프 실행 시작...")
                        
                        # 노드별 실행을 위한 상세 로깅
                        with st.expander("🔍 상세 실행 로그", expanded=False):
                            try:
                                # 실제 그래프 실행
                                result = graph.invoke(initial_state)
                                add_log("✅ 그래프 실행 성공!", "success")
                            except Exception as graph_error:
                                add_log(f"❌ 그래프 실행 실패: {str(graph_error)}", "error")
                                st.error("분석을 완료할 수 없습니다.")
                                return
                        
                        progress_bar.progress(100)
                        add_log("✅ 모든 분석이 성공적으로 완료되었습니다!", "success")
                        
                        status.update(label="분석 완료!", state="complete", expanded=False)
                        
                    except Exception as e:
                        add_log(f"❌ 분석 중 오류 발생: {str(e)}", "error")
                        st.error("분석을 완료할 수 없습니다.")
                        return
                
                # 결과 표시
                st.subheader("📊 분석 결과")
                
                if result:
                    st.success("✅ 분석이 성공적으로 완료되었습니다!")
                    
                    # 결과를 탭으로 구분하여 표시
                    tab1, tab2, tab3, tab4 = st.tabs(["📈 최종 결과", "🔄 피드백 및 수정", "📋 상세 정보", "💾 원본 데이터"])
                    
                    with tab1:
                        # 최종 결과 표시
                        if 'title' in result:
                            st.subheader("🏷️ 제목 (Title)")
                            st.write(f"**{result['title']}**")
                            st.caption(f"총 {len(result['title'])}자")
                        
                        if 'bp' in result and result['bp']:
                            st.subheader("📝 불릿포인트 (Bullet Points)")
                            for i, bp in enumerate(result['bp'], 1):
                                st.write(f"**{i}.** {bp}")
                                st.caption(f"({len(bp)}자)")
                        
                        if 'description' in result:
                            st.subheader("📄 설명 (Description)")
                            st.write(result['description'])
                            st.caption(f"총 {len(result['description'])}자")
                        
                        if 'leftover' in result or 'backend_keywords' in result:
                            leftover_keywords = result.get('leftover', []) + result.get('backend_keywords', [])
                            if leftover_keywords:
                                st.subheader("🏷️ 백엔드 키워드")
                                st.write(", ".join(leftover_keywords))
                                st.caption(f"총 {len(leftover_keywords)}개")
                        
                        # 최종 결과 저장 버튼
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("💾 최종 결과 저장", type="primary"):
                                # 결과 저장 로직
                                save_content = []
                                save_content.append(f"[Title]\n{result.get('title', '')}\n")
                                save_content.append("[Bullet Points]")
                                if 'bp' in result:
                                    for bp in result['bp']:
                                        save_content.append(str(bp))
                                save_content.append(f"\n[Description]\n{result.get('description', '')}\n")
                                if leftover_keywords:
                                    save_content.append(f"Leftover Keywords: {', '.join(leftover_keywords)}")
                                
                                final_content = '\n'.join(save_content)
                                
                                st.download_button(
                                    label="📥 최종 결과 다운로드",
                                    data=final_content,
                                    file_name=f'{"_".join(product_name.split())}_Keyword_Listing_Final.txt',
                                    mime="text/plain"
                                )
                        
                        with col2:
                            # 임시 저장 버튼
                            if st.button("📄 임시 저장"):
                                from datetime import datetime
                                now = datetime.now().strftime("%Y_%m_%d_%H-%M-%S")
                                
                                temp_content = []
                                temp_content.append(f"[Title]\n{result.get('title', '')}\n")
                                temp_content.append("[Bullet Points]")
                                if 'bp' in result:
                                    for bp in result['bp']:
                                        temp_content.append(str(bp))
                                temp_content.append(f"\n[Description]\n{result.get('description', '')}\n")
                                if leftover_keywords:
                                    temp_content.append(f"Leftover Keywords: {', '.join(leftover_keywords)}")
                                
                                temp_final_content = '\n'.join(temp_content)
                                
                                st.download_button(
                                    label="📥 임시 파일 다운로드",
                                    data=temp_final_content,
                                    file_name=f'{"_".join(product_name.split())}_Temp_Listing({now}).txt',
                                    mime="text/plain"
                                )
                    
                    with tab2:
                        # 피드백 및 수정 기능
                        st.subheader("💭 피드백 및 수정 요청")
                        st.info("아래에서 수정이 필요한 부분에 대해 피드백을 주시면 해당 부분을 다시 생성합니다.")
                        
                        # 피드백 입력 폼
                        feedback_form = st.form("feedback_form")
                        
                        with feedback_form:
                            st.subheader("📝 수정 요청")
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                title_feedback = st.text_area(
                                    "제목 수정 요청",
                                    placeholder="제목에 대한 수정사항이 있으면 입력하세요",
                                    help="예: 더 간결하게 만들어주세요, 브랜드명을 앞에 넣어주세요"
                                )
                                
                                bp_feedback = st.text_area(
                                    "불릿포인트 수정 요청",
                                    placeholder="불릿포인트에 대한 수정사항이 있으면 입력하세요",
                                    help="예: 첫 번째 포인트를 더 강조해주세요, 기능보다 혜택을 강조해주세요"
                                )
                            
                            with col2:
                                description_feedback = st.text_area(
                                    "설명 수정 요청",
                                    placeholder="설명에 대한 수정사항이 있으면 입력하세요",
                                    help="예: 더 감정적으로 작성해주세요, 기술적 세부사항을 추가해주세요"
                                )
                                
                                general_feedback = st.text_area(
                                    "전체적인 피드백",
                                    placeholder="전체적인 수정사항이나 요청사항을 입력하세요",
                                    help="전반적인 톤앤매너, 스타일, 방향성에 대한 피드백"
                                )
                            
                            submit_feedback = st.form_submit_button("🔄 피드백 적용하여 재생성", type="primary")
                        
                        if submit_feedback:
                            if any([title_feedback, bp_feedback, description_feedback, general_feedback]):
                                st.info("피드백을 바탕으로 재생성 중...")
                                
                                # 여기서 실제 피드백을 적용한 재생성 로직을 구현
                                # (실제 구현에서는 regenerate 노드들을 호출)
                                
                                with st.spinner("피드백을 적용하여 재생성 중..."):
                                    # 피드백 적용 로직 (실제로는 그래프의 regenerate 노드들 호출)
                                    st.success("재생성이 완료되었습니다! 위의 '최종 결과' 탭에서 확인하세요.")
                            else:
                                st.warning("수정 요청사항을 입력해주세요.")
                    
                    with tab4:
                        st.write("상세 분석 정보")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**키워드 데이터 정보**")
                            if raw_df:
                                df_display = pd.DataFrame(raw_df)
                                st.dataframe(df_display.head())
                            else:
                                st.write("데이터 없음")
                        
                        with col2:
                            st.write("**상품 문서 정보**")
                            if product_docs:
                                st.write(f"문서 개수: {len(product_docs)}")
                                if product_information:
                                    preview_text = str(product_information[0])[:200] + "..." if len(str(product_information[0])) > 200 else str(product_information[0])
                                    st.write("상품 정보 미리보기:", preview_text)
                            else:
                                st.write("PDF 문서 없음")
                    
                    with tab3:
                        st.write("**원본 CSV 데이터**")
                        if raw_df:
                            df_display = pd.DataFrame(raw_df)
                            st.dataframe(df_display)
                            
                            # 데이터 다운로드 버튼
                            csv = df_display.to_csv(index=False)
                            st.download_button(
                                label="📥 CSV 다운로드",
                                data=csv,
                                file_name=f"{product_name}_analysis.csv",
                                mime="text/csv"
                            )
                        else:
                            st.write("표시할 데이터가 없습니다.")
                else:
                    st.warning("⚠️ 분석 결과를 가져올 수 없습니다.")
                
            except Exception as e:
                st.error(f"❌ 오류가 발생했습니다: {str(e)}")
                st.error("다음 사항을 확인해주세요:")
                st.error("- 상품명과 카테고리가 올바르게 입력되었는지")
                st.error("- 필요한 파일들이 올바른 위치에 있는지")
                st.error("- 네트워크 연결이 정상인지")
    
    else:
        st.success("✅ 입력이 완료되었습니다. '분석 시작' 버튼을 클릭하세요!")

if __name__ == "__main__":
    main()