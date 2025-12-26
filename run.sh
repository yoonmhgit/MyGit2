#!/bin/bash

# Flask 이미지 보정 애플리케이션 실행 스크립트

set -e

echo "🎨 Flask 이미지 보정 애플리케이션"
echo "================================="
echo ""

# 가상환경 존재 여부 확인
if [ ! -d "venv" ]; then
    echo "📦 가상환경을 생성합니다..."
    python3 -m venv venv
    echo "✅ 가상환경이 생성되었습니다."
    echo ""
fi

# 가상환경 활성화
echo "🔧 가상환경을 활성화합니다..."
source venv/bin/activate

# 의존성 패키지 설치
echo "📥 의존성 패키지를 설치합니다..."
pip install -q -r requirements.txt

echo "✅ 모든 패키지가 설치되었습니다."
echo ""

# 업로드 폴더 생성
mkdir -p uploads

echo "🚀 Flask 애플리케이션을 시작합니다..."
echo ""
echo "브라우저에서 다음 주소로 접속하세요:"
echo "👉 http://localhost:5000"
echo ""
echo "종료하려면 Ctrl+C를 누르세요."
echo ""

# Flask 앱 실행
python app.py
