from openai import OpenAI
import time, json
from functools import wraps
from glob import glob
from tqdm import tqdm

client = OpenAI(api_key='YOUR_API_KEY')

# System Prompt
SYSTEM_PROMPT = "You are a highly skilled data analyst with expertise in extracting and organizing information from unstructured text. Your task is to analyze the title and description of YouTube videos that are related to food recipes. From the provided text, identify the main dish being discussed, list the ingredients used, categorize them into main ingredients and seasonings, and recognize any relevant tags based on the context (e.g., diet preferences, main ingredients, cooking method). Finally, you will present this information in a structured JSON format, including the dish name, ingredients (split into 'ingredient' for main ingredients and 'seasoning' for condiments or spices), and relevant tags extracted from the text, along with a reformulated title that succinctly describes the dish for a diet-conscious audience. Your output should be precise, informative, and easily understandable, reflecting both the culinary aspects and any dietary considerations highlighted in the video."

# 함수 사용 예시
PROMPT = """당신은 비정형 텍스트에서 정보를 추출하고 정리하는 데 능숙한 데이터 분석가입니다. 당신의 임무는 음식 레시피와 관련된 YouTube 영상의 제목과 설명을 분석하는 것입니다. 제공된 텍스트에서 논의되는 주요 요리명을 식별하고, 사용된 재료들을 나열하며, 주재료와 양념으로 재료들을 분류하고, 문맥에 기반한 관련 태그들(예: 다이어트 선호도, 주요 재료, 조리 방법 등)을 인식합니다. 마지막으로, 이 정보를 구조화된 JSON 형식으로 제시합니다. 이 형식에는 요리명, 재료들(‘ingredient’에는 주재료, ‘seasoning’에는 조미료나 향신료로 분류), 그리고 텍스트에서 추출된 관련 태그들이 포함되며, 다이어트를 의식하는 청중을 위해 간결하게 재구성된 제목도 함께 제공됩니다. 당신의 출력은 정확하고, 정보가 가득하며, 쉽게 이해할 수 있어야 하며, 요리의 요소뿐만 아니라 비디오에서 강조된 고려사항을 반영해야 합니다.

규칙
1. 값은 반드시 한글로 반환해주세요.
2. 반드시 JSON 형식만 간단하게 반환해주세요.
3. 아래는 예시입니다.
Input:
title: 살 힘들게 빼지 말고, 이거 드세요! 심지어 맛도 있어...
description: 무조건 살 빠지는...\n\n\n이 남자의 cook 네이버 카페(이 남자의 식구들) : https://cafe.naver.com/tmc09\n\n\n+++ 계량 : 밥스푼, 티스푼, 계량컵(200ml)+++\n두부 1모(500g)\n양배추 200g\n청양고추 1개\n소금 1/2작은스푼\n양조간장 1스푼\n들기름 1스푼\n통깨 1스푼\n후추가루 3꼬집\n\n\n#다이어트요리\n#두부요리\n#양배추요리\n#볶음밥\n#두부볶음

Output:
{"food": "두부양배추볶음", "ingredient": ["두부", "양배추", "청양고추"], "seasoning": ["소금", "양조간장", "들기름", "통깨", "후추가루", "tags": "다이어트", "두부", "양배추", "볶음밥", "두부볶음", "title": "두부양배추볶음으로 맛있는 다이어트"}

문제
Input:
title: %s
description: %s

Output:"""

# 재시도 데코레이터 정의
def retry(max_retries=3, wait_seconds=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    print(f"An error occurred: {e}. Retrying {retries}/{max_retries}...")
                    time.sleep(wait_seconds)
            return func(*args, **kwargs)  # 마지막 시도에서도 실패하면 그 결과를 반환
        return wrapper
    return decorator

@retry(max_retries=3, wait_seconds=10)
def call_chatgpt(prompt):
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
    )
    return response


### Main ###
results = []

for json_path in glob("data/*.json"):
    print(json_path)

    with open(json_path) as f:
        videos = json.load(f)

        for video in tqdm(videos):
            try:
                response = call_chatgpt(PROMPT % (video["title"], video["description"]))

                result = {**video, **json.loads(response.choices[0].message.content)}

                results.append(result)
            except Exception as e:
                print("=================================")
                print(f"{video}, {e}")

with open(f'data/results.json', 'w', encoding='utf-8') as file:
    json.dump(results, file, ensure_ascii=False, indent=4)
