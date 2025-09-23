from typing import List
from schemas.global_state import State
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


verification_template_system ="""
You are an expert content verifier for Amazon product listings. 
Your task is to meticulously cross-verify the given 'Content to Verify' against the provided 'Factual Product Information'.
Your goal is to ensure the content is 100% accurate and factually consistent with the product information.

- Correct any discrepancies or inaccuracies in the 'Content to Verify'.
- Enhance the content with crucial details from the 'Factual Product Information' if they are missing.
- Return ONLY the corrected and verified content as a raw string. Do not add any introductory text, explanations, or markdown formatting like .
- If the 'Content to Verify' is a list of bullet points, maintain the list structure by separating each point with a newline character."),
"""

verification_template_human = """
[Factual Product Information]
{product_information}

[Content to Verify - {content_type}]
{content_to_verify}
"""

# 각 콘텐츠(title, bp, description)를 개별적으로 검증하기 위한 새로운 프롬프트
VERIFICATION_PROMPT_V2 = ChatPromptTemplate.from_messages([
        ('system', verification_template_system),
        ('human', verification_template_human)
    ])

def listing_verificate_v2(state: State) -> dict:
    """
    Verifies and corrects the title, bullet points, and description separately based on product information,
    using three distinct LLM calls.

    Args:
        state (State): The current graph state.

    Returns:
        dict: A dictionary containing the verified 'title', 'bp', and 'description'.
    """
    print("---Executing Verification Node (v2) ---")

    # 1. State에서 현재 리스팅 정보와 제품 사실 정보를 올바른 방식으로 가져옵니다.
    current_title = state["title"]
    current_bp = state["bp"]
    current_description = state["description"]
    product_information = state["product_information"]

    # 2. LLM을 초기화하고 검증 체인을 생성합니다.
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    verification_chain = VERIFICATION_PROMPT_V2 | llm

    # 3. API 호출 1: Title 검증
    print("Verifying Title...")
    title_response = verification_chain.invoke({
        "product_information": product_information,
        "content_type": "Title",
        "content_to_verify": current_title
    })
    verified_title = title_response.content

    # 4. API 호출 2: Bullet Points 검증
    print("Verifying Bullet Points...")
    bp_as_string = "\n".join(current_bp)
    bp_response = verification_chain.invoke({
        "product_information": product_information,
        "content_type": "Bullet Points",
        "content_to_verify": bp_as_string
    })
    # LLM의 문자열 응답을 다시 리스트 형태로 변환합니다.
    verified_bp = bp_response.content.strip().split('\n')

    # 5. API 호출 3: Description 검증
    print("Verifying Description...")
    description_response = verification_chain.invoke({
        "product_information": product_information,
        "content_type": "Description",
        "content_to_verify": current_description
    })
    verified_description = description_response.content

    print("---Verification Complete (v2) ---")
    
    # 6. 검증 완료된 콘텐츠를 State 업데이트를 위해 반환합니다.
    return {
        "title": verified_title,
        "bp": verified_bp,
        "description": verified_description,
    }
