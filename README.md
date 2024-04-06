# fastapi-template
Template for python microservice API

sqlacodegen {db_con_string} > x.py


# create python 12 env
```bash
python3 -m venv be
source be/bin/activate
```

.env
```bash
ENV_STATE="dev" # or prod
API_NAME="HK-2024-BE"
API_DESCRIPTION="Backend for hack kosice 2024 project"
API_VERSION="1.0.0"
API_DEBUG_MODE=True
```


```bash
uvicorn manage:app --port 8000
```

```bash
docker build -t legacy-refactorer .
```

```bash
docker run -d -p 8000:8000 legacy-refactorer .
```