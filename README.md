# Beagle Ninja

![img.png](images/img.png)

## 🧅 Tor Anonymity System with Load Balancer SOCKS Proxy

A portable Docker-based multi-Tor setup with HAProxy load balancing for enhanced anonymity and timing attack prevention.

### 🎯 Features

- **4 Independent Tor Instances** - Separate circuits for redundancy
- **Random Load Balancing** - HAProxy with `balance random` for unpredictable routing
- **Privoxy Integration** - HTTP proxy with content filtering
- **Health Monitoring** - Built-in HAProxy statistics dashboard
- **Cross-Platform** - Works on Linux, macOS, and Windows

### 📋 Prerequisites

- **Docker** (20.10+)
- **Docker Compose** (2.0+)
- **4GB RAM** recommended


### 🔌 Usage

### Option 1: Simple Random Tor Access (Recommended for most use cases)

Use HAProxy's load-balanced endpoint:

```bash
# SOCKS5 proxy
curl -x socks5h://127.0.0.1:9999 https://check.torproject.org

# HTTP proxy via Privoxy
curl -x http://127.0.0.1:8118 https://check.torproject.org

# Configure applications
# Firefox: Settings → Network → SOCKS5: 127.0.0.1:9999
# Chrome:   --proxy-server="socks5://127.0.0.1:9999"
```

### Option 2: Direct Tor Instance Access

Access specific Tor instances (useful for proxychains):

```bash
# Tor instance 1
curl -x socks5h://127.0.0.1:9050 https://check.torproject.org

# Tor instance 2
curl -x socks5h://127.0.0.1:9051 https://check.torproject.org

# Tor instance 3
curl -x socks5h://127.0.0.1:9052 https://check.torproject.org

# Tor instance 4
curl -x socks5h://127.0.0.1:9053 https://check.torproject.org
```

### Option 3: Proxychains (Advanced)

See **[docs/PROXYCHAINS_SETUP.md](docs/PROXYCHAINS_SETUP.md)** for detailed configuration.

Quick example:
```bash
proxychains4 curl https://check.torproject.org
proxychains4 nmap -sT target.com
```



### Container Logs
```bash
# All logs
docker-compose logs -f

# Specific service
docker-compose logs -f tor-loadbalancer

# Individual Tor instance logs
tail -f logs/tor1. out. log
tail -f logs/haproxy.out.log
```

## 🔒 Security Considerations

### ✅ work in progress
- Stream isolation per destination/port
- Regular circuit rotation (every 10 minutes)
- No relay/exit node operation
- Container security hardening (capabilities dropped)
- Cookie authentication for control ports

### ⚠️ Known Limitations
- **Not a silver bullet** - Tor provides anonymity, not invincibility
- **Application leaks** - Browser fingerprinting, WebRTC, DNS leaks can expose you
- **Malicious exit nodes** - Always use HTTPS for sensitive data
- **Timing attacks** - This setup reduces but doesn't eliminate correlation risks
- **Tor over Tor** - Using proxychains to chain Tor instances is controversial

### 🛡️ Hardening Recommendations

1. **Use with Tails/Whonix** - Combine with OS-level anonymity
2**Browser hardening**:
    - Use Tor Browser or hardened Firefox
    - Disable WebRTC:  `media.peerconnection.enabled = false`
    - Use HTTPS Everywhere / uBlock Origin
    - Disable JavaScript for high-security scenarios
4. **DNS protection**:
   ```bash
   # Always use SOCKS5H (H = resolve hostnames via proxy)
   curl -x socks5h://127.0.0.1:9999 https://example.com
   ```
5. **Clear data on shutdown** - Run stop script and clear Tor data dirs

## 🔧 Configuration

### Exclude Specific Countries

Edit `configs/torrc1` through `configs/torrc4`:

```conf
# Exclude exit nodes from specific countries
ExcludeExitNodes {CN},{RU},{IR},{KP}
StrictNodes 1
```

Country codes:  https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2

### Adjust Circuit Rotation

```conf
# Rotate circuits more frequently (trade anonymity for freshness)
MaxCircuitDirtiness 300    # 5 minutes instead of 10
NewCircuitPeriod 15        # Consider new circuit every 15 sec
```

### Change Load Balancing Algorithm

Edit `configs/haproxy.cfg`:

```conf
backend tor_backends
    # Random (best for anti-timing attacks)
    balance random
    
    # OR Round-robin (predictable but evenly distributed)
    # balance roundrobin
    
    # OR Least connections (best for performance)
    # balance leastconn
```


### Optional: Pre-build Docker Image


## 🧪 Testing

### Verify Tor Connection
```bash
curl -x socks5h://127.0.0.1:9999 https://check.torproject.org
```

Should output:  "Congratulations.  This browser is configured to use Tor."

### Check Your IP
```bash
# Without Tor
curl https://api.ipify.org

# Through Tor
curl -x socks5h://127.0.0.1:9999 https://api.ipify.org
```

IPs should be different!

### DNS Leak Test
```bash
# Bad (DNS leak)
curl -x socks5://127.0.0.1:9999 https://www.dnsleaktest.com

# Good (DNS via Tor)
curl -x socks5h://127.0.0.1:9999 https://www.dnsleaktest.com
```

Always use `socks5h` (with 'h') to resolve DNS through Tor!

### Test All Tor Instances
```bash
for port in 9050 9051 9052 9053 9999; do
    echo "Testing port $port:"
    curl -x socks5h://127.0.0.1:$port https://api.ipify.org
done
```

Should show different IPs (unless circuits happen to share exit nodes).

## 🐛 Troubleshooting

### Container won't start
```bash
# Check Docker is running
docker info

# View error logs
docker-compose logs

# Rebuild from scratch
docker-compose down -v
docker-compose up -d --build
```

### Tor circuits not establishing
```bash
# Wait longer (can take 60+ seconds)
docker-compose logs -f | grep "Bootstrapped"

# Check if Tor ports are already in use
netstat -tulpn | grep -E "9050|9051|9052|9053"

# Restart with fresh circuits
./scripts/stop.sh
rm -rf data/tor*/*
./scripts/start.sh
```

### Slow performance
- Tor is inherently slower than direct connections
- Try different load balancing:  `balance leastconn` in haproxy.cfg
- Increase `NumEntryGuards` in torrc files
- Check HAProxy stats for unhealthy backends

### "Permission denied" errors
```bash
# Fix data directory permissions
sudo chown -R 1000:1000 data/
chmod 700 data/tor*
```


## 🔄 Maintenance

### Update Tor
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Clear old circuits
```bash
rm -rf data/tor1/* data/tor2/* data/tor3/* data/tor4/*
```

### Backup configuration
```bash
tar -czf tor-config-backup-$(date +%Y%m%d).tar.gz config/
```

## ⚖️ Legal Disclaimer

This tool is provided for **legitimate privacy and security purposes**. Users are responsible for complying with all applicable laws.  The authors do not condone illegal activity.

Tor is legal in most countries but may be restricted in some jurisdictions. Check local laws before use.

## 🤝 Contributing

Improvements welcome! Consider:
- I2P integration
- Better health checking
- Vanguards

## 📜 License

MIT License - See LICENSE file

## 🔗 Resources

- [Tor Project](https://www.torproject.org/)
- [HAProxy Documentation](http://www.haproxy.org/)
- [Privoxy Manual](https://www.privoxy.org/user-manual/)
- [Proxychains GitHub](https://github.com/haad/proxychains)
- [Docker Security Best Practices](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)
- The first address for using Tor: https://www.torproject.org/
- Tor Bridges: https://bridges.torproject.org/bridges?transport=obfs4
- Here are the Spec for Tor, here you can learn a lot about Tor: https://spec.torproject.org/

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review logs:  `docker-compose logs`
3. Open an issue on GitHub (if applicable)
4. Consult Tor Project documentation

---

**Stay safe, stay anonymous!  🧅🔒**