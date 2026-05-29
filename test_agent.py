import base64
from langchain_community.llms import Ollama

# 이미지를 Base64 스트링으로 변환하는 함수
def encode_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def main():
    # 아까 준비한 이미지 파일 이름으로 매칭
    image_path = "CCTV16.jpg" 

    try:
        base64_image = encode_image(image_path)
        print("1. 이미지 인코딩 완료.")
    except FileNotFoundError:
        print(f"[오류] 폴더에 {image_path} 파일이 없습니다!")
        return

    print("2. 로컬 LLaVA 모델 호출 중...")
    llm = Ollama(model="llava")

    # 에이전트가 상황을 파악하기 위한 질문
    prompt = "이 이미지에 무엇이 보이나요? 주요 객체와 배경을 스스로 분석해서 판단 결과를 알려주세요."

    print("3. AI 에이전트가 이미지를 자율 분석 중입니다...\n")
    llm_with_image = llm.bind(images=[base64_image])
    response = llm_with_image.invoke(prompt)

    print("=== [AI Agent 판단 결과] ===")
    print(response)

if __name__ == "__main__":
    main()
