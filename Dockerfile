FROM python:3.12.2

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install pip
RUN pip3 install -r requirements.txt

EXPOSE 8000
EXPOSE 8501

COPY . .
CMD sh -c "python3 --version && pip list && uvicorn manage:app --host 0.0.0.0 --port 8000"
