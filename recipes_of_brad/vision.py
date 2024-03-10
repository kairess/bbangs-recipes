import base64
import requests
import json

# OpenAI API Key
api_key = "YOUR_API_KEY"

PROMPT = """1. 사진에 나와있는 음식 재료들을 전부 알려줘.
2. 양념, 조미료 등을 제외한 원재료들만 알려줘.
3. 출력은 json 형태로 하고 원재료들을 1차원 리스트 형태로 반환해줘. 아래는 예시임.
["빵", "파스타", "파인애플", "상추", "레몬", "사과", "방울토마토", "브로콜리", "파프리카", "당근", "버섯"]
4. 다른 말은 필요없이 간단하게 JSON만 반환해줘."""

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

def get_response(image_path):
    base64_image = encode_image(image_path)

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [{
            "role": "user",
            "content": [{
                "type": "text",
                "text": f"{PROMPT}",
            }, {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            }]
        }],
        "max_tokens": 300,
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    try:
        # 응답에서 content 문자열을 추출
        content = response.json()['choices'][0]['message']['content']

        # json 형식 문자열 정제
        json_str = content.replace('```json', '').replace('```', '').strip()
        
        # 파이썬 배열로 파싱
        data = json.loads(json_str)

        # 결과 출력
        return data
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return False

if __name__ == "__main__":
    r = get_response("2.png")
    print(r)
