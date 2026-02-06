FROM debian:bullseye-slim AS builder
RUN apt-get update && apt-get install -y git build-essential && apt-get clean
WORKDIR /work
RUN git clone https://github.com/igaw/jitterdebugger.git /work/jitterdebugger
RUN cd jitterdebugger && make

FROM debian:bullseye-slim
RUN apt-get update && apt-get install -y python3-pip procps && apt-get clean
RUN pip3 install poetry==1.8.4
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache
WORKDIR /work
COPY --from=builder /work/jitterdebugger/jitterdebugger /work/jitterdebugger/jittersamples /work/jitterdebugger/jitterplot /usr/bin/
COPY api/ ./api
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-root && rm -rf $POETRY_CACHE_DIR 
EXPOSE 5000 
CMD poetry run python3 /work/api/app.py
