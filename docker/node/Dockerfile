FROM debian:bookworm-slim@sha256:734a72b3d6142a71993b4bc580ca01d8ca687f77a2c422d96a961d3376b179bc

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends openssh-server python3 python3-apt \
    && passwd -d root \
    && rm -rf /var/lib/apt/lists/*

COPY sshd_config /etc/ssh/sshd_config
COPY entrypoint.sh /usr/local/bin/node-entrypoint
RUN chmod 0755 /usr/local/bin/node-entrypoint

EXPOSE 22
HEALTHCHECK --interval=5s --timeout=3s --start-period=5s --retries=20 \
    CMD ["python3", "-c", "import socket; s=socket.create_connection(('127.0.0.1',22),2); assert s.recv(80).startswith(b'SSH-2.0'); s.close()"]
ENTRYPOINT ["/usr/local/bin/node-entrypoint"]
