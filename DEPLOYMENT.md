# 🚀 배포 가이드

Flask 이미지 보정 애플리케이션을 프로덕션 환경에 배포하는 방법입니다.

## 프로덕션 배포 옵션

### 옵션 1: Gunicorn (권장)

#### 1단계: Gunicorn 설치

```bash
pip install gunicorn
```

#### 2단계: 실행

```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

옵션 설명:
- `-w 4`: 4개의 워커 프로세스
- `-b 0.0.0.0:8000`: 모든 인터페이스의 8000번 포트에서 수신
- `app:app`: app.py 파일의 app 객체

#### 3단계: systemd 서비스 설정 (선택사항)

`/etc/systemd/system/flask-image-editor.service` 파일 생성:

```ini
[Unit]
Description=Flask Image Editor Application
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/project
Environment="PATH=/path/to/project/venv/bin"
ExecStart=/path/to/project/venv/bin/gunicorn -w 4 -b 0.0.0.0:8000 app:app

[Install]
WantedBy=multi-user.target
```

서비스 시작:

```bash
sudo systemctl start flask-image-editor
sudo systemctl enable flask-image-editor
```

### 옵션 2: uWSGI

#### 1단계: uWSGI 설치

```bash
pip install uwsgi
```

#### 2단계: 설정 파일 생성 (uwsgi.ini)

```ini
[uwsgi]
module = app:app
master = true
processes = 4
socket = 0.0.0.0:8000
chmod-socket = 660
vacuum = true
die-on-term = true
```

#### 3단계: 실행

```bash
uwsgi --ini uwsgi.ini
```

### 옵션 3: Docker

#### Dockerfile 예시

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

#### 빌드 및 실행

```bash
docker build -t flask-image-editor .
docker run -d -p 5000:5000 flask-image-editor
```

## Nginx 리버스 프록시 설정

프로덕션 환경에서는 Nginx를 리버스 프록시로 사용하는 것을 권장합니다.

### Nginx 설정 예시

`/etc/nginx/sites-available/flask-image-editor`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
    }

    location /static {
        alias /path/to/project/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

Nginx 설정 활성화:

```bash
sudo ln -s /etc/nginx/sites-available/flask-image-editor /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## SSL/TLS 설정 (HTTPS)

### Let's Encrypt 사용

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

자동 갱신 설정:

```bash
sudo certbot renew --dry-run
```

## 환경 변수 설정

프로덕션 환경에서는 환경 변수를 사용하여 민감한 정보를 관리합니다.

`.env` 파일 생성:

```bash
SECRET_KEY=your-super-secret-key-here
FLASK_ENV=production
MAX_CONTENT_LENGTH=16777216
```

`.env` 파일 로드 (python-dotenv 사용):

```bash
pip install python-dotenv
```

`app.py`에 추가:

```python
from dotenv import load_dotenv
load_dotenv()
```

## 성능 최적화

### 1. 이미지 캐싱

Redis를 사용한 결과 캐싱:

```bash
pip install redis
```

### 2. CDN 사용

정적 파일(CSS, JS)을 CDN으로 서빙하여 성능 향상

### 3. 로드 밸런싱

여러 인스턴스를 실행하고 Nginx로 로드 밸런싱

```nginx
upstream flask_app {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    location / {
        proxy_pass http://flask_app;
    }
}
```

## 모니터링

### 로깅 설정

`app.py`에 추가:

```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Flask Image Editor startup')
```

### 애플리케이션 모니터링

- **Prometheus + Grafana**: 메트릭 수집 및 시각화
- **Sentry**: 에러 추적
- **New Relic**: APM (Application Performance Monitoring)

## 보안 고려사항

### 1. SECRET_KEY 변경

프로덕션 환경에서 반드시 강력한 SECRET_KEY 사용:

```python
import secrets
print(secrets.token_hex(32))
```

### 2. CORS 설정

다른 도메인에서 접근이 필요한 경우:

```bash
pip install flask-cors
```

```python
from flask_cors import CORS
CORS(app, resources={r"/*": {"origins": "https://your-domain.com"}})
```

### 3. Rate Limiting

API 남용 방지:

```bash
pip install flask-limiter
```

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

### 4. 입력 검증

파일 업로드 시 추가 검증:

- 파일 매직 넘버 확인
- 이미지 콘텐츠 검증
- 파일명 살균 처리

## 클라우드 배포

### AWS (EC2)

1. EC2 인스턴스 생성 (Ubuntu 22.04)
2. 보안 그룹 설정 (포트 80, 443 개방)
3. 애플리케이션 배포
4. Elastic Load Balancer 설정 (선택사항)

### Google Cloud Platform (App Engine)

`app.yaml` 생성:

```yaml
runtime: python311
entrypoint: gunicorn -b :$PORT app:app

instance_class: F2

automatic_scaling:
  target_cpu_utilization: 0.65
  min_instances: 1
  max_instances: 10
```

배포:

```bash
gcloud app deploy
```

### Heroku

1. Heroku CLI 설치
2. `Procfile` 생성:

```
web: gunicorn app:app
```

3. 배포:

```bash
heroku create your-app-name
git push heroku main
```

### DigitalOcean App Platform

1. GitHub 저장소 연결
2. 자동 배포 설정
3. 환경 변수 설정

## 백업 전략

### 데이터베이스 백업 (향후 구현 시)

```bash
# 매일 자동 백업 cron 작업
0 2 * * * /path/to/backup-script.sh
```

### 애플리케이션 백업

- 코드: Git 저장소
- 업로드된 이미지: S3 또는 클라우드 스토리지
- 설정 파일: 버전 관리

## 업데이트 절차

1. 새 코드를 Git에서 pull
2. 의존성 업데이트: `pip install -r requirements.txt`
3. 데이터베이스 마이그레이션 (필요시)
4. 애플리케이션 재시작: `sudo systemctl restart flask-image-editor`
5. 로그 확인: `sudo journalctl -u flask-image-editor -f`

## 문제 해결

### 메모리 부족

워커 수를 줄이거나 인스턴스 크기 증가

### 느린 응답

- 이미지 처리 작업을 Celery로 비동기 처리
- Redis 캐싱 도입
- CDN 사용

### 업로드 실패

- Nginx `client_max_body_size` 확인
- Flask `MAX_CONTENT_LENGTH` 설정 확인

## 추가 리소스

- [Flask Deployment Options](https://flask.palletsprojects.com/en/latest/deploying/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
