# 📡 API 문서

Flask 이미지 보정 애플리케이션의 REST API 엔드포인트 문서입니다.

## 기본 정보

- **Base URL**: `http://localhost:5000`
- **Content-Type**: `application/json` (POST 요청 시)
- **파일 업로드**: `multipart/form-data`

## 엔드포인트

### 1. 홈페이지

메인 웹 인터페이스를 렌더링합니다.

```
GET /
```

**응답**
- Status: 200 OK
- Content-Type: text/html
- Body: HTML 페이지

---

### 2. 이미지 업로드

이미지 파일을 업로드하고 Base64로 인코딩된 결과를 반환합니다.

```
POST /upload
```

**요청**

Content-Type: `multipart/form-data`

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| image | File | 예 | 업로드할 이미지 파일 |

**지원 포맷**
- JPG / JPEG
- PNG
- GIF
- BMP
- TIFF
- WEBP

**최대 파일 크기**: 16MB

**응답**

```json
{
  "success": true,
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
  "width": 1920,
  "height": 1080
}
```

**에러 응답**

```json
{
  "error": "No image file provided"
}
```

Status Codes:
- `200`: 성공
- `400`: 잘못된 요청 (파일 없음, 잘못된 형식)
- `500`: 서버 에러

**예시 (cURL)**

```bash
curl -X POST http://localhost:5000/upload \
  -F "image=@/path/to/image.jpg"
```

**예시 (JavaScript)**

```javascript
const formData = new FormData();
formData.append('image', fileInput.files[0]);

const response = await fetch('/upload', {
    method: 'POST',
    body: formData
});

const data = await response.json();
console.log(data.image); // Base64 이미지
```

---

### 3. 이미지 처리

업로드된 이미지에 필터와 조정을 적용합니다.

```
POST /process
```

**요청**

Content-Type: `application/json`

```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
  "adjustments": {
    "brightness": 1.2,
    "contrast": 1.1,
    "saturation": 1.0,
    "sharpness": 1.0,
    "temperature": 0.2,
    "hue": 10,
    "hsl_saturation": 0.1,
    "lightness": 0.05,
    "camera_profile": "arri"
  }
}
```

**파라미터**

| 파라미터 | 타입 | 범위 | 기본값 | 설명 |
|---------|------|------|--------|------|
| image | String | - | 필수 | Base64 인코딩된 이미지 |
| adjustments | Object | - | 필수 | 조정 파라미터 객체 |

**Adjustments 객체**

| 속성 | 타입 | 범위 | 기본값 | 설명 |
|------|------|------|--------|------|
| brightness | Float | 0.0 - 2.0 | 1.0 | 밝기 (1.0 = 원본) |
| contrast | Float | 0.0 - 2.0 | 1.0 | 명암 (1.0 = 원본) |
| saturation | Float | 0.0 - 2.0 | 1.0 | 채도 (1.0 = 원본) |
| sharpness | Float | 0.0 - 2.0 | 1.0 | 선명도 (1.0 = 원본) |
| temperature | Float | -1.0 - 1.0 | 0.0 | 색온도 (0 = 원본, + = 따뜻, - = 차가움) |
| hue | Integer | -180 - 180 | 0 | 색조 회전 (도 단위) |
| hsl_saturation | Float | -1.0 - 1.0 | 0.0 | HSL 채도 조정 |
| lightness | Float | -1.0 - 1.0 | 0.0 | 명도 조정 |
| camera_profile | String | - | "" | 카메라 프로필 이름 |

**카메라 프로필**

| 값 | 설명 |
|----|------|
| "" (빈 문자열) | 프로필 없음 |
| "arri" | ARRI Alexa 프로필 |
| "red" | RED Digital Cinema 프로필 |
| "canon" | Canon Cinema 프로필 |
| "sony" | Sony Venice 프로필 |
| "blackmagic" | Blackmagic 프로필 |

**응답**

```json
{
  "success": true,
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
}
```

**에러 응답**

```json
{
  "error": "Failed to process image: [error message]"
}
```

Status Codes:
- `200`: 성공
- `500`: 서버 에러

**예시 (JavaScript)**

```javascript
const response = await fetch('/process', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        image: originalImageBase64,
        adjustments: {
            brightness: 1.2,
            contrast: 1.1,
            saturation: 1.0,
            sharpness: 1.0,
            temperature: 0,
            hue: 0,
            hsl_saturation: 0,
            lightness: 0,
            camera_profile: 'arri'
        }
    })
});

const data = await response.json();
previewImage.src = data.image;
```

**예시 (Python)**

```python
import requests
import json

url = 'http://localhost:5000/process'
data = {
    'image': 'data:image/jpeg;base64,...',
    'adjustments': {
        'brightness': 1.2,
        'contrast': 1.1,
        'saturation': 1.0,
        'sharpness': 1.0,
        'temperature': 0.2,
        'hue': 10,
        'hsl_saturation': 0.1,
        'lightness': 0.05,
        'camera_profile': 'arri'
    }
}

response = requests.post(url, json=data)
result = response.json()
print(result['image'])
```

---

### 4. 이미지 다운로드

처리된 이미지를 다운로드합니다.

```
POST /download
```

**요청**

Content-Type: `application/json`

```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
}
```

**파라미터**

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| image | String | 예 | Base64 인코딩된 이미지 |

**응답**

- Status: 200 OK
- Content-Type: image/jpeg
- Content-Disposition: attachment; filename="edited_image_[timestamp].jpg"
- Body: 바이너리 이미지 데이터

**에러 응답**

```json
{
  "error": "Failed to download image: [error message]"
}
```

Status Codes:
- `200`: 성공
- `500`: 서버 에러

**예시 (JavaScript)**

```javascript
const response = await fetch('/download', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        image: processedImageBase64
    })
});

if (response.ok) {
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `edited_image_${Date.now()}.jpg`;
    a.click();
    window.URL.revokeObjectURL(url);
}
```

**예시 (Python)**

```python
import requests

url = 'http://localhost:5000/download'
data = {
    'image': 'data:image/jpeg;base64,...'
}

response = requests.post(url, json=data)

if response.status_code == 200:
    with open('downloaded_image.jpg', 'wb') as f:
        f.write(response.content)
```

---

## 에러 코드

| 코드 | 설명 |
|------|------|
| 200 | 성공 |
| 400 | 잘못된 요청 (파일 없음, 잘못된 형식 등) |
| 413 | 요청 엔티티가 너무 큼 (16MB 초과) |
| 500 | 내부 서버 에러 |

## 제한사항

- **파일 크기**: 최대 16MB
- **동시 요청**: 서버 설정에 따라 다름 (기본: 제한 없음)
- **Rate Limiting**: 기본적으로 설정되지 않음 (프로덕션에서 설정 권장)

## 성능 고려사항

### 처리 시간

이미지 처리 시간은 다음 요소에 따라 달라집니다:

- 이미지 크기 (큰 이미지 = 긴 처리 시간)
- 적용된 필터 수
- 서버 성능

**평균 처리 시간**:
- 1920x1080: ~500ms
- 3840x2160: ~2000ms

### 최적화 팁

1. **이미지 크기 제한**: 큰 이미지는 업로드 전 클라이언트에서 리사이즈
2. **디바운싱**: 슬라이더 조정 시 API 호출을 지연시켜 요청 수 감소
3. **캐싱**: 동일한 조정값에 대해 결과 캐싱
4. **WebSocket**: 실시간 처리를 위해 WebSocket 사용 고려

## 보안

### CORS

기본적으로 CORS는 설정되어 있지 않습니다. 다른 도메인에서 API를 사용하려면 CORS 설정이 필요합니다.

### 인증

현재 버전에서는 인증이 구현되어 있지 않습니다. 프로덕션 환경에서는 다음을 고려하세요:

- API 키 인증
- JWT 토큰
- OAuth 2.0

### Rate Limiting

API 남용을 방지하기 위해 Rate Limiting 구현을 권장합니다.

## 버전 정보

- **API 버전**: 1.0
- **Flask 버전**: 3.0.0
- **마지막 업데이트**: 2024

## 지원

문제가 발생하거나 질문이 있으면 GitHub 이슈를 등록해주세요.
