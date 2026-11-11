FROM python:3.12-alpine

WORKDIR /app
COPY print-learn-server.py /app/print-learn-server.py
COPY run.sh /run.sh
RUN chmod a+x /run.sh

ENV PRINT_DB_PATH=/data/print_learn.db \
    PRINT_BOT_PORT=8765

CMD ["/run.sh"]
