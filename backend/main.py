from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import timedelta
import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv
import uuid
from typing import Optional

load_dotenv()
app = FastAPI(title="Image Upload API", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:8080").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# S3 클라이언트 설정
# AWS S3 사용 시: S3_ENDPOINT_URL을 비워두거나 None으로 설정
# MinIO 사용 시: S3_ENDPOINT_URL에 MinIO 엔드포인트 설정
endpoint_url = os.getenv("S3_ENDPOINT_URL")
if endpoint_url and endpoint_url.strip():
    endpoint_url = endpoint_url
else:
    endpoint_url = None  # None이면 자동으로 AWS S3 사용

s3_client = boto3.client(
    's3',
    endpoint_url=endpoint_url,  # None이면 AWS S3, 값이 있으면 MinIO 등 커스텀 엔드포인트
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION", "ap-northeast-2")
)

BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "hyjk826-mlops-1011")  # 기본 버킷 이름
PRESIGNED_URL_EXPIRATION = int(os.getenv("PRESIGNED_URL_EXPIRATION", "3600"))  # 1시간


class PresignedUrlRequest(BaseModel):
    filename: str
    content_type: str = "image/jpeg"


class UploadCompleteRequest(BaseModel):
    filename: str
    object_key: str


@app.get("/api/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy", "service": "image-upload-api"}


@app.post("/api/presigned-url")
async def generate_presigned_url(request: PresignedUrlRequest):
    """
    Presigned URL 생성
    클라이언트가 이미지를 직접 S3에 업로드할 수 있는 URL 반환
    """
    try:
        # 파일 확장자 추출
        file_extension = request.filename.split('.')[-1] if '.' in request.filename else 'jpg'
        
        # 고유한 객체 키 생성 (UUID 사용)
        object_key = f"uploads/{uuid.uuid4()}.{file_extension}"
        
        # Presigned URL 생성 (PUT 요청용)
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': BUCKET_NAME,
                'Key': object_key,
                'ContentType': request.content_type
            },
            ExpiresIn=PRESIGNED_URL_EXPIRATION
        )
        
        # 다운로드용 Presigned URL도 생성 (선택사항)
        download_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': BUCKET_NAME,
                'Key': object_key
            },
            ExpiresIn=PRESIGNED_URL_EXPIRATION
        )
        
        return {
            "upload_url": presigned_url,
            "download_url": download_url,
            "object_key": object_key,
            "expires_in": PRESIGNED_URL_EXPIRATION
        }
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"S3 오류: {str(e)}")


@app.get("/api/list-images")
async def list_images(limit: int = 100):
    """업로드된 이미지 목록 조회"""
    try:
        response = s3_client.list_objects_v2(
            Bucket=BUCKET_NAME,
            Prefix="uploads/",
            MaxKeys=limit
        )
        
        images = []
        if 'Contents' in response:
            for obj in response['Contents']:
                # 각 이미지에 대한 presigned URL 생성
                download_url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={
                        'Bucket': BUCKET_NAME,
                        'Key': obj['Key']
                    },
                    ExpiresIn=3600
                )
                images.append({
                    "key": obj['Key'],
                    "size": obj['Size'],
                    "last_modified": obj['LastModified'].isoformat(),
                    "url": download_url
                })
        
        return {"images": images, "count": len(images)}
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"S3 오류: {str(e)}")


@app.delete("/api/delete-image/{object_key:path}")
async def delete_image(object_key: str):
    """이미지 삭제"""
    try:
        s3_client.delete_object(
            Bucket=BUCKET_NAME,
            Key=object_key
        )
        return {"message": "이미지가 삭제되었습니다.", "object_key": object_key}
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"S3 오류: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
