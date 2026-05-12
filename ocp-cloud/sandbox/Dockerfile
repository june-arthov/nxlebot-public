FROM python:3.11-slim AS builder
# Build stage — nothing persisted

FROM python:3.11-slim

# ── Security: remove dangerous binaries ──
RUN rm -rf /usr/bin/ssh /usr/bin/nc /usr/bin/wget /usr/bin/curl \
    /usr/bin/gcc /usr/bin/g++ /usr/bin/as /usr/bin/ld \
    /usr/bin/perl /usr/bin/php* /usr/bin/ruby /usr/bin/lua* \
    /usr/bin/gdb /usr/bin/strace /usr/bin/ltrace \
    /usr/bin/xxd /usr/bin/hexdump \
    /sbin/iptables /sbin/ip6tables /usr/sbin/tcpdump \
    /bin/mount /bin/umount /usr/bin/fusermount* \
    2>/dev/null || true

# ── Read-only root filesystem marker ──
RUN touch /.readonly

# ── Runtime dependencies only ──
RUN pip3 install --no-cache-dir requests 2>/dev/null || true

# ── Copy interpreter, lock permissions ──
COPY ocp_interpreter.py /app/ocp_interpreter.py
RUN chmod 555 /app/ocp_interpreter.py && \
    chown root:root /app/ocp_interpreter.py && \
    chmod 555 /app && \
    chown root:root /app

# ── Create user ──
RUN useradd -m -s /bin/bash -u 1000 sandbox && \
    chmod 755 /home/sandbox

USER sandbox
WORKDIR /tmp

ENTRYPOINT ["python3", "/app/ocp_interpreter.py"]
