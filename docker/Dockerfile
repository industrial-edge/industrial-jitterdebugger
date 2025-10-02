ARG VERSION=0.0.0

FROM alpine:3.22 AS builder
RUN apk add --no-cache git build-base
WORKDIR /work
RUN git clone https://github.com/igaw/jitterdebugger.git /work/jitterdebugger && \
    cd /work/jitterdebugger && \
    git config user.email "local@build.com" && \
    git config user.name "Local Build" && \
    git switch -c localbuild 9e0cd08e34575089869bee7e28d9900d34c4fe83 && \
    make

FROM alpine:3.22
ARG VERSION
RUN apk add --no-cache python3 uv procps stress-ng
ENV UV_PROJECT_ENVIRONMENT=/usr/local

COPY --from=builder /work/jitterdebugger/jitterdebugger /work/jitterdebugger/jittersamples /work/jitterdebugger/jitterplot /usr/bin/
COPY industrial_jitterdebugger-${VERSION}*.whl ./

RUN PYTHONDONTWRITEBYTECODE=1 uv pip install --no-cache --system --break-system-packages /industrial_jitterdebugger-${VERSION}*.whl && \
    rm /industrial_jitterdebugger-${VERSION}*.whl
