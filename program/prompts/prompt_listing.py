from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.prompts.few_shot import FewShotPromptTemplate


# ====================================================================================================
# Keyword Prompt
keyword_template = '''
You are given a keyword list related to the product {product_name} to be sold on Amazon.
Each keyword must be classified into one of the following categories:

[Relevance_Category Definitions]

Direct:
- Keywords that explicitly contain the product's core feature or name
- Example: "chicken shredder," "meat shredder"

Related:
- Keywords closely connected to the product category or usage context
- Similarity to product category words (Kitchen gadget, Meat grinder, Food prep)
- Not direct, but **close in category/usage context**
- Example: "kitchen gadget," "meal prep"

Indirect:
- Keywords that are complementary, seasonal, or niche, appealing to similar customers but not describing the core product
- Complementary/seasonal/niche/long-tail keywords
- Keywords for complementary products that appeal to the same customer base despite differing functions
- Example: "cooking gifts," "countertop appliance"

NotRelated:
- Keywords that are irrelevant to the product
- This keyword is not related to the product at all
- Example: "fitness," "travel bag"

[Additional Rules: Move to Leftover]
- If a keyword contains a brand name, move it to Leftover
- If a keyword is an ASIN (Amazon Standard Identification Number), move it to Leftover  
- If a keyword has 3 or more words (long-tail keyword), move it to Leftover
- These keywords must not remain in Direct, Related, or Indirect categories — always place them in Leftover to avoid consumer confusion

[Listing Elements - Keyword Relevance Category Mapping]

1. Title (Product name / top-level visibility)
- Direct: Must be included (core product nouns, main function, purpose)
- Related: Optionally included (adjectives or feature highlights — keep title length in mind)
- Indirect: Generally excluded (title should focus on core relevance; too broad hurts CTR)
- NotRelated: Exclude entirely
→ Summary: Title = Direct focus, with minimal Related support. Up to 10 keywords maximum.

2. Bullet Points (features & benefits / SEO + readability)
- Direct: Lead with them (start each BP with core keywords to highlight function)
- Related: Actively include (describe features, use cases, benefits)
- Indirect: Limited use (only if they add context or lifestyle scenarios)
- NotRelated: Exclude
→ Summary: Bullet Points = Direct + Related required, Indirect only for context. Requires 5 important direct keywords and associated indirect keywords for each.

3. Description (detailed explanation / SEO + persuasion)
- Direct: Repeat and emphasize (strengthen product relevance)
- Related: Naturally weave in (improves SEO while keeping readability)
- Indirect: Actively leverage (for storytelling, lifestyle context, long-tail search traffic)
- NotRelated: Exclude
→ Summary: Description = Direct repetition + Related integration + Indirect expansion. Primarily uses Related keywords, approximately 20 keywords.

4. Leftover (backend keywords / hidden search terms)
- Direct: If already used in Title/BP/Description, avoid duplication
- Related: Place unused ones here
- Indirect: Good spot for remaining Indirect terms
- NotRelated: Remove (noise reduction)
→ Summary: Leftover = Collect unused Related & Indirect; drop NotRelated. Keywords not used in the above sections.

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
        },
        {
            "title_keyword": "brown water bottle, water bottle simple modern, simple modern mesa, mesa loop, simple modern water bottle, simple modern, fall water bottle, sm water bottle, simple modern mesa loop, mesa loop simple modern, brown owala water bottle, simple modern 30 oz, simply modern, simple modern harvest collection, hot pink water bottle, simply modern water bottle, 30 oz water bottle, simple modern fall, owala orange, owala brown, simple modern water bottle kids, simple modern 30 oz tumbler, owala sway 30 oz, simply modern kids water bottle, owala down to earth, kids simple modern water bottle, simple modern halloween, ember cold tumbler, simple modern fall tumbler, blue owala water bottle 24 oz",
            "title": "Simple Modern Mesa Loop Water Bottle with Straw | 24oz Cup Holder Friendly Insulated Stainless Steel Bottles for Travel, Sports and School | Midnight Black"
        },
        {
            "title_keyword": "water bottle, owala water bottle, owala water bottle 24 oz, owala water bottle 32oz, owala water bottle 40 oz, water bottles, kids water bottle, owala kids, insulated water bottle, water bottle insulated, owala kids water bottle, owala 40 oz, kids water bottle for school, stainless steel water bottles, water bottle for school, owala 24 oz, owala free sip, awalah water bottle, owala 32 oz, water bottle with straw, water bottle stainless steel, pink owala, owala 16 oz, back to school, owala free sip sway, water bottle kids, travel accessories, hydro flask water bottles, yeti kids water bottle, hydroflask 40 oz water bottle",
            "title": "Owala FreeSip Insulated Stainless Steel Water Bottle with Straw, BPA-Free Sports Water Bottle, Great for Travel, 24 Oz, Denim"
        },
        {
            "title_keyword": "food storage containers with lids, lunch containers, food containers, food storage containers, containers with lids, lunch containers for adults, rubbermaid brilliance storage containers, tupperware set, rubbermaid brilliance, tupperware glass, rubbermaid food storage containers, tupperware sets with lids, glass tupperware, food storage, food containers with lids, food prep containers, containers for food, glass storage containers, meal prep containers, meal prep containers glass, glass food storage, glass meal prep containers with lids, glass tupperware sets with lids, small containers with lids, snack containers, organization and storage, snapware glass storage containers, pyrex glass storage containers with lids, meal prep, freezer storage containers",
            "title": "Rubbermaid Brilliance Food Storage Containers BPA Free Airtight Lids Ideal for Lunch Meal Prep & Leftovers Set of 5 (3.2 Cup)"
        },
        {  
            "title_keyword": "bissell little green machine, upholstery cleaner, little green clean machine, couch cleaner, upholstery cleaner machine, green machine carpet cleaner, couch cleaner machine, mattress cleaner, car detailing, green machine, portable carpet cleaner, little green machine, steam cleaner for furniture, wet vacuum cleaner, carpet cleaner, car seat cleaner, bissell carpet cleaner, rug cleaner, pet carpet cleaner, steam cleaner for car, carpet cleaner machine, carpet steam cleaner, carpet shampooer, cleaning tools, bissell steam cleaner, carpet shampooer machine, portable vacuum for car, bissell little green machine solution, mini foldable desktop mop, shark stain striker",
            "title": 'BISSELL Little Green Mini Portable Carpet and Upholstery Deep Cleaner, Car/Auto Detailer, with HydroRinse Self-Cleaning Tool and 4" Tough Stain Tool, Tea Green, 4075'
        }
    ]

title_example_prompt = PromptTemplate.from_template('[keyword]\n{title_keyword}\n[output]\nTitle: {title}')

title_prefix = """
Generate optimal product title by referring to the requirements, guidelines, and examples below.

[Product title requirements]
Title requirements apply to all product types, except media product types, in all of our worldwide stores. In order to list a product for the first time, your title must meet the below requirements. If your product is already listed and the title doesn't comply with these requirements, the title might be automatically corrected or it might not appear in search results.

Follow these criteria when creating product titles:
• Titles must not exceed 200 characters, including spaces. Refer to Title length criteria exceptions for a list of exceptions to this requirement.
• Titles must not contain promotional phrases, such as "free shipping" or "100% quality guaranteed."
• Titles must not use the following special characters: !, $, ?, _, curly brackets, ^, ¬, ¦. Other special characters, such as ~, #, <, >, and *, are allowed only in specific contexts. For example, you may use these symbols as product identifiers ("Style #4301") or measurements ("<10 lb"). Decorative usage of special characters is not allowed. For example, the title "Paradise Towel Wear Co. Beach Coverup << Size Kids XXS >>" is non-compliant because of the excessive use of symbols around the size.
• Titles must contain the minimum amount of information that can be used to clearly describe the product, such as "Amazon Essentials Dress," "Columbia Hiking Boots," or "Sony Headphones."
• Titles must not contain the same word more than twice. For example, "Baby Boy Outfits Baby Boy fall Winter Clothes Baby Boy Long Sleeve Suspender Outfit Sets" is a non-compliant title.

[Product title guidelines]
Creating high-quality product titles is crucial for driving discoverability and conversions. Customers quickly scan search results, so ensuring that your title captures the most important product information is key to making your listing discoverable. Additionally, overly long or cluttered titles can be difficult to read. Therefore, the ideal title should concisely reflect the key information about the physical product, without excessive detail or non-essential elements.

The following guidelines are best practices that you may want to consider to provide the best possible customer experience:

• Keep titles concise. While 200 characters is the maximum allowed, we recommend that you use 80 or fewer characters because mobile screens truncate long titles.
• Don't include redundant information, unnecessary synonyms, or excessive keywords in the product title.
• Include only the information that will help customers quickly recognize and understand the product. Order the words to reflect the most important product information upfront. You may consider the following order, if applicable:
    - Brand name
    - Flavor/style
    - Product type name
    - Key attribute (that is, the unique selling proposition of the product)
    - Color
    - Size/pack count
    - Model number

[For example]
- Amazon Fresh Decaf Colombia Whole Bean Coffee, Medium Roast, 12 Ounce (Pack of 3)
- Amazon Fire HD 8 Tablet, 8" HD Display, 3GB Memory, 32GB RAM, 512GB, Black
- Amazon Essentials Toddler Girls' Short-Sleeve Pique Polo Dress
• For products that have variations, include the size and color variations in the title of the child ASINs and not in the title of the parent ASIN. The detail page displays the title of the parent ASIN, and the title of the child ASIN will only appear once the ASIN is added to the customer's cart. The child ASIN title will not appear on the product detail page.
    Example parent title: Amazon Essentials T-Shirt
    Example child title: Amazon Essentials T-Shirt, White, Medium
• Don't use ALL CAPS.
• Capitalize the first letter of each word, except for prepositions (in, on, over, with), conjunctions (and, or, for), or articles (the, a, an).
• Use numerals: "2" instead of "two".
• Use only standard letters and numbers. Don't use non-language ASCII characters such as Æ, Š, Œ, Ÿ, or Ž.
• Don't use subjective commentary, such as "Hot Item" or "Best seller".
• Titles can include necessary punctuation, like hyphens (-), forward slashes (/), commas (,), ampersands (&), and periods (.).
• Titles can abbreviate measurements, such as "cm", "oz", "in", and "kg".
"""

title_suffix = """
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
    suffix=title_suffix,
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
    },
    {
        "bp_keyword": "brown water bottle, water bottle simple modern, simple modern mesa, mesa loop, simple modern water bottle, simple modern, fall water bottle, sm water bottle, simple modern mesa loop, mesa loop simple modern, brown owala water bottle, simple modern 30 oz, simply modern, simple modern harvest collection, hot pink water bottle, simply modern water bottle, 30 oz water bottle, simple modern fall, owala orange, owala brown, simple modern water bottle kids, simple modern 30 oz tumbler, owala sway 30 oz, simply modern kids water bottle, owala down to earth, kids simple modern water bottle, simple modern halloween, ember cold tumbler, simple modern fall tumbler, blue owala water bottle 24 oz",
        "bp": [
            ' Cupholder Friendly: Both 30oz and 24oz fit most cupholders',
            ' Folding Loop Handle: Comfort grip coating. Grab and go with just a finger',
            ' Contoured Straw: Say goodbye to mouth wrinkles and hello to unmatched flow rate',
            ' Clean-Lock Covered Lid: Click the button up/down to lock or unlock',
            ' Soft Landings: Silicone base for quiet sitting. Dishwasher safe'
        ]
    },
    {
        "bp_keyword": "water bottle, owala water bottle, owala water bottle 24 oz, owala water bottle 32oz, owala water bottle 40 oz, water bottles, kids water bottle, owala kids, insulated water bottle, water bottle insulated, owala kids water bottle, owala 40 oz, kids water bottle for school, stainless steel water bottles, water bottle for school, owala 24 oz, owala free sip, awalah water bottle, owala 32 oz, water bottle with straw, water bottle stainless steel, pink owala, owala 16 oz, back to school, owala free sip sway, water bottle kids, travel accessories, hydro flask water bottles, yeti kids water bottle, hydroflask 40 oz water bottle",
        "bp": [
            ' 24-ounce insulated stainless-steel water bottle with a FreeSip spout and push-button lid with lock',
            ' Patented FreeSip spout designed for either sipping upright through the built-in straw or tilting back to swig from the spout opening',
            ' Protective push-to-open lid keeps spout clean; convenient carry loop doubles as a lock',
            ' Double-wall insulation keeps drinks cold for up to 24 hours; wide opening for cleaning and adding ice; cup holder-friendly base',
            ' BPA, lead, and phthalate-free; hand wash cup, dishwasher-safe lid; not for use with hot liquids'
        ]
    },
    {
        "bp_keyword": "food storage containers with lids, lunch containers, food containers, food storage containers, containers with lids, lunch containers for adults, rubbermaid brilliance storage containers, tupperware set, rubbermaid brilliance, tupperware glass, rubbermaid food storage containers, tupperware sets with lids, glass tupperware, food storage, food containers with lids, food prep containers, containers for food, glass storage containers, meal prep containers, meal prep containers glass, glass food storage, glass meal prep containers with lids, glass tupperware sets with lids, small containers with lids, snack containers, organization and storage, snapware glass storage containers, pyrex glass storage containers with lids, meal prep, freezer storage containers",
        "bp": [
            '100% Leak-proof: Guaranteed no-spill seal and secure latches',
            ' Crystal-clear Tritan Built: Stain-resistant and odor-resistant material for a clear view of contents',
            ' Lightweight & Sturdy: Easy to carry, yet durable for everyday use',
            ' Built-in Vents: Convenient microwave heating without removing the lid',
            ' Space-saving: Stackable design for organized fridge or pantry',
            ' Dishwasher, Microwave & Freezer Safe: Easy and safe to use in various conditions',
            ' Large Set: Includes five 3.2-cup containers and matching lids, totaling 10 pieces'
        ]
    },
    {
        "bp_keyword": "bissell little green machine, upholstery cleaner, little green clean machine, couch cleaner, upholstery cleaner machine, green machine carpet cleaner, couch cleaner machine, mattress cleaner, car detailing, green machine, portable carpet cleaner, little green machine, steam cleaner for furniture, wet vacuum cleaner, carpet cleaner, car seat cleaner, bissell carpet cleaner, rug cleaner, pet carpet cleaner, steam cleaner for car, carpet cleaner machine, carpet steam cleaner, carpet shampooer, cleaning tools, bissell steam cleaner, carpet shampooer machine, portable vacuum for car, bissell little green machine solution, mini foldable desktop mop, shark stain striker",
        "bp": [
            'EVERY PURCHASE SAVES PETS. Every purchase makes it possible for BISSELL to continue our support of BISSELL Pet Foundation and its mission of saving pets in need.'
            'SAVE YOUR SANCTUARY: Tackle spills and pet stains while removing dander, dust, and pollen allergens.',
            'CLEANS MORE THAN CARPET: Spray, scrub, and suction to remove embedded dirt and stains from upholstery, car interiors, pet beds, and more.',
            'INCLUDES: 4" Tough Stain Tool with removeable lens, HydroRinse self-cleaning hose tool, and 8oz. BISSELL Little Green Formula.',
            'EASY STORAGE: Conveniently stores in small spaces - perfect for cabinets, closets, and more.',
            'LITTLE GREEN FORMULA: Instantly and permanently removes stains and eliminates everyday household odors.'
        ]
    }
]

bp_example_prompt = PromptTemplate.from_template('[keyword]\n{bp_keyword}\n[output]\nBullet Point: {bp}')

bp_prefix = """
Generate high-quality bullet points suitable for product characteristics by referring to the requirements, guidelines, and examples below.

[Product bullet points requirements]
Bullet points highlight the five main features and benefits you want customers to know about your products. Bullet points help customers quickly understand if the product is right for them.

Do not include below information. Bullet points with below information will be removed or updated:
• Special characters such as ™, ®, €, …, †, ‡, o, ¢, £, ¥, ©, ±, ~, â
• Any emojis such as ☺, ☹, ✅, ❌
• ASIN number or "not applicable" or "NA" or "n/a" or "N/A", "not eligible", "yet to decide", "to be decided", "TBD", "COPY PENDING"
• Prohibited phrases such as eco-friendly, environmentally friendly, ecologically friendly, anti-microbial, anti-bacterial, Made from Bamboo, contains Bamboo, Made from Soy or contains Soy. For more information, go to General Listing Restrictions
• Prohibited guarantee information such as "Full refund" or "If not satisfied, send it back" or "Unconditional guarantee with no limit"
• Company information, website links, external hyperlinks or any contact
• Repetition in bullet points. Each bullet point must mention unique product information
• Include at least three bullet points

[Writing guidelines for high-quality bullet points]
• Begin with a capital letter
• Be formatted as a sentence fragment; don't use end punctuation
• Use semicolons to separate phrases within a single bullet point
• Use more than 10 characters but less than 255 characters
• Write numbers one to nine in full, excluding names, model numbers, and measurements
• Add header to bullet point and use ":" as separator before providing complete information
• Include a space between a digit and a measurement (for example, 60 ml)
• Use clear, natural language in the bullet points, avoid stuffing in unnecessary keywords or phrases
• Highlight product features and benefits, not the brand's marketing story
• Highlight how the product meets the customer needs, rather than just listing facts
• Maintain data consistency across product variants
• Do not divert or refer to other products not included under this ASIN
• Remove or minimize duplication across attributes such as title, product description or product overview. Highlight additional or supporting information to help the customer make a more informed decision
• Avoid any subjective, performance, or comparative claims, unless they are verifiable on the product packaging. Do not compare your product to competitor brands
• Avoid claims relating to accolades and awards, unless the product detail page contains supporting details, such as date and awarding body
• Avoid claims about the results of consumer surveys, even if the survey collected subjective opinions, unless substantiated with the source and date

[Example of high-quality bullet points]
• Cotton Fabric: Made from 100% cotton for softness and breathability
• Long Sleeve: Long sleeves add coverage and style
• Loose Fit: Relaxed fit allows for easy movement and comfort
• Machine Washable: Durable construction allows for easy care
• Versatile Style: Perfect for dance practice, playtime, or outdoor activity
"""

bp_suffix = """
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
    suffix=bp_suffix,
    input_variables=["product_name", "category", 'product_information', "bp_keyword"],
    )

# ====================================================================================================
# Description Prompt
description_examples = [
    {
        "description_keyword": "chicken, chicken shredder, tools, chicken shredder tool twist, meat shredder, shredder, pork, tool, hand tools, meat shredder tool twist, chicken shredder tool twist large, shredder kitchen, chicken shredder tool, food shredder, chicken breast, kitchen, food, meat, shredded chicken, cooked chicken, kitchen gadgets, meal prep, kitchen tools, amazon kitchen, cooking gifts, cooking gadgets",        
        "description": "<p>[Why You'll Love It]<br />The 10'' Chicken Shredder Tool Twist is your ultimate kitchen companion for quick, safe, and efficient meal preparation. Whether you're making shredded chicken tacos, salads, or pulled pork sandwiches, this tool saves time and effort, delivering professional results in seconds.<br /> <br />[Key Features]<br /> &bull; Effortless Shredding: Quickly and evenly shred cooked chicken, pork, or beef for various dishes.<br /> &bull; Non-Slip Stability: The anti-slip base ensures safety and ease during use.<br /> &bull; Large Capacity: Perfect for family-sized meals with a 10-inch bowl and a transparent lid to monitor the process.<br /> &bull; Ergonomic Design: Comfortable handle reduces hand strain and ensures optimal control.<br /> &bull; Easy Maintenance: Dishwasher-safe design makes cleaning a breeze.</p><p>[Perfect for These People] <br />Crafted with durability in mind, this versatile shredder is ideal for home cooks, meal prep enthusiasts, BBQ lovers, and even pet owners needing a quick way to prepare shredded meat. Add this must-have gadget to your kitchen and transform your cooking experience.</p>"
    },
    {
        "description_keyword": "brown water bottle, water bottle simple modern, simple modern mesa, mesa loop, simple modern water bottle, simple modern, fall water bottle, sm water bottle, simple modern mesa loop, mesa loop simple modern, brown owala water bottle, simple modern 30 oz, simply modern, simple modern harvest collection, hot pink water bottle, simply modern water bottle, 30 oz water bottle, simple modern fall, owala orange, owala brown, simple modern water bottle kids, simple modern 30 oz tumbler, owala sway 30 oz, simply modern kids water bottle, owala down to earth, kids simple modern water bottle, simple modern halloween, ember cold tumbler, simple modern fall tumbler, blue owala water bottle 24 oz",
        "description": "Simple Modern's Mesa Loop water bottle is designed to support your hydration needs no matter where the day takes you. The sleek, cupholder-friendly bottle delivers reliable hydration with a one-handed, spill-proof operation — perfect for juggling kids, meetings, errands, and life on the go. Its collapsible, soft-touch handle also offers a comfortable grip without adding bulk, making it easy to carry. A lockable, leak-proof lid is included while the silicone base ensures soft, quiet landings wherever you set it down. Double-wall insulation keeps drinks cold for 24 hours, and the BPA-free and dishwasher safe design was made for ultimate convenience. The sleek, minimalist, refined design blends seamlessly from driving, to the office, to school pickup, and so much more."
    },
    {
        "description_keyword": "water bottle, owala water bottle, owala water bottle 24 oz, owala water bottle 32oz, owala water bottle 40 oz, water bottles, kids water bottle, owala kids, insulated water bottle, water bottle insulated, owala kids water bottle, owala 40 oz, kids water bottle for school, stainless steel water bottles, water bottle for school, owala 24 oz, owala free sip, awalah water bottle, owala 32 oz, water bottle with straw, water bottle stainless steel, pink owala, owala 16 oz, back to school, owala free sip sway, water bottle kids, travel accessories, hydro flask water bottles, yeti kids water bottle, hydroflask 40 oz water bottle",    
        "description": "The Owala FreeSip Insulated Stainless-Steel Water Bottle with Locking Push-Button Lid easily tackles every thirst. With a built-in, easy-clean straw and a wide-mouth opening, the FreeSip reusable bottle is designed for drinking two different ways: sipping upright through the straw or tilting back to swig from the wide-mouth spout opening. Add in a push-to-open lid and playful colors, and staying hydrated has never been simpler—or more fun. Additional features include double-wall insulated stainless steel that keeps drinks cold up to 24 hours, a carry loop that doubles as a lock, a cup holder-friendly base, and a wide opening for easy cleaning and adding ice. The Owala FreeSip Insulated Stainless-Steel Water Bottle with Locking Push-Button Lid is available in three sizes: 24-Ounce, 32-Ounce, and 40-Ounce. Lid is dishwasher safe; hand wash cup. Not for use with hot liquids. Manufacturer's limited lifetime warranty."
    },
    {
        "description_keyword": "food storage containers with lids, lunch containers, food containers, food storage containers, containers with lids, lunch containers for adults, rubbermaid brilliance storage containers, tupperware set, rubbermaid brilliance, tupperware glass, rubbermaid food storage containers, tupperware sets with lids, glass tupperware, food storage, food containers with lids, food prep containers, containers for food, glass storage containers, meal prep containers, meal prep containers glass, glass food storage, glass meal prep containers with lids, glass tupperware sets with lids, small containers with lids, snack containers, organization and storage, snapware glass storage containers, pyrex glass storage containers with lids, meal prep, freezer storage containers",
        "description": "Revolutionize your meal prep with the Rubbermaid Brilliance Food Storage Containers set. Made from BPA-free Tritan, these high-quality containers are visibly clear like glass, but are incredibly durable and easy to carry. They feature 100% leak-proof seals and secure latches to preserve freshness and prevent spills. Not only are they stain and odor-resistant, but they also have built-in vents under latches for mess-free microwaving with the lid on. With a stackable design, they ensure space-efficiency in your fridge or pantry, improving organization and accessibility. This pack comes with five 3.2-cup plastic containers and matching lids."
    },
    {
        "description_keyword": "bissell little green machine, upholstery cleaner, little green clean machine, couch cleaner, upholstery cleaner machine, green machine carpet cleaner, couch cleaner machine, mattress cleaner, car detailing, green machine, portable carpet cleaner, little green machine, steam cleaner for furniture, wet vacuum cleaner, carpet cleaner, car seat cleaner, bissell carpet cleaner, rug cleaner, pet carpet cleaner, steam cleaner for car, carpet cleaner machine, carpet steam cleaner, carpet shampooer, cleaning tools, bissell steam cleaner, carpet shampooer machine, portable vacuum for car, bissell little green machine solution, mini foldable desktop mop, shark stain striker",
        "description": "Save on space without sacrificing on cleaning ability. Use BISSELL® Little Green® Mini portable upholstery and carpet cleaner to spray, scrub and lift away tough messes, like dirt and stains, from all types of surfaces. Easily access hard-to-clean spaces like staircases or car interiors with Little Green® Mini portable deep cleaner’s lightweight and compact design. Every purchase makes it possible for BISSELL to continue our support of BISSELL Pet Foundation® and its mission of saving pets in need. Since 2011, BISSELL has donated over $26 million in support of BISSELL Pet Foundation®. When you purchase a BISSELL® product, you help save pets, too. Our products are engineered to clean even the toughest messes so pets can stay at home and out of shelters."
    }
]



description_example_prompt = PromptTemplate.from_template('[keyword]\n{description_keyword}\n[output]\nDescription: {description}')

description_prefix = """
Generate high-quality product description by referring to the requirements, guidelines, and previously generated bullet points below. Ensure NO content duplication with the bullet points.

[Product description requirements]
The product description, presented in paragraph form on the detail page, should provide an elaboration beyond the bullet points. This section allows you to go into more depth with content NOT covered in bullet points, including detailed usage scenarios, technical specifications, compatibility information, care instructions, warranty details, and comprehensive application contexts. The product description should be concise, clear, and engaging, providing complementary information that helps customers make informed purchasing decisions.

• Description must not exceed 2000 bytes in total length
• Make the description interesting and communicate the product value within the first 200 characters
• Present content in paragraph form on the detail page

[Content differentiation from bullet points]
• DO NOT repeat or rephrase bullet point content
• Focus on usage scenarios and real-world applications not mentioned in BP
• Include technical specifications, dimensions, materials, and compatibility details
• Provide care and maintenance instructions beyond basic cleaning
• Mention warranty, return policy, or customer service information
• Describe target audience and ideal use cases
• Include installation, setup, or first-use guidance when applicable
• Address frequently asked questions or common concerns
• Provide context about product category and market positioning

[Product description guidelines]
• Present content in paragraph form with natural flow between topics
• Lead with compelling value proposition in first 200 characters to capture attention immediately
• Expand on practical usage scenarios and real-world applications
• Include technical details: dimensions, weight, materials, specifications
• Provide comprehensive care instructions and maintenance tips
• Mention compatibility with other products, accessories, or systems
• Include warranty information, return policies, or customer support details
• Address target demographics and specific use cases
• Use engaging, conversational tone that builds confidence in purchase decision
• Focus on information that answers "How do I use this?" and "Will this work for me?"
• Avoid subjective claims unless verifiable on packaging
• Do not mention competitors or make comparative statements
• Ensure content adds value beyond what bullet points already communicate
• Keep total length under 2000 bytes while maintaining comprehensive coverage
"""

description_suffix = """
[Generated Bullet Points]
{bp_result}
---
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
    suffix=description_suffix,
    input_variables=["product_name", "category", "product_information", "description_keyword", "bp_result"],
)

# ====================================================================================================
# Verification Prompt
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
verification_prompt = ChatPromptTemplate.from_messages([
        ('system', verification_template_system),
        ('human', verification_template_human)
    ])