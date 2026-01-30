FROM debian:trixie-slim

LABEL maintainer="BeagleByte"
LABEL description="Multi-Tor with HAProxy load balancer for enhanced anonymity"

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Install packages
RUN apt-get update && apt-get install -y \
    tor \
    haproxy \
    privoxy \
    supervisor \
    curl \
    net-tools \
    procps \
    obfs4proxy snowflake-client\
    nano \
    mc netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Create tor user and directories
RUN useradd -r -m -d /var/lib/tor -s /bin/false debian-tor || true

# Create privoxy user if not exists
RUN groupadd -r privoxy && \
    useradd -r -m -d /var/lib/privoxy -s /bin/false privoxy || true && \
    mkdir -p /etc/privoxy && \
    chown -R privoxy:privoxy /etc/privoxy && \
    chmod -R 750 /etc/privoxy && \
    chown privoxy:privoxy /etc/privoxy/config && \
    chmod 440 /etc/privoxy/config

# Create data directories with proper permissions
RUN mkdir -p /var/lib/tor1 /var/lib/tor2 /var/lib/tor3 /var/lib/tor4 && \
    mkdir -p /var/log/tor /var/log/haproxy /var/log/privoxy /var/log/supervisor && \
    mkdir -p /var/log/tor-proxy && \
    chown -R debian-tor:debian-tor /var/lib/tor1 /var/lib/tor2 /var/lib/tor3 /var/lib/tor4 && \
    chown -R debian-tor:debian-tor /var/log/tor && \
    chmod 700 /var/lib/tor1 /var/lib/tor2 /var/lib/tor3 /var/lib/tor4



COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
# Expose ports
EXPOSE 9050 9051 9052 9053 9999 8118

# Health check
HEALTHCHECK --interval=120s --timeout=10s --start-period=30s --retries=3 \
CMD curl -x socks5h://127.0.0.1:9050 -s https://check.torproject.org/ | grep -q Congratulations || exit 1

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
# Start supervisor
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf", "-n"]