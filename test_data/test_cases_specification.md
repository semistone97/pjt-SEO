# 테스트 데이터 케이스 명세

이 문서는 `test_data` 폴더에 있는 각 하위 폴더가 어떤 테스트 케이스를 상정하고 있는지 설명합니다.

---

## 1. `chicken shredder`

*   **케이스 종류:** 정상 작동 (Happy Path) / 전체 기능 테스트
*   **목표:** 모든 종류의 데이터(키워드, 제품 정보, 리뷰)가 순서대로 제공될 때, 에이전트의 전체 워크플로우가 정상적으로 동작하는지 확인.
*   **파일 구성:**
    *   `1. keyword_series.csv`
    *   `1.1. ASIN keyword.csv`
    *   `1.2. magnet Kyeword.csv`
    *   `2. product_info.chicken shredder.pdf`
    *   `3. reviews.csv`

---

## 2. `amazon alarm clock`

*   **케이스 종류:** 핵심 기능 테스트 / 다중 파일 처리
*   **목표:** 여러 개의 키워드 파일을 제공했을 때, 에이전트가 이를 어떻게 통합하고 처리하는지 확인.
*   **파일 구성:**
    *   `alarm_설명서.pdf`
    *   `extended_keywords.csv` (약 200개의 순수 키워드)
    *   `keyword.csv` (원본 키워드)

---

## 3. `iphone case`

*   **케이스 종류:** 최소 정보 정상 케이스
*   **목표:** 가장 필수적인 정보(키워드, 제품 정보)만으로 에이전트의 핵심 기능이 정상 동작하는지 확인.
*   **파일 구성:**
    *   `1. iphone_keyword.csv`
    *   `2. pi-iphone_case.pdf`

---

## 4. `honeywell turbo fan`

*   **케이스 종류:** 예외 상황 / 비정형 데이터 처리
*   **목표:** 제품 정보 PDF 대신 '리뷰 PDF'가 주어졌을 때, 에이전트가 비정형 데이터에서 정보를 추출하려 시도하는지, 또는 명확한 피드백을 주는지 확인.
*   **파일 구성:**
    *   `helium10-keyword-manager...csv`
    *   `제품리뷰.pdf`

### 결과
```bash
=== 키워드 분배 결과 ===
 Title Keyword: 3개
 BP Keyword: 5개
 Description Keyword: 12개
 Leftover: 49개
```

[Title]  
Honeywell Turbo Force Power Fan, 40W Table/Desk Fan, Compact & Lightweight, 3 Speed Settings, Manual Adjustment, Black

[Bullet Point]  
COMPACT DESIGN: Ideal for small spaces, this fan features a compact and lightweight design for easy portability and storage; perfect for desks or bedside tables.  
SIMPLE OPERATION: User-friendly single dial for quick speed adjustments; choose from three speed settings - low, medium, and high - to suit your cooling needs.  
DIRECTED AIRFLOW: Manual 90˚ up-down adjustment allows you to direct airflow exactly where you need it, enhancing comfort in any room or workspace; tailored cooling solution.  
NO ASSEMBLY REQUIRED: Comes fully assembled right out of the box; enjoy immediate relief from the heat with this hassle-free, ready-to-use fan.  
AFFORDABLE PRICE POINT: Offers a cost-effective solution for personal cooling needs without compromising.

[Description]  
The Honeywell Turbo Force Power Fan stands out as an essential tool for anyone seeking a cost-effective and straightforward cooling solution. Its compact and lightweight design makes it ideal for use in small spaces like desks, where space is at a premium. With the ability to deliver a powerful airflow, this fan is perfect for those hot summer days when you need immediate relief.

**Versatile Usage Scenarios:** Whether you're working from home or simply relaxing, the Honeywell Turbo Force Power Fan provides directed airflow to keep you cool and comfortable. It's particularly useful for individuals who require focused cooling, such as those who work at a desk or enjoy reading in bed.

**Technical Specifications:**
- **Dimensions:** 29cm H x 29cm W x 16cm D
- **Weight:** 1.3kg
- **Power:** 40W
- **Speed Settings:** Three distinct speeds (low, medium, high) offer customizable cooling options.

**Care and Maintenance:** Maintaining your fan is simple. Regularly clean the blades and grill with a soft brush or cloth to ensure optimal performance. The fan's compact design makes it easy to store when not in use.

**Warranty and Support:** Each Honeywell Turbo Force Power Fan is backed by a manufacturer's warranty, ensuring peace of mind with your purchase. For any technical support or queries, Honeywell's customer service is readily available to assist you.

**Target Audience:** This fan is perfect for budget-conscious consumers seeking a no-frills solution to personal cooling needs. Its straightforward operation makes it suitable for individuals of all ages, including students, apartment dwellers, and those living in small homes.

**Installation and Setup:** Arriving fully assembled, the fan requires no additional setup, allowing you to experience relief from the heat immediately upon unboxing.

Leftover Keywords: 10 inch portable fan, 12 inch clip on fan, 12 inch desk fan, 12 inch fans electric 3 speed, 12 portable fan, 6 in fan, amazon mini fan, amazon small fan, arctic wind fan, b001r1rxug, baby safe fan, bedroom desk fan, bedroom table fan, bedside fan, bedside fan for sleeping, bedside table fan, best fans for cooling bedroom, black amazon, black desk fan, black small fan, brushless fan, cheap fan, child safe fan, climate keeper fan, corded fan, counter fan, counter fan for kitchen, counter top fan, countertop fan, desk & table fan, desk & table small fan, desk electric fans, desk fan electric, desk fan for bedroom, desk fan for dorm, desk fans for bedroom small, desk fans small, desk room fans, desk shop fans, desk top fan, desk top fans small quiet electric, dorm desk fan, dorm room essentials fan, duracraft fan, easy home fan, electric desk fan, electric table fan, fam for dorm, fan 660, fan bathroom, fan bedside, fan deals, fan for bedroom small, fan for nightstand, fan for small bedroom, fan for table, fan for white noise, fan noise, fan office, fan overnight delivery, fan plug in, fan same day delivery, fan small, fan small room, fan table, fan tabletop, fan under 20, fan white noise, fan with long cord, fan xing, fans for bathroom, fans for office, fans for small rooms, fans that blow cold air portable, fans', grow room fan, high performance fan, honey well, honeywell 11 fan, household fan, intertek fan, kid safe fan, kitchen counter fan, little fan, little fans for bedroom, mini fan for bedroom, mini fan for room, mini room fan, night stand fan, nightstand fan for bedroom, on fan electric, outlet fan plug in, polar wind fan, portable fan electric, portable fan plug in, room circulation fan, rv fan, side table fan, side table fan for bedroom, small bedroom fan, small bedroom fan quiet, small bedside fan for sleeping, small bedside fans, small black fan, small circulating fan, small counter fan, small electric fans for bedroom, small fan bedroom, small fan desk, small fan dorm, small fan electric white noise, small fan for bedroom, small fan for desk, small fan for dorm, small fan for dorm room, small fan for kitchen, small fan for room, small fan with plug, small fans amazon, small fans for bedroom quiet, small fans for rooms, small fans portable plug in electric, small house fan, small indoor fan, small kitchen fan, small loud fan, small loud fan for sleeping, small personal fans, small quiet fan for bedroom, small room fan, small room fans for bedroom, small round fan, small table fan for bedroom, small table fans, spot fan, strong cooling fan, table & desk fan, table fan climate keeper, table fan quiet, table fan small, table top fan, table top fan for desk, tabletop fan, tabletop fan for bedroom, torpedo fan, vornado 660, vornado 660 fan, vornado 660 large air circulator, vornado 660 large air circulator fan, vornado 660 large whole room air circulator fan, vornado 733, vornado fan 660, vornado fan vornado 660 large air circulator, vornado large, vornado large fan, white noise fan



---

## 5. `medicube collagen cream`

*   **케이스 종류:** 데이터 부족 / 오류 처리
*   **목표:** 키워드 파일만 존재할 때, 에이전트가 필수 정보 부족을 인지하고 사용자에게 피드백을 주거나 프로세스를 정상적으로 중단하는지 확인.
*   **파일 구성:**
    *   `with no column...csv`

---

## 6. `salad spinner`

*   **케이스 종류:** 데이터 부족 및 분리 / 경로 처리
*   **목표:** 매우 적은 수의 키워드로 시작했을 때의 성능과
*   **파일 구성:**
    *   `1. few keyword.csv`
    *   `샐러드 스피너 (Salad Spinner).pdf`


- 결과

```bash
=== 키워드 분배 결과 ===
 Title Keyword: 3개
 BP Keyword: 5개
 Description Keyword: 7개
 Leftover: 1개
```

[Title]  
Salad Spinner with Pump Handle and Transparent Bowl, Efficient Vegetable Dryer for Crisp Salads

[Bullet Point]  
RAPID MOISTURE REMOVAL: Uses centrifugal force to dry salad greens quickly and efficiently, reducing preparation time and enhancing meal prep convenience  
FRESHNESS MAINTENANCE: Proper moisture removal ensures dressings adhere better, maintaining the crisp texture of salads for longer, and enhancing flavors  
VERSATILE USE: Inner basket doubles as a vegetable washer, while the outer bowl can be used for serving salads, optimizing kitchen space and functionality  
EASY TO OPERATE: Features a user-friendly lid with a spinning mechanism; simply press the pump or rotate the handle for desired results, making it suitable for all ages  
TIME-SAVING: Reduces salad preparation time and ensures vegetables stay fresh longer when refrigerated

[Description]  
The Salad Spinner is a must-have kitchen gadget for anyone aiming to elevate their salad game with minimal effort. Designed to swiftly and effectively remove excess moisture from your freshly washed greens using centrifugal force, this tool enhances the adhesion of dressings, ensuring a delightful, crisp texture with every bite. Beyond salads, the versatile design allows you to wash and dry fruits or other vegetables, making it an indispensable multi-use tool in your kitchen.

Crafted with a compact and space-saving design, the Salad Spinner seamlessly integrates into any kitchen setup without consuming excessive space. Its clear outer bowl doubles as an elegant serving dish, while the inner basket efficiently strains and dries produce, ensuring your meals are not only delicious but also aesthetically pleasing.

**Technical Specifications:**
- **Materials:** Durable, food-safe plastic
- **Dimensions:** Approximately 10 inches in diameter, ideal for small to medium-sized servings
- **Weight:** Lightweight yet sturdy for easy handling

**Care Instructions:**
- Dishwasher safe on the top rack for hassle-free cleaning
- For manual cleaning, simply rinse with warm soapy water and dry thoroughly before storing

**Warranty and Customer Support:**
Every Salad Spinner comes with a 1-year warranty, ensuring quality and reliability. Our responsive customer service team is readily available to assist with any queries or concerns, providing peace of mind with every purchase.

**Target Audience:**
Perfect for health-conscious individuals, busy families, and culinary enthusiasts who appreciate the value of fresh, homemade salads. Ideal for those short on time but unwilling to compromise on flavor and freshness.

**Installation and First Use Guidance:**
Simply insert the washed produce into the inner basket, place the lid securely, and use the spinning mechanism to remove moisture. It's straightforward and user-friendly for all ages, making salad preparation a breeze even for novice cooks.

Leftover Keywords: oxo salad spinner