from langchain_core.prompts import PromptTemplate
from langchain_core.prompts.few_shot import FewShotPromptTemplate


# ====================================================================================================
# Keyword Prompt
keyword_template = '''
Below is data showing various keywords related to the product {product_name} to be sold on Amazon, along with how closely each keyword is linked to the actual product (relevance_category).

The meaning of relevance_category is as follows:
Direct: 
- The keyword directly includes the product's core feature/name
Intermediate: 
- Similarity to product category words (Kitchen gadget, Meat grinder, Food prep)
- Not direct, but **close in category/usage context**
Indirect:
- Complementary/seasonal/niche/long-tail keywords
- Keywords for complementary products that appeal to the same customer base despite differing functions
NotRelated:
- This keyword is not related to the product at all



We plan to use these keywords on the product sales page. Please distribute them according to the criteria across Title/Bullet Point/Description/Leftover.
- Title: Most core, includes key attributes. Primarily Direct keywords, up to 10 keywords maximum
- Bullet Point: Includes the product's benefits from the customer's perspective. Requires 5 important direct keywords and associated indirect keywords for each.
- Description: Product explanation. Primarily uses intermediate keywords, approximately 20 keywords.
- Leftover: Keywords not used in the above sections.

---
[Data]
Product Name: {product_name}
Category: {category}
Product Description: {product_information}
---
[Keywords]
Keyword Data:
{data}
---
[Output]
'''

keyword_prompt = PromptTemplate.from_template(keyword_template)

# ====================================================================================================
# Title Prompt
title_examples = [
    {
        "title_keyword": "chicken, chicken shredder, tools, chicken shredder tool twist, meat shredder, shredder, pork, tool, hand tools, meat shredder tool twist, chicken shredder tool twist large, shredder kitchen, chicken shredder tool, food shredder, chicken breast, kitchen, food, meat, shredded chicken, cooked chicken, kitchen gadgets, meal prep, kitchen tools, amazon kitchen, cooking gifts, cooking gadgets",
        "title": "Chicken Shredder, 10'' Large Chicken Shredder Tool Twist with Transparent Lid, Ergonomic Handle and Anti-Slip Base, Dishwasher Safe, Ideal for Meal Prep"
    }
]

title_example_prompt = PromptTemplate.from_template('[keyword]\n{title_keyword}\n[output]\nTitle: {title}')

title_prefix = """
Use the example for reference. Please create Amazon product titles by verifying the following information.
The goal is to maximize search visibility. Strictly adhere to the rules below.

[Rules]
- Title must not exceed 200 characters.
- Include the brand name, product line, and key attributes.
- Use relevant keywords in the first 80 characters.
- Capitalize the first letter of every word except prepositions, conjunctions, and articles.
"""

title_snuffix = """
[Data]
Product Name: {product_name}
Category: {category}
Product Description: {product_information}
---
[Keywords]
{title_keyword}
---
[Output]
Final Title:  
"""

title_prompt = FewShotPromptTemplate(
    examples=title_examples,
    example_prompt=title_example_prompt,
    prefix=title_prefix,
    suffix=title_snuffix,
    input_variables=["product_name", "category", "product_information", "title_keyword"],
)

# ====================================================================================================
# BP Prompt
bp_examples = [
    {
        "bp_keyword": "chicken, chicken shredder, tools, chicken shredder tool twist, meat shredder, shredder, pork, tool, hand tools, meat shredder tool twist, chicken shredder tool twist large, shredder kitchen, chicken shredder tool, food shredder, chicken breast, kitchen, food, meat, shredded chicken, cooked chicken, kitchen gadgets, meal prep, kitchen tools, amazon kitchen, cooking gifts, cooking gadgets",
        "bp": [
            'EASY SHREDDING: Effortlessly shred cooked chicken, pork, or beef into even pieces, perfect for tacos, salads, sandwiches, and more. Save time and elevate meal prep with this essential kitchen tool.',
            'STABLE ANTI-SLIP BASE: Equipped with a non-slip base for stability, ensuring safe and efficient shredding without the tool slipping during use.'
            'LARGE CAPACITY WITH TRANSPARENT LID: The 10-inch size accommodates family-sized portions. The transparent lid lets you monitor the shredding process, ensuring perfect results every time.',
            'ERGONOMIC HANDLE DESIGN: Designed with a comfortable, easy-grip handle to reduce hand strain and improve control, making shredding tasks quick and effortless.',
            'DISHWASHER SAFE: Made for convenience, the shredder is dishwasher-safe and easy to clean, ensuring a hassle-free experience in busy kitchens.',
        ]
    }
]

bp_example_prompt = PromptTemplate.from_template('[keyword]\n{bp_keyword}\n[output]\nBullet Point: {bp}')

bp_prefix = """
Use the example for reference and create bullet points for the Amazon product based on the following information.
The goal is to convey accurate information to customers and make them want to use the product. Please strictly adhere to the rules below.

[Rules]
- Each bullet point must not exceed 250 characters.
- Write readable bullet points that explain how the product can benefit customers.
- Key Features: Write the product's main functions and characteristics as a short list of sentences within 100 characters maximum, capitalizing the first letter of each item.

1. Each BP must not exceed 250 characters.
2. The first 3 BPs describe the product's benefits, using keywords that help customers assess its value.
3. The remaining 2 BPs describe the product's functions, using keywords related to what the product can do.
4. If no further keywords are provided, do not generate and fill them; return the response at that point.
5. Write in sentence form, not as a list of keywords.
"""

bp_snuffix = """
[Data]
Product Name: {product_name}
Category: {category}
Product Description: {product_information}
---
[Keywords]
{bp_keyword}
---
[Output]
Final BP:  
"""

bp_prompt = FewShotPromptTemplate(
    examples=bp_examples,
    example_prompt=bp_example_prompt,
    prefix=bp_prefix,
    suffix=bp_snuffix,
    input_variables=["product_name", "category", 'product_information', "bp_keyword"],
    )


# ====================================================================================================
# Description Prompt
description_examples = [
    {
        "description_keyword": "chicken, chicken shredder, tools, chicken shredder tool twist, meat shredder, shredder, pork, tool, hand tools, meat shredder tool twist, chicken shredder tool twist large, shredder kitchen, chicken shredder tool, food shredder, chicken breast, kitchen, food, meat, shredded chicken, cooked chicken, kitchen gadgets, meal prep, kitchen tools, amazon kitchen, cooking gifts, cooking gadgets",
        "description": '''
[Why You'll Love It]
 
  The 10'' Chicken Shredder Tool Twist is your ultimate kitchen companion for quick, safe, and efficient meal preparation. Whether you're making shredded chicken tacos, salads, or pulled pork sandwiches, this tool saves time and effort, delivering professional results in seconds.
 
  [Key Features]
 
  • Effortless Shredding: Quickly and evenly shred cooked chicken, pork, or beef for various dishes.
 
  • Non-Slip Stability: The anti-slip base ensures safety and ease during use.
 
  • Large Capacity: Perfect for family-sized meals with a 10-inch bowl and a transparent lid to monitor the process.
 
  • Ergonomic Design: Comfortable handle reduces hand strain and ensures optimal control.
 
  • Easy Maintenance: Dishwasher-safe design makes cleaning a breeze.
 
  [Perfect for These People]
 
  Crafted with durability in mind, this versatile shredder is ideal for home cooks, meal prep enthusiasts, BBQ lovers, and even pet owners needing a quick way to prepare shredded meat. Add this must-have gadget to your kitchen and transform your cooking experience.
        
        '''
    }
]

description_example_prompt = PromptTemplate.from_template('[keyword]\n{description_keyword}\n[output]\nDescription: {description}')

description_prefix = """
Please write the Description for an Amazon product by referring to the example and checking the following information.
The goal is to convey accurate information to customers in a clean manner, so please strictly adhere to the rules below.

[Rules]
1. The maximum length for the Description is 2000 characters.
2. Within the first 200 characters, write one meaningful sentence that includes important keywords.
3. Write the remaining content using keywords to make it easy for customers to read.
4. If no more keywords can be suggested, do not generate and fill them; return the answer at that point.
5. Answer must be written in English.
"""

description_snuffix = """
[Data]
Product Name: {product_name}
Category: {category}
Product Description: {product_information}
---
[Keywords]
{description_keyword}
---
[Output]
Final Description:  
"""

description_prompt = FewShotPromptTemplate(
    examples=description_examples,
    example_prompt=description_example_prompt,
    prefix=description_prefix,
    suffix=description_snuffix,
    input_variables=["product_name", "category", "product_information", "description_keyword"],
)