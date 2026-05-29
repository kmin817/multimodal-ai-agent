import base64
import os
import time
import re
from langchain_ollama import OllamaLLM as Ollama
import pyautogui

def capture_current_screen(filename="current_screen.png"):
    print("-> 현재 화면을 캡처하는 중...")
    screenshot = pyautogui.screenshot()
    screenshot.save(filename)
    return filename

def encode_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def execute_click_action(x, y):
    print(f"-> [ACTION] AI의 지시에 따라 화면의 X: {x}, Y: {y} 좌표를 클릭합니다.")
    pyautogui.moveTo(x, y, duration=1.0)
    pyautogui.click()

def main():
    print("=== 멀티모달 AI 에이전트 루프 시작 ===")
    
    image_path = capture_current_screen()
    base64_image = encode_image(image_path)

    llm = Ollama(model="llava", num_predict=128)
    
    # 1. 프롬프트 강화: 다른 설명 섞지 말라고 엄격하게 제한
    prompt = """
    당신은 사용자의 화면을 제어하는 AI 에이전트입니다.
    현재 화면 스크린샷을 분석하고, 가장 먼저 주목해야 하거나 클릭해야 할 중요한 요소를 하나만 골라주세요.
    
    [중요규칙]
    사고 과정이나 부연 설명은 절대로 하지 마십시오. 오직 아래의 형식만 딱 두 줄 출력하고 답변을 끝내세요.
    
    CLICK_X: [정수값만 입력]
    CLICK_Y: [정수값만 입력]
    """

    print("AI 에이전트가 화면을 분석하고 다음 행동을 고민 중입니다...")
    llm_with_image = llm.bind(images=[base64_image])
    response = llm_with_image.invoke(prompt)

    print("\n=== [AI Agent의 사고 과정 및 판단] ===")
    print(response)
    print("======================================\n")

    # 2. 파싱 로직 강화: 정규표현식으로 문장 속에서 숫자만 추출
    try:
        click_x = None
        click_y = None
        
        for line in response.split('\n'):
            if "CLICK_X:" in line:
                # 'CLICK_X:' 뒤에 나오는 문자열 중 숫자(\d+)만 추출
                numbers = re.findall(r'\d+', line.split("CLICK_X:")[1])
                if numbers:
                    click_x = int(numbers[0])
            if "CLICK_Y:" in line:
                # 'CLICK_Y:' 뒤에 나오는 문자열 중 숫자(\d+)만 추출
                numbers = re.findall(r'\d+', line.split("CLICK_Y:")[1])
                if numbers:
                    click_y = int(numbers[0])

        if click_x is not None and click_y is not None:
            execute_click_action(click_x, click_y)
        else:
            print("[경고] AI 답변에서 구체적인 CLICK_X, CLICK_Y 좌표를 추출하지 못했습니다.")
            
    except Exception as e:
        print(f"[오류 발생] 행동을 실행하는 중 문제가 발생했습니다: {e}")

    if os.path.exists(image_path):
        os.remove(image_path)

if __name__ == "__main__":
    main()
