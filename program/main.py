from dotenv import load_dotenv
from graph.builder import build_graph
from utils.data_loader import load_csv

load_dotenv()

def main():
    # 데이터 로드
    print('@@@ 프로그램 설명, 약관이 들어갈 곳 @@@')
    
    print('\n--- 형식에 맞는 CSV 파일 검색 중... ---')
    
    raw_df, file = load_csv()

    if raw_df is None:
        print("\n형식에 맞는 CSV 파일이 없습니다.")    
        return
    
    print("\n읽은 파일:", file)

    # 그래프 실행
    graph = build_graph()
    final_state = graph.invoke({
        'data': raw_df, 
        'product_name': 'iphone case',
        'category': 'smartphone case',
        'product_information': ''
        # 'product_name': input('\n상품명: '),
        # 'category': input('상품의 카테고리를 적어주세요: '),
        # 'product_information': input('상품의 크기, 소재 관련 데이터를 적어주세요: ')
    })

if __name__ == "__main__":
    main()