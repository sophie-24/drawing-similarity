import sys
import cv2
import numpy as np
from tensorflow.keras.models import load_model

# 💡 1. 인자로 받은 label 가져오기
if len(sys.argv) < 2:
    print("❗ 주제를 전달받지 못했습니다.")
    sys.exit(1)

label = sys.argv[1]
label_list = ['apple', 'computer', 'cat', 'fish', 'car']  # 모델의 클래스 순서

# 💡 2. 모델 로딩
try:
    model = load_model("model/quickdraw_model.keras")
except Exception as e:
    print("❌ 모델 로딩 실패:", str(e))
    sys.exit(1)

# 💡 3. input.png 불러오기
img = cv2.imread("input.png", cv2.IMREAD_GRAYSCALE)
if img is None:
    print("❌ input.png 파일을 찾을 수 없습니다.")
    sys.exit(1)

# 💡 4. 전처리
# 1. 흑백 변환 & 이진화
img = cv2.resize(img, (28, 28))
_, img = cv2.threshold(img, 180, 255, cv2.THRESH_BINARY_INV)

# 💡 5. 윤곽선 찾기 (가장 큰 것 1개만 사용)
contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
if contours:
    x, y, w, h = cv2.boundingRect(max(contours, key=cv2.contourArea))
    img = img[y:y+h, x:x+w]  # crop
else:
    print("❌ 윤곽선을 찾을 수 없습니다.")
    sys.exit(1)

# 모델 입력 형태로 변환 (크기 통일)
img = cv2.resize(img, (28, 28))
img = img.reshape(1, 28, 28, 1) / 255.0

# 💡 5. 예측
pred = model.predict(img)
pred_index = np.argmax(pred)
pred_label = label_list[pred_index]
confidence = float(np.max(pred))

# 💡 6. 결과 출력 (stdout → server.js가 읽음)
print(f"예측: {pred_label} ({confidence:.2f})")

if pred_label == label: 
    #유예조건을 낮춤 / 정답과 일치 여부만 판단
    print("✅ 성공")
else:
    print("❌ 실패")
