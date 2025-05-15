console.log("✅ server.js 파일 실행됨");

const express = require('express');
const fs = require('fs');
const { execFile } = require('child_process');
const bodyParser = require('body-parser');
const app = express();

app.use(express.static('public'));
app.use(bodyParser.json({ limit: '10mb' }));

app.post('/analyze', (req, res) => {
  const { image, label } = req.body;

  if (!label) {
    return res.status(400).json({ result: '❗ label 정보가 없습니다.' });
  }

  try {
    // 1. input.png 저장
    const imgData = image.replace(/^data:image\/png;base64,/, "");
    fs.writeFileSync('input.png', imgData, 'base64');
    console.log('✅ input.png 저장 완료');

    // 2. Python 실행 경로 + 스크립트
   const pythonPath = 'venv310\\Scripts\\python.exe'; 
   const scriptPath = 'predict.py';

    console.log('📍 실행할 Python:', pythonPath);
    console.log('📍 실행할 스크립트:', scriptPath);

    execFile(pythonPath, [scriptPath, label], (error, stdout, stderr) => {
      console.log('⚙️ execFile 콜백 시작됨');

      if (error) {
        console.error('❌ Python 실행 오류:', error);
        console.error('📄 stderr:', stderr);
        return res.status(500).json({ result: 'Python 실행 중 오류 발생' });
      }

      const output = stdout.trim();
      console.log('📤 Python 출력:', output);

      // ✅ 예측 결과 파싱
      const success = output.includes("✅ 성공");
      const match = output.match(/예측: (\w+) \(([\d.]+)\)/);

      if (success && match) {
        const pred = match[1];
        const conf = parseFloat(match[2]);
        return res.json({
          result: `🎯 예측된 그림: ${pred} / 정확도: ${conf.toFixed(2)}`,
          success: true,
          done: true
        });
      } else {
        return res.json({
          result: `❌ 인식 실패: ${output}`,
          success: false,
          done: true
        });
      }
    });

  } catch (err) {
    console.error('🔥 try-catch 예외 발생:', err);
    return res.status(500).json({ result: '서버 내부 오류 발생' });
  }
});

app.listen(3000, () => {
  console.log('🌐 서버 실행 중: http://localhost:3000');
});
