FROM python:3.11-slim
WORKDIR /app

COPY ./mcp/mcp-nos/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY ./mcp/mcp-nos/server.py /app/server.py

ENV MCPO_EXPOSED_PORT=8001

EXPOSE ${MCPO_EXPOSED_PORT}

CMD ["sh", "-c", "mcpo --host 0.0.0.0 --port \"$MCPO_EXPOSED_PORT\" -- python /app/server.py"]
