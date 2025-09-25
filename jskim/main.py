import os
from dotenv import load_dotenv
from graph.builder import build_graph
from utils.data_loader import load_keywords_csv, load_information_pdf

load_dotenv()

def main():
    # 데이터 로드
    print('@@@ 프로그램 설명, 약관이 들어갈 곳 @@@')

    # Input Variables
    product_name = input('\n상품명: ')
    category = input('\n상품의 카테고리를 적어주세요: ')

    # 되돌리기
    while category in ['/return']:
        product_name = input('\n상품명: ')
        category = input('\n상품의 카테고리를 적어주세요: ')
    
    raw_df = load_keywords_csv(product_name)
    product_docs, product_information = load_information_pdf()

    # 그래프 실행
    graph = build_graph()
    graph.invoke({
        'product_name': product_name,
        'category': category,
        'data': raw_df, 
        'product_docs': product_docs,
        'product_information': product_information
    })

if __name__ == "__main__":
    main()