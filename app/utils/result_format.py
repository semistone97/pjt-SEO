import streamlit as st

def result_format():

    result_template_1 = '''
[AI 기반 아마존 리스팅 최적화 결과]

상품명: {product_name}
카테고리: {category}
    '''

    result_template_2 = '''
피드백 반영 횟수: {feedback_count}
{feedback_history}
    '''

    result_template_3 = '''

[Title] - {title_length}자

{title}

[Bullet Points] - {bp_length}자

{bp}

[Description] - {description_length}자

{description}

[미사용 키워드]

{leftovers}
    '''

    title = st.session_state.initial_result.get('title', 'N/A')
    bps = st.session_state.initial_result.get('bp', [])

    bp_length = []
    for bp in bps:
        bp_length.append(str(len(bp)))

    description = st.session_state.initial_result.get('description', 'N/A')

    result_text_1 = result_template_1.format(
        product_name=st.session_state.get('product_name', 'N/A'),
        category=st.session_state.get('category', 'N/A'),
    )

    result_text_3 = result_template_3.format(
        title_length=len(title),
        title=title,
        
        bp=chr(10).join(f'{i}. {bp}' for i, bp in enumerate(bps, 1)),
        bp_length=', '.join(bp_length),
        
        description_length=len(description),
        description=description,
        
        leftovers = ", ".join(
            st.session_state.initial_result.get('leftover', []) + 
            st.session_state.initial_result.get('backend_keywords', [])
        )
    )

    feedback_history_text = ""

    if st.session_state.feedback_history:
        feedback_history_text = "\n반영된 피드백 내역:\n"
        for i, feedback in enumerate(st.session_state.feedback_history, 1):
            feedback_history_text += f"{i}. {feedback}\n"
        
        result_text_2 = result_template_2.format(
            feedback_count=st.session_state.get('feedback_count', 0),
            feedback_history=feedback_history_text,
        )

        return result_text_1 + result_text_2 + result_text_3

    return result_text_1 + result_text_3