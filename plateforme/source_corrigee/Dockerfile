FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN python -m pip install --no-cache-dir -r requirements-lock.txt && \
    python -m pip install --no-cache-dir --no-deps .
ENTRYPOINT ["oric-full"]
CMD ["smoke"]
