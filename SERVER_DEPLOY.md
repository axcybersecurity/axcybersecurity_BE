# 서버 배포

강의자료 첨부파일은 파일당 기본 100MB까지 업로드할 수 있습니다. Nginx에서 multipart 부가 데이터를 포함해 110MB까지 요청을 받도록 설정합니다.

## 최초 1회 설정

서버에서 저장소 루트로 이동한 뒤 실행합니다.

```bash
sudo cp deploy/nginx/upload-size.conf /etc/nginx/conf.d/axcybersecurity-upload-size.conf
sudo nginx -t
sudo systemctl reload nginx
```

`nginx -t`가 실패하면 reload 명령은 실행하지 말고 표시된 설정 오류를 먼저 수정합니다.

## 백엔드 재시작

서버에서 사용 중인 systemd 서비스를 재시작합니다. 아래의 `<service-name>`은 실제 서비스 이름으로 바꿔야 합니다.

```bash
sudo systemctl restart <service-name>
sudo systemctl status <service-name> --no-pager
```

파일당 제한을 바꾸려면 백엔드 서비스에 `CLASSNOTICE_MAX_FILE_SIZE_MB`환경 변수를 설정하고, Nginx의 `client_max_body_size`는 그보다 약간 크게 설정합니다.

## 계정 생성

백엔드 저장소 루트에서 계정 생성 명령을 실행합니다. 비밀번호는 명령줄 기록에 남지 않도록 실행 후 숨김 입력으로 받습니다.

```bash
.venv/bin/python -m scripts.create_user gini 정지인 학부연구생
```
