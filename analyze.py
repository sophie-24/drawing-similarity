import sys
import json
import numpy as np
import cv2
from PIL import Image, ImageDraw
from skimage.metrics import structural_similarity as ssim

# 💡 1. 명령줄 인자로 label 받기
if len(sys.argv) < 2:
    print("❗ 주제를 전달받지 못했습니다.")
    sys.exit(1)

label = sys.argv[1]  # 예: 'apple'
path = f"data/{label}.ndjson"

# 💡 2. 해당 주제 데이터 로드
try:
    with open(path, 'r') as f:
        drawings = [json.loads(line)["drawing"] for line in f][:100]
except FileNotFoundError:
    print(f"❌ 파일을 찾을 수 없습니다: {path}")
    sys.exit(1)

# 💡 3. 벡터 그림을 흑백 이미지로 변환
def draw_strokes(strokes, size=256, line_width=6):
    img = Image.new("L", (size, size), color=255)
    draw = ImageDraw.Draw(img)
    for stroke in strokes:
        for i in range(len(stroke[0]) - 1):
            draw.line(
                [(stroke[0][i], stroke[1][i]), (stroke[0][i + 1], stroke[1][i + 1])],
                fill=0, width=line_width
            )
    return np.array(img)

# 💡 4. 웹캠 이미지 로드 + 전처리
input_img = cv2.imread("input.png", cv2.IMREAD_GRAYSCALE)
if input_img is None:
    print("❌ input.png 파일을 찾을 수 없습니다.")
    sys.exit(1)

# 크기 통일
input_img = cv2.resize(input_img, (256, 256))

# 엣지 감지 후 반전하여 흰 배경 + 검정 선
edges = cv2.Canny(input_img, 100, 200)
input_img = cv2.bitwise_not(edges)

# 💡 5. 평균 SSIM 유사도 계산
sims = []
for d in drawings:
    d_img = draw_strokes(d)
    # SSIM 계산 시 dtype과 data_range 명확히 설정
    s = ssim(input_img, d_img, data_range=255)
    sims.append(s)

score = np.mean(sims)

# 💡 6. 결과 출력 (서버.js에서 유사도 파싱할 수 있게 포맷 통일)
print(f"판별: {label} / 유사도: {score:.2f}")

cv2.imshow("웹캠 입력", input_img)
cv2.imshow("예시 벡터 그림", d_img)
cv2.waitKey(0)
cv2.destroyAllWindows()
