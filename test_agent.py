import base64
import re
import time
import pyautogui
from langchain_ollama import OllamaLLM as Ollama
from langchain_core.messages import HumanMessage


def capture_current_screen(filename="current_screen.png"):
    print("-> 3초 후 캡처합니다. 토끼가 보이는 화면으로 전환하세요...")
    time.sleep(3)
    screenshot = pyautogui.screenshot()
    screenshot.save(filename)
    print("-> 캡처 완료!")
    return filename


def encode_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


def move_to_target(x, y):
    print(f"-> [ACTION] X: {x}, Y: {y} 로 마우스 이동")
    pyautogui.moveTo(x, y, duration=1.5)


def parse_coordinates(response: str):
    x_match = re.search(r'CLICK_X\s*:\s*([0-1]?\.\d+)', response)
    y_match = re.search(r'CLICK_Y\s*:\s*([0-1]?\.\d+)', response)

    if x_match and y_match:
        return float(x_match.group(1)), float(y_match.group(1))
    return None, None


def main():
    print("=== 토끼 탐지 에이전트 시작 ===")

    image_path = capture_current_screen()
    base64_image = encode_image(image_path)

    llm = Ollama(model="minicpm-v", num_predict=128, temperature=0.0)


    prompt = """Look at this screenshot very carefully.

There should be a rabbit (small furry animal with long ears) somewhere in the image.
Find it and tell me its location.

Output ONLY:
FOUND: YES
CLICK_X: [horizontal ratio 0.0~1.0, 0.0=left edge, 1.0=right edge]
CLICK_Y: [vertical ratio 0.0~1.0, 0.0=top edge, 1.0=bottom edge]

If absolutely no rabbit exists:
FOUND: NO"""

    message = HumanMessage(
        content=[
            {
                "type": "image_url",
                "image_url": f"data:image/png;base64,{base64_image}",
            },
            {"type": "text", "text": prompt},
        ]
    )

    print("AI가 화면에서 토끼를 탐색 중...")
    response = llm.invoke([message])

    print("\n=== [AI 응답] ===")
    print(response)
    print("=================\n")

    try:
        # 토끼 발견 여부 확인
        if "FOUND: NO" in response.upper():
            print("[결과] 화면에서 토끼를 찾지 못했습니다.")
            return

        screen_width, screen_height = pyautogui.size()
        click_x_ratio, click_y_ratio = parse_coordinates(response)

        if click_x_ratio is not None and click_y_ratio is not None:
            click_x_ratio = max(0.01, min(0.99, click_x_ratio))
            click_y_ratio = max(0.01, min(0.99, click_y_ratio))

            click_x = int(click_x_ratio * screen_width)
            click_y = int(click_y_ratio * screen_height)

            print(f"[결과] 토끼 발견! 비율({click_x_ratio:.3f}, {click_y_ratio:.3f}) → 픽셀({click_x}, {click_y})")
            move_to_target(click_x, click_y)
        else:
            print("[경고] 좌표 파싱 실패. AI 응답을 확인하세요.")

    except Exception as e:
        print(f"[오류] {e}")


if __name__ == "__main__":
    main()