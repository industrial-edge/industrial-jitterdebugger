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
RUN apk add --no-cache python3 py3-pip procps stress-ng

COPY --from=builder /work/jitterdebugger/jitterdebugger /work/jitterdebugger/jittersamples /work/jitterdebugger/jitterplot /usr/bin/
COPY dist/industrial_jitterdebugger-${VERSION}*.whl ./

RUN PYTHONDONTWRITEBYTECODE=1 pip3 install --no-cache-dir --no-compile --root-user-action=ignore --break-system-packages /industrial_jitterdebugger-${VERSION}*.whl && \
    rm /industrial_jitterdebugger-${VERSION}*.whl
