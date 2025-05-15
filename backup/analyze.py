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

# 💡 2. 데이터 로드 (20개만 사용)
try:
    with open(path, 'r') as f:
        drawings = [json.loads(line)["drawing"] for line in f][:20]
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

# 💡 4. 입력 이미지 전처리
input_img = cv2.imread("input.png", cv2.IMREAD_GRAYSCALE)
if input_img is None:
    print("❌ input.png 파일을 찾을 수 없습니다.")
    sys.exit(1)

# 크기 통일 + 이진화(반전된 선 강조)
input_img = cv2.resize(input_img, (256, 256))

input_img = cv2.adaptiveThreshold(input_img, 255,
                                  cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                  cv2.THRESH_BINARY_INV,
                                  11, 2)
# 💡 5. 유사도 계산
sims = []
for d in drawings:
    d_img = draw_strokes(d)

    _, d_img = cv2.threshold(d_img, 180, 255, cv2.THRESH_BINARY_INV)
    
    s = ssim(input_img, d_img, data_range=255)
    sims.append(s)

score = np.mean(sims)
print(f"판별: {label} / 유사도: {score:.2f}")
