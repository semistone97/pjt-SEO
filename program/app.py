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
            st.subheader("🔄 그래프 분석 실행")

            graph = build_graph()
            graph.invoke({
                'product_name': product_name,
                'category': category,
                'data': raw_df, 
                'product_docs': product_docs,
                'product_information': product_information
            })



                # # 결과 표시
                # st.subheader("📊 분석 결과")
                
    #             if result:
    #                 st.success("✅ 분석이 성공적으로 완료되었습니다!")
                    
    #                 # 결과를 탭으로 구분하여 표시
    #                 tab1, tab2, tab3, tab4 = st.tabs(["📈 최종 결과", "🔄 피드백 및 수정", "📋 상세 정보", "💾 원본 데이터"])
                    
    #                 with tab1:
    #                     # 최종 결과 표시
    #                     if 'title' in result:
    #                         st.subheader("🏷️ 제목 (Title)")
    #                         st.write(f"**{result['title']}**")
    #                         st.caption(f"총 {len(result['title'])}자")
                        
    #                     if 'bp' in result and result['bp']:
    #                         st.subheader("📝 불릿포인트 (Bullet Points)")
    #                         for i, bp in enumerate(result['bp'], 1):
    #                             st.write(f"**{i}.** {bp}")
    #                             st.caption(f"({len(bp)}자)")
                        
    #                     if 'description' in result:
    #                         st.subheader("📄 설명 (Description)")
    #                         st.write(result['description'])
    #                         st.caption(f"총 {len(result['description'])}자")
                        
    #                     if 'leftover' in result or 'backend_keywords' in result:
    #                         leftover_keywords = result.get('leftover', []) + result.get('backend_keywords', [])
    #                         if leftover_keywords:
    #                             st.subheader("🏷️ 백엔드 키워드")
    #                             st.write(", ".join(leftover_keywords))
    #                             st.caption(f"총 {len(leftover_keywords)}개")
                        
    #                     # 최종 결과 저장 버튼
    #                     col1, col2 = st.columns(2)
    #                     with col1:
    #                         if st.button("💾 최종 결과 저장", type="primary"):
    #                             # 결과 저장 로직
    #                             save_content = []
    #                             save_content.append(f"[Title]\n{result.get('title', '')}\n")
    #                             save_content.append("[Bullet Points]")
    #                             if 'bp' in result:
    #                                 for bp in result['bp']:
    #                                     save_content.append(str(bp))
    #                             save_content.append(f"\n[Description]\n{result.get('description', '')}\n")
    #                             if leftover_keywords:
    #                                 save_content.append(f"Leftover Keywords: {', '.join(leftover_keywords)}")
                                
    #                             final_content = '\n'.join(save_content)
                                
    #                             st.download_button(
    #                                 label="📥 최종 결과 다운로드",
    #                                 data=final_content,
    #                                 file_name=f'{"_".join(product_name.split())}_Keyword_Listing_Final.txt',
    #                                 mime="text/plain"
    #                             )
                        
    #                     with col2:
    #                         # 임시 저장 버튼
    #                         if st.button("📄 임시 저장"):
    #                             from datetime import datetime
    #                             now = datetime.now().strftime("%Y_%m_%d_%H-%M-%S")
                                
    #                             temp_content = []
    #                             temp_content.append(f"[Title]\n{result.get('title', '')}\n")
    #                             temp_content.append("[Bullet Points]")
    #                             if 'bp' in result:
    #                                 for bp in result['bp']:
    #                                     temp_content.append(str(bp))
    #                             temp_content.append(f"\n[Description]\n{result.get('description', '')}\n")
    #                             if leftover_keywords:
    #                                 temp_content.append(f"Leftover Keywords: {', '.join(leftover_keywords)}")
                                
    #                             temp_final_content = '\n'.join(temp_content)
                                
    #                             st.download_button(
    #                                 label="📥 임시 파일 다운로드",
    #                                 data=temp_final_content,
    #                                 file_name=f'{"_".join(product_name.split())}_Temp_Listing({now}).txt',
    #                                 mime="text/plain"
    #                             )
                    
    #                 with tab2:
    #                     # 피드백 및 수정 기능
    #                     st.subheader("💭 피드백 및 수정 요청")
    #                     st.info("아래에서 수정이 필요한 부분에 대해 피드백을 주시면 해당 부분을 다시 생성합니다.")
                        
    #                     # 피드백 입력 폼
    #                     feedback_form = st.form("feedback_form")
                        
    #                     with feedback_form:
    #                         st.subheader("📝 수정 요청")
                            
    #                         col1, col2 = st.columns(2)
                            
    #                         with col1:
    #                             title_feedback = st.text_area(
    #                                 "제목 수정 요청",
    #                                 placeholder="제목에 대한 수정사항이 있으면 입력하세요",
    #                                 help="예: 더 간결하게 만들어주세요, 브랜드명을 앞에 넣어주세요"
    #                             )
                                
    #                             bp_feedback = st.text_area(
    #                                 "불릿포인트 수정 요청",
    #                                 placeholder="불릿포인트에 대한 수정사항이 있으면 입력하세요",
    #                                 help="예: 첫 번째 포인트를 더 강조해주세요, 기능보다 혜택을 강조해주세요"
    #                             )
                            
    #                         with col2:
    #                             description_feedback = st.text_area(
    #                                 "설명 수정 요청",
    #                                 placeholder="설명에 대한 수정사항이 있으면 입력하세요",
    #                                 help="예: 더 감정적으로 작성해주세요, 기술적 세부사항을 추가해주세요"
    #                             )
                                
    #                             general_feedback = st.text_area(
    #                                 "전체적인 피드백",
    #                                 placeholder="전체적인 수정사항이나 요청사항을 입력하세요",
    #                                 help="전반적인 톤앤매너, 스타일, 방향성에 대한 피드백"
    #                             )
                            
    #                         submit_feedback = st.form_submit_button("🔄 피드백 적용하여 재생성", type="primary")
                        
    #                     if submit_feedback:
    #                         if any([title_feedback, bp_feedback, description_feedback, general_feedback]):
    #                             st.info("피드백을 바탕으로 재생성 중...")
                                
    #                             # 여기서 실제 피드백을 적용한 재생성 로직을 구현
    #                             # (실제 구현에서는 regenerate 노드들을 호출)
                                
    #                             with st.spinner("피드백을 적용하여 재생성 중..."):
    #                                 # 피드백 적용 로직 (실제로는 그래프의 regenerate 노드들 호출)
    #                                 st.success("재생성이 완료되었습니다! 위의 '최종 결과' 탭에서 확인하세요.")
    #                         else:
    #                             st.warning("수정 요청사항을 입력해주세요.")
                    
    #                 with tab4:
    #                     st.write("상세 분석 정보")
    #                     col1, col2 = st.columns(2)
                        
    #                     with col1:
    #                         st.write("**키워드 데이터 정보**")
    #                         if raw_df:
    #                             df_display = pd.DataFrame(raw_df)
    #                             st.dataframe(df_display.head())
    #                         else:
    #                             st.write("데이터 없음")
                        
    #                     with col2:
    #                         st.write("**상품 문서 정보**")
    #                         if product_docs:
    #                             st.write(f"문서 개수: {len(product_docs)}")
    #                             if product_information:
    #                                 preview_text = str(product_information[0])[:200] + "..." if len(str(product_information[0])) > 200 else str(product_information[0])
    #                                 st.write("상품 정보 미리보기:", preview_text)
    #                         else:
    #                             st.write("PDF 문서 없음")
                    
    #                 with tab3:
    #                     st.write("**원본 CSV 데이터**")
    #                     if raw_df:
    #                         df_display = pd.DataFrame(raw_df)
    #                         st.dataframe(df_display)
                            
    #                         # 데이터 다운로드 버튼
    #                         csv = df_display.to_csv(index=False)
    #                         st.download_button(
    #                             label="📥 CSV 다운로드",
    #                             data=csv,
    #                             file_name=f"{product_name}_analysis.csv",
    #                             mime="text/csv"
    #                         )
    #                     else:
    #                         st.write("표시할 데이터가 없습니다.")
    #             else:
    #                 st.warning("⚠️ 분석 결과를 가져올 수 없습니다.")
                
    #         except Exception as e:
    #             st.error(f"❌ 오류가 발생했습니다: {str(e)}")
    #             st.error("다음 사항을 확인해주세요:")
    #             st.error("- 상품명과 카테고리가 올바르게 입력되었는지")
    #             st.error("- 필요한 파일들이 올바른 위치에 있는지")
    #             st.error("- 네트워크 연결이 정상인지")
    
    # else:
    #     st.success("✅ 입력이 완료되었습니다. '분석 시작' 버튼을 클릭하세요!")

if __name__ == "__main__":
    main()