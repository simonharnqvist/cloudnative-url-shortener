FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
COPY .env .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./ .

RUN pip install .
RUN pip list && python -c "import url_shortener" || echo 'Not found!'

ENV RUN_MODE=app

CMD ["/bin/bash", "-c", "\
    if [ \"$RUN_MODE\" = \"test\" ]; then \
        echo 'Running tests...'; \
        pytest tests/ --disable-warnings -v; \
    else \
        echo 'Starting app...'; \
        uvicorn url_shortener.api:app --host 0.0.0.0 --port 8000; \
    fi"]