# 이미지 업로드 시스템 가이드

S3 Presigned URL을 사용한 이미지 업로드 시스템입니다.

## 🏗️ 아키텍처

```
Frontend (Nginx)
    ↓ HTTP 요청
API Server (FastAPI)
    ↓ Presigned URL 생성
AWS S3 (Object Storage)
    ↑ 직접 업로드
Client (Browser)
```

## 📁 프로젝트 구조

```
testweb-dev/
├── backend/              # API 서버
│   ├── main.py          # FastAPI 애플리케이션
│   ├── requirements.txt # Python 의존성
│   ├── Dockerfile       # 백엔드 이미지 빌드
│   └── README.md        # API 문서
├── web/                 # 프론트엔드
│   ├── index.html       # 테트리스 게임
│   └── upload.html      # 이미지 업로드 페이지
├── Dockerfile           # 웹서버 이미지 빌드
└── .github/workflows/   # CI/CD
    ├── build-and-push.yml      # 웹서버 빌드
    └── build-backend.yml       # 백엔드 빌드

testweb-ops/
├── k8s/                 # Kubernetes 매니페스트
│   └── backend-api.yaml # API 서버 배포
└── argocd/             # ArgoCD Applications
    └── backend-api.yaml
```

## 🚀 배포 순서

### 1. AWS S3 버킷 확인

AWS S3 버킷이 이미 생성되어 있는지 확인:
- 버킷 이름: `hyjk826-mlops-1011`
- 리전: `ap-northeast-2`
- 버킷이 없으면 AWS Console에서 생성 필요

### 2. 백엔드 API 배포

```bash
# 백엔드 이미지 빌드 및 푸시 (GitHub Actions 자동)
# 또는 수동 빌드:
cd testweb-dev/backend
docker build -t ghcr.io/hyjk826/testweb-dev-backend:latest .
docker push ghcr.io/hyjk826/testweb-dev-backend:latest

# Kubernetes에 배포
kubectl apply -f testweb-ops/k8s/backend-api.yaml

# 또는 ArgoCD로 배포
kubectl apply -f testweb-ops/argocd/backend-api.yaml
```

### 4. 웹서버 배포

기존 웹서버 배포 프로세스 사용 (testweb-ops의 기존 워크플로우 사용)

## 📝 사용 방법

### 프론트엔드 접속

1. **이미지 업로드 페이지**: `http://웹서버주소/upload.html`
2. **기능**:
   - 드래그 앤 드롭 또는 클릭하여 이미지 선택
   - 자동으로 Presigned URL 생성 및 업로드
   - 업로드된 이미지 갤러리 확인
   - 이미지 삭제

### API 사용 예시

#### Presigned URL 생성
```javascript
const response = await fetch('http://api.example.com/api/presigned-url', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    filename: 'image.jpg',
    content_type: 'image/jpeg'
  })
});

const { upload_url, object_key } = await response.json();
```

#### S3에 직접 업로드
```javascript
const file = document.getElementById('fileInput').files[0];
await fetch(upload_url, {
  method: 'PUT',
  body: file,
  headers: { 'Content-Type': file.type }
});
```

## 🔧 설정

### 환경 변수

#### 백엔드 API
```env
# AWS S3 사용 시: S3_ENDPOINT_URL은 설정하지 않음 (자동 감지)
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_REGION=ap-northeast-2
S3_BUCKET_NAME=hyjk826-mlops-1011
PRESIGNED_URL_EXPIRATION=3600
CORS_ORIGINS=http://localhost:8080
```

### 프론트엔드 API URL 수정

`web/upload.html` 파일에서:
```javascript
const API_BASE_URL = 'http://api.example.com/api'; // 실제 API 주소로 변경
```

## 🔍 문제 해결

### AWS S3 접속 오류
- AWS 인증 정보 확인 (Access Key, Secret Key)
- 버킷 이름 확인 (`hyjk826-mlops-1011`)
- 버킷이 존재하는지 AWS Console에서 확인
- IAM 권한 확인 (s3:PutObject, s3:GetObject, s3:DeleteObject, s3:ListBucket)

### 백엔드 API 오류
```bash
kubectl logs -f deployment/backend-api -n image-upload
kubectl get pods -n image-upload
```

### CORS 오류
- `backend-api.yaml`의 `CORS_ORIGINS` 환경 변수 확인
- 프론트엔드 도메인과 일치하는지 확인

## 📊 모니터링

### 리소스 확인
```bash
# 모든 리소스 확인
kubectl get all -n image-upload

# 로그 확인
kubectl logs -f deployment/backend-api -n image-upload
```

## 🎯 다음 단계

- [ ] 인증 시스템 추가 (JWT)
- [ ] 이미지 리사이징/최적화
- [ ] CDN 연동
- [ ] 모니터링/알림 설정
