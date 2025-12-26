# 🎨 Flask 이미지 보정 애플리케이션 MVP

Python Flask 기반의 웹 이미지 편집 애플리케이션입니다. 다양한 필터와 카메라 프로필을 적용하여 이미지를 실시간으로 보정할 수 있습니다.

## ✨ 주요 기능

### 1. 이미지 업로드
- 드래그 앤 드롭 지원
- 다양한 이미지 포맷 지원 (JPG, PNG, GIF, BMP, TIFF, WEBP)
- 최대 16MB 파일 크기 지원
- 자동 이미지 리사이징 (1920x1080 최대 크기)

### 2. 기본 필터
- **밝기 (Brightness)**: 이미지의 전체적인 밝기 조정
- **명암 (Contrast)**: 명암 대비 조정
- **채도 (Saturation)**: 색상의 강도 조정
- **선명도 (Sharpness)**: 이미지의 선명함 조정

### 3. 색 조정
- **색온도 (Temperature)**: 따뜻한 톤 또는 차가운 톤으로 조정
- **색조 (Hue)**: HSV 색상 공간에서 색상 회전
- **HSL 채도**: 세밀한 채도 조정
- **명도 (Lightness)**: HSV 명도 조정

### 4. 카메라 프로필
전문 시네마 카메라의 색상 특성을 재현하는 프로필:

- **ARRI Alexa**: 자연스러운 색상 재현
- **RED Digital Cinema**: 높은 대비와 선명한 색상
- **Canon Cinema**: 따뜻한 톤의 색상
- **Sony Venice**: 균형잡힌 색상 프로필
- **Blackmagic**: 플랫한 프로필

### 5. 보정된 이미지 다운로드
- 고품질 JPEG 포맷으로 저장 (품질 95%)
- 타임스탬프가 포함된 자동 파일명 생성

## 🚀 설치 및 실행

### 필수 요구사항
- Python 3.8 이상
- pip (Python 패키지 관리자)

### 설치 방법

1. 저장소 클론 또는 다운로드

2. 의존성 패키지 설치:
```bash
pip install -r requirements.txt
```

3. 애플리케이션 실행:
```bash
python app.py
```

4. 웹 브라우저에서 접속:
```
http://localhost:5000
```

## 📁 프로젝트 구조

```
.
├── app.py                 # Flask 백엔드 애플리케이션
├── requirements.txt       # Python 의존성 패키지
├── templates/
│   └── index.html        # 메인 HTML 템플릿
├── static/
│   ├── css/
│   │   └── style.css     # 스타일시트
│   └── js/
│       └── app.js        # 프론트엔드 JavaScript
└── uploads/              # 임시 업로드 폴더 (자동 생성)
```

## 🛠️ 기술 스택

### 백엔드
- **Flask 3.0.0**: 경량 웹 프레임워크
- **Pillow (PIL) 10.1.0**: 이미지 처리 라이브러리
- **OpenCV 4.8.1**: 고급 이미지 처리
- **NumPy 1.26.2**: 수치 계산

### 프론트엔드
- **HTML5**: 시맨틱 마크업
- **CSS3**: 모던 스타일링 (Flexbox, Grid)
- **Vanilla JavaScript**: 프레임워크 없는 순수 JS

## 🎯 사용 방법

1. **이미지 업로드**
   - 드래그 앤 드롭 영역에 이미지를 끌어다 놓거나
   - 클릭하여 파일 선택 대화상자에서 이미지 선택

2. **필터 적용**
   - 슬라이더를 조정하여 실시간으로 필터 적용
   - 각 슬라이더의 현재 값이 오른쪽에 표시됨

3. **색 조정**
   - 색온도, 색조, 채도, 명도를 세밀하게 조정
   - 변경사항은 자동으로 적용됨

4. **카메라 프로필 선택**
   - 원하는 카메라 프로필을 선택하여 특정 카메라의 색감 재현
   - 프로필 설명을 참고하여 선택

5. **이미지 다운로드**
   - "다운로드" 버튼을 클릭하여 보정된 이미지 저장
   - 자동으로 타임스탬프가 포함된 파일명으로 저장

6. **초기화**
   - "초기화" 버튼을 클릭하여 모든 조정값을 기본값으로 리셋

## 🔧 API 엔드포인트

### POST /upload
이미지 업로드 엔드포인트

**Request:**
- Content-Type: multipart/form-data
- Body: image file

**Response:**
```json
{
  "success": true,
  "image": "data:image/jpeg;base64,...",
  "width": 1920,
  "height": 1080
}
```

### POST /process
이미지 처리 엔드포인트

**Request:**
```json
{
  "image": "data:image/jpeg;base64,...",
  "adjustments": {
    "brightness": 1.0,
    "contrast": 1.0,
    "saturation": 1.0,
    "sharpness": 1.0,
    "temperature": 0,
    "hue": 0,
    "hsl_saturation": 0,
    "lightness": 0,
    "camera_profile": "arri"
  }
}
```

**Response:**
```json
{
  "success": true,
  "image": "data:image/jpeg;base64,..."
}
```

### POST /download
이미지 다운로드 엔드포인트

**Request:**
```json
{
  "image": "data:image/jpeg;base64,..."
}
```

**Response:**
- Content-Type: image/jpeg
- File download

## 🎨 카메라 프로필 상세

각 카메라 프로필은 실제 시네마 카메라의 색상 특성을 시뮬레이션합니다:

### ARRI Alexa
- 영화 촬영에 널리 사용되는 카메라
- 자연스러운 스킨톤과 부드러운 색상 전환
- 중간 대비, 높은 채도

### RED Digital Cinema
- 디지털 시네마의 선구자
- 높은 대비와 선명한 색상
- 강렬한 레드 톤

### Canon Cinema
- 따뜻한 톤의 색상 재현
- 부드러운 스킨톤
- 중간 대비와 채도

### Sony Venice
- 균형잡힌 색상 프로필
- 다목적 사용에 적합
- 중간 대비와 채도

### Blackmagic
- 플랫한 프로필로 후반 작업에 유리
- 최소한의 색보정
- 낮은 대비

## 🔒 보안 고려사항

- 파일 크기 제한: 16MB
- 허용된 파일 형식만 업로드 가능
- 파일명 보안 처리 (secure_filename)
- 프로덕션 환경에서는 SECRET_KEY 변경 필요

## 📝 개발 노트

### 이미지 처리 파이프라인
1. 이미지 업로드 및 검증
2. RGB 색상 공간으로 변환
3. 크기 조정 (1920x1080 이하)
4. 필터 적용 순서:
   - 밝기
   - 명암
   - 채도
   - 선명도
   - 색온도
   - HSL 조정
   - 카메라 프로필
5. Base64 인코딩 후 전송

### 성능 최적화
- 디바운싱을 통한 API 호출 최소화 (300ms)
- 이미지 자동 리사이징으로 처리 속도 향상
- Base64를 통한 클라이언트-서버 간 이미지 전송

## 🚧 향후 개선 사항

- [ ] 이미지 크롭 기능
- [ ] 회전 및 뒤집기 기능
- [ ] 추가 필터 (빈티지, 블러, 노이즈 등)
- [ ] 프리셋 저장/로드 기능
- [ ] 히스토그램 표시
- [ ] Before/After 비교 슬라이더
- [ ] 배치 처리 기능
- [ ] 사용자 인증 및 이미지 저장
- [ ] WebSocket을 통한 실시간 처리

## 📄 라이선스

이 프로젝트는 교육 목적으로 제작된 MVP입니다.

## 🤝 기여

버그 리포트, 기능 제안, Pull Request는 언제나 환영합니다!

## 📧 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 등록해주세요.
