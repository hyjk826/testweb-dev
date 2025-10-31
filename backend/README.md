# 이미지 업로드 API 서버

S3 Presigned URL을 사용한 이미지 업로드 API 서버입니다.

## 기능

- ✅ Presigned URL 생성 (클라이언트가 직접 S3에 업로드)
- ✅ 이미지 목록 조회
- ✅ 이미지 삭제
- ✅ AWS S3 호환

## API 엔드포인트

### 1. 헬스 체크
```
GET /api/health
```

### 2. Presigned URL 생성
```
POST /api/presigned-url
Content-Type: application/json

{
  "filename": "image.jpg",
  "content_type": "image/jpeg"
}

Response:
{
  "upload_url": "https://...",
  "download_url": "https://...",
  "object_key": "uploads/uuid.jpg",
  "expires_in": 3600
}
```

### 3. 이미지 목록 조회
```
GET /api/list-images?limit=100
```

### 4. 이미지 삭제
```
DELETE /api/delete-image/{object_key}
```

## 환경 변수

```env
# AWS S3 사용 시: S3_ENDPOINT_URL은 설정하지 않음 (자동 감지)
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_REGION=ap-northeast-2
S3_BUCKET_NAME=hyjk826-mlops-1011
PRESIGNED_URL_EXPIRATION=3600
CORS_ORIGINS=http://localhost:8080
PORT=8000
```

## 로컬 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp env.example .env
# .env 파일 수정

# 서버 실행
uvicorn main:app --reload --port 8000
```

## Docker 빌드

```bash
docker build -t image-upload-api:latest .
docker run -p 8000:8000 --env-file .env image-upload-api:latest
```

## Kubernetes 배포

```bash
kubectl apply -f ../testweb-ops/k8s/backend-api.yaml
```
