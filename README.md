# discord-bot
혐오발언 탐지 모델 활용 사례

## 사용 방법
`.env` 파일 작성
```sh
cp .env.example .env
vim .env
```

빌드 후 실행
```sh
docker build . --tag=discord-bot
docker run --env-file=.env discord-bot
```
