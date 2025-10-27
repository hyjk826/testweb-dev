# NGINX로 정적 파일 서빙 (경량)
FROM nginx:1.25-alpine

# 정적 파일 복사 (권한 지정 불필요)
COPY ./web/ /usr/share/nginx/html/

# 기본 설정은 이미지에 포함된 /etc/nginx/conf.d/default.conf 사용
# (K8s에서 ConfigMap으로 default.conf를 마운트하면 자동 대체됨)

EXPOSE 80

# Dockerfile의 HEALTHCHECK는 K8s 프로브와 중복이므로 제거
# (필요하면 curl 설치 후 추가 가능)

CMD ["nginx", "-g", "daemon off;"]
