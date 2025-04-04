FROM python:alpine

RUN adduser -D -u 1000 -g 1000 appuser

USER appuser

COPY --chown=appuser:appuser . /tmp

RUN pip install --no-cache-dir /tmp \
    && rm -rf /tmp/*

CMD ["python3", "-m", "tl_producer.app"]