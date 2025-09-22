import os
from dotenv import load_dotenv
from graph.builder import build_graph
from utils.data_loader import load_csv

load_dotenv()

def main():
    # 데이터 로드
    print('@@@ 프로그램 설명, 약관이 들어갈 곳 @@@')

    # Input Variables
    product_name = 'chicken shredder'
    # product_name = input('\n상품명: ')
    
    raw_df = load_csv(product_name)

    # 그래프 실행
    graph = build_graph()
    final_state = graph.invoke({
        'data': raw_df, 
        'product_name': product_name,
        'category': 'Home & Kitchen',
        'product_information': 'multipurpose meat shredder'
        # 'category': input('상품의 카테고리를 적어주세요: '),
        # 'product_information': input('상품의 크기, 소재 관련 데이터를 적어주세요: ')
    })

    save_dir = 'output'
    os.makedirs(save_dir, exist_ok=True)
    filename = f'{"_".join(product_name.split())}_Keyword_Listing_Final.txt'
    file_path = os.path.join(save_dir, filename)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f'\n[Title]\n{final_state.get('title')}\n')
        f.write('\n[Bullet Point]\n')
        for bp in final_state.get('bp'):
            f.write(str(bp) + '\n')
        f.write(f'\n[Description]\n{final_state.get('description')}\n')
        f.write('\nLeftover Keywords: ' + ', '.join(map(str, sorted(final_state.get('leftover') + final_state.get('backend_keywords')))))
                
        print(f'최종 결과물을 {filename} 파일에 저장합니다. ')

if __name__ == "__main__":
    main()