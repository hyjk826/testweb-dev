# TestWeb Dev Repository

이 리포지토리는 testweb 애플리케이션의 소스 코드를 관리합니다.

## 구조

```
testweb-dev/
├── .github/
│   └── workflows/
│       └── build-and-push.yml    # GitHub Actions 워크플로우
├── web/                          # 정적 웹 파일들
│   └── index.html
├── Dockerfile                    # Docker 이미지 빌드 파일
└── README.md
```

## GitHub Actions 설정

### 1. Secrets 설정

다음 secrets를 GitHub 리포지토리 설정에서 추가해야 합니다:

- `OPS_REPO_TOKEN`: testweb-ops 리포지토리에 대한 액세스 토큰

### 2. 토큰 생성 방법

1. GitHub에서 Personal Access Token 생성:
   - Settings → Developer settings → Personal access tokens → Tokens (classic)
   - `repo` 권한 선택
   - `workflow` 권한 선택

2. testweb-ops 리포지토리에 토큰 추가:
   - Settings → Secrets and variables → Actions
   - `OPS_REPO_TOKEN` 이름으로 토큰 추가

## 워크플로우 동작

1. **코드 푸시 시**: main 또는 develop 브랜치에 푸시하면 자동으로 실행
2. **이미지 빌드**: Docker 이미지를 빌드하고 ghcr.io에 푸시
3. **ops 리포지토리 트리거**: 이미지 푸시 완료 후 testweb-ops 리포지토리에 웹훅 전송

## 이미지 태그 전략

- `latest`: main 브랜치의 최신 이미지
- `develop`: develop 브랜치의 최신 이미지
- `{branch}-{sha}`: 특정 커밋의 이미지
