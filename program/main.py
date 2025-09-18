from dotenv import load_dotenv
from models.builder import build_graph
from data_loader import load_csv

load_dotenv()

def main():
    # 데이터 로드
    print('형식에 맞는 CSV 파일 검색 중...')
    
    raw_df, file = load_csv()

    if raw_df is None:
        print("형식에 맞는 CSV 파일이 없습니다.")    
        return
    
    print("읽은 파일:", file)

    # 그래프 실행
    graph = build_graph()
    final_state = graph.invoke({
        'data': raw_df, 
        'product_name': input('product name: '),
        'category': input('category: '),
        'product_description': input('product description: ')
    })

    # 결과 생성
    print('결과 생성을 완료했습니다')
    print(f'Title: {len(final_state['title'])}자\n{final_state['title']}')
    for bp in final_state['bp']:
        print(f'BP: {len(bp)}자\n{bp}')
    print(f'Description: {len(final_state['description'])}자\n{final_state['description']}')

if __name__ == "__main__":
    main()