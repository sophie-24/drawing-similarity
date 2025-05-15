console.log("✅ server.js 파일 실행됨");

const express = require('express');
const fs = require('fs');
const { execFile } = require('child_process');
const bodyParser = require('body-parser');
const app = express();

app.use(express.static('public'));
app.use(bodyParser.json({ limit: '10mb' }));

let attempts = 0;
const MAX_ATTEMPTS = 3;

app.post('/analyze', (req, res) => {
  const { image, label } = req.body;

  if (!label) {
    return res.status(400).json({ result: '❗ label 정보가 없습니다.' });
  }

  try {
    const imgData = image.replace(/^data:image\/png;base64,/, "");
    fs.writeFileSync('input.png', imgData, 'base64');
    console.log('✅ input.png 저장 완료');

    const pythonPath = 'C:\\Users\\20231\\AppData\\Local\\Programs\\Python\\Python312\\python.exe';
    const scriptPath = 'analyze.py';

    console.log('📍 실행할 Python:', pythonPath);
    console.log('📍 실행할 analyze.py:', scriptPath);

    execFile(pythonPath, [scriptPath, label], (error, stdout, stderr) => {
      console.log('⚙️ execFile 콜백 시작됨');

      if (error) {
        console.error('❌ Python 오류:', error);
        console.error('📄 stderr:', stderr);
        return res.status(500).json({ result: 'Python 실행 오류 발생' });
      }

      console.log("📤 Python 출력:", stdout);

      const output = stdout.trim();
      const match = output.match(/유사도: ([0-9.]+)/);
      const similarity = match ? parseFloat(match[1]) : 0;

      if (similarity >= 0.5) {
        return res.json({
          result: `🎉 성공! 유사도: ${similarity.toFixed(2)}`,
          success: true,
          done: true
        });
      } else {
        attempts++;
        if (attempts >= MAX_ATTEMPTS) {
          return res.json({
            result: `❌ 실패! 유사도: ${similarity.toFixed(2)} / 최대 시도 초과`,
            success: false,
            done: true
          });
        } else {
          return res.json({
            result: `😢 유사도가 부족합니다: ${similarity.toFixed(2)}`,
            done: false,
            remaining: MAX_ATTEMPTS - attempts
          });
        }
      }
    });
  } catch (err) {
    console.error('🔥 try-catch에서 예외 발생:', err);
    return res.status(500).json({ result: '서버 내부 예외 발생' });
  }
});

app.listen(3000, () => {
  console.log('🌐 서버 실행 중: http://localhost:3000');
});
