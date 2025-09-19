from langchain_core.prompts import PromptTemplate
from prompts.prompt_listing import title_prompt, bp_prompt, description_prompt

# ====================================================================================================
# 피드백 프롬프트
feedback_template = '''
사용자 피드백을 title, bp, description 관련으로 나눠서 파싱합니다.

피드백이 없으면 빈 문자열만 넣습니다.

결과는 항상 JSON 형식으로 반환합니다.

[피드백]
{user_feedback}
'''

feedback_prompt = PromptTemplate.from_template(feedback_template)
