from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import PromptTemplate

# ====================================================================================================
# filter_prompt

filter_template = """
다음 키워드 리스트에 대해 조건을 적용하되, 삭제는 가능한 한 신중히 수행한다:

[조건]
1. 영어 이외의 외국어 키워드 삭제 권장. 
2. 같은 키워드의 단수형과 복수형 단어가 동시에 존재할 경우에만, 복수형 키워드를 제거함 
3. 오타로 판단되는 키워드의 경우, 원본 키워드가 존재할 경우 오타 키워드를 제거함

[데이터]
{data}

[출력]
{format_instructions}
"""

filter_prompt = PromptTemplate.from_template(filter_template)


# ====================================================================================================
# relevance_prompt

relevance_template_system = '''
You are an expert in Amazon SEO and keyword analysis.
Your task is to classify the relevance of a list of keywords to a given product into one of four categories:
- 'Direct': Directly related to the product, indicating high purchase intent. Customers searching this are very likely to buy the product.
- 'Related': Related to the product's function or use case, but less specific.
- 'Indirect': Related to the broader product category or a peripheral use case, but not the product itself.
- 'NotRelated': Not relevant to the product at all.

Please return your response ONLY as a valid JSON array of objects, where each object has two keys: "keyword" and "relevance_category". Do not include any other text, explanation, or markdown.

Example format:
[
  {{"keyword": "chicken shredder", "relevance_category": "Direct"}},
  {{"keyword": "kitchen gadget", "relevance_category": "Related"}},
  {{"keyword": "wedding gift", "relevance_category": "Indirect"}},
  {{"keyword": "car accessories", "relevance_category": "NotRelated"}}
]
'''
relevance_template_human = '''
Product Name: {product_name}
Product Description: {product_information}

Please classify the following keywords and provide their relevance categories in the specified JSON format:
{keyword_list_str}
'''

relevance_prompt = ChatPromptTemplate.from_messages([
        ("system", relevance_template_system),
        ("human", relevance_template_human)
    ])


# ====================================================================================================
# select_keywords_prompt

select_count = 50

select_template_system = f'''
You are a senior marketing strategist building a balanced and powerful keyword portfolio for an Amazon product. 
Your goal is to select the {select_count} most valuable keywords from the provided list to maximize both immediate sales and long-term market reach.

Each keyword has a 'relevance_category' ('Direct', 'Related', 'Indirect').
It may also has a 'value_score' (representing opportunity).

Think of your selection as a strategic portfolio with three tiers. Your final list of {select_count} should be a strategic mix of these tiers:

1.  **Core Conversion Keywords (approx. {select_count * 0.5}~{select_count * 0.6} slots):**
    *   Select these from the **'Direct'** category. These are your most important keywords for driving immediate sales.
    *   (If value_score exists) Within this category, choose the ones with the **highest `value_score`**.
    *   (If no value_score) Choose keywords that most directly and unambiguously describe the product.

2.  **Audience Expansion Keywords (approx. {select_count * 0.2}-{select_count * 0.3} slots):**
    *   Select these from the **'Related'** category. These keywords will help you reach a broader, but still highly relevant, audience.
    *   (If value_score exists) Prioritize those with the **highest `value_score`**.
    *   (If no value_score) Choose keywords that describe common use cases or target customer groups for the product.

3.  **Strategic Discovery Keywords (approx. {select_count * 0.1}-{select_count * 0.2} slots):**
    *   (If value_score exists) Select these from the **'Indirect'** category. Look for "hidden gems" here – keywords with an **exceptionally high `value_score`** that can bring in valuable, low-competition traffic.
    *   (If no value_score) Look for creative or unexpected keywords that could lead new types of customers to the product.

**Your final goal is a balanced portfolio of {select_count} keywords.** Avoid simply filling the list only with 'Direct' keywords. The aim is to ensure both high conversion and wider audience discovery.

Return your response ONLY as a valid JSON array of strings, containing the {select_count} selected keywords. Do not include any other text, explanation, or markdown.

Example format:
[
  "keyword 1",
  "keyword 2",
  "keyword 3"
]
'''

select_template_human = '''
Here is the list of candidate keywords with their relevance and value scores. Please select the top {select_count}.
{data_list_str}
'''

select_prompt = ChatPromptTemplate.from_messages([
        ("system", select_template_system),
        ("human", select_template_human)
    ])


# ====================================================================================================
# info_refine_prompt

summarization_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert at summarizing product information. Please extract the key features, specifications, and purpose of the product from the following text in a concise manner. The summary should be in English."),
        ("human", "Product Text:\n```\n{product_text}\n```")
    ])
