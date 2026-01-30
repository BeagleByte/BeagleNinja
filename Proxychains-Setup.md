# 🔗 Proxychains Configuration Guide

Complete guide to using proxychains with your multi-Tor setup for advanced proxy chaining and routing.

## 📚 Table of Contents

1. [Installation](#installation)
2. [Basic Configuration](#basic-configuration)
3. [Advanced Chaining Strategies](#advanced-chaining-strategies)
4. [Usage Examples](#usage-examples)
5. [Security Considerations](#security-considerations)
6. [Troubleshooting](#troubleshooting)

---

## 📥 Installation

### Linux (Debian/Ubuntu)
```bash
sudo apt update
sudo apt install proxychains4
```

### Linux (Fedora/RHEL)
```bash
sudo dnf install proxychains-ng
```

### macOS
```bash
brew install proxychains-ng
```

### Windows (WSL2)
```bash
# Use WSL2 Ubuntu and follow Linux instructions
wsl --install
```

---

## ⚙️ Basic Configuration

### Configuration File Locations

Proxychains checks for config files in this order:
1. `./proxychains.conf` (current directory)
2. `~/.proxychains/proxychains.conf` (user home)
3. `/etc/proxychains.conf` (system-wide)
4. `/etc/proxychains4.conf` (system-wide, newer versions)

### Recommended:  User-level Configuration

Create a user-specific config:

```bash
mkdir -p ~/.proxychains
nano ~/.proxychains/proxychains.conf
```

---

## 🔧 Configuration Examples

### Example 1: Simple Random Tor Selection

**Use case**: Basic anonymity, random Tor node per connection

```conf name=proxychains.conf
# Random selection - picks ONE random proxy from the list
random_chain

# Proxy DNS requests
proxy_dns

# Timeouts (in milliseconds)
tcp_read_time_out 15000
tcp_connect_time_out 8000

[ProxyList]
# All 4 Tor instances from your container
socks5 127.0.0.1 9050
socks5 127.0.0.1 9051
socks5 127.0.0.1 9052
socks5 127.0.0.1 9053
```

**Result**: Each connection uses a randomly selected Tor instance.

---

### Example 2: Dynamic Chain (Recommended)

**Use case**: Use all working proxies, skip dead ones

```conf
# Use all proxies in list, skip dead ones
dynamic_chain

proxy_dns
tcp_read_time_out 15000
tcp_connect_time_out 8000

[ProxyList]
socks5 127.0.0.1 9050
socks5 127.0.0.1 9051
socks5 127.0.0.1 9052
socks5 127.0.0.1 9053
```

**Result**: Traffic goes through all 4 Tor instances in order, but continues if one fails.

---

### Example 3: Random Chain (Multi-hop)

**Use case**: Maximum unpredictability, Tor-over-Tor

```conf
# Random chain - uses X random proxies from the list
random_chain

# Number of proxies to chain
chain_len = 2

proxy_dns
tcp_read_time_out 15000
tcp_connect_time_out 8000

[ProxyList]
socks5 127.0.0.1 9050
socks5 127.0.0.1 9051
socks5 127.0.0.1 9052
socks5 127.0.0.1 9053
```

**Result**: Each connection uses 2 random Tor instances chained together.

**⚠️ Warning**:  Tor Project doesn't officially recommend Tor-over-Tor, but it adds unpredictability.

---

### Example 4: Strict Chain (All or Nothing)

**Use case**: Require all proxies to work, fail if any is down

```conf
# Must use ALL proxies in exact order
strict_chain

proxy_dns
tcp_read_time_out 15000
tcp_connect_time_out 8000

[ProxyList]
socks5 127.0.0.1 9050
socks5 127.0.0.1 9051
socks5 127.0.0.1 9052
socks5 127.0.0.1 9053
```

**Result**: Traffic goes through all 4 Tor instances sequentially.  Connection fails if ANY instance is down.

---

### Example 5: Mixed Proxy Types

**Use case**: Combine Tor with other proxies

```conf
dynamic_chain
proxy_dns
tcp_read_time_out 15000
tcp_connect_time_out 8000

[ProxyList]
# First hop: Your custom VPN or proxy
socks5 vpn-server.example.com 1080

# Second hop: Tor via HAProxy (random selection)
socks5 127.0.0.1 9999

# Third hop: Another external proxy (optional)
# http proxy.example.com 8080 username password
```

**Result**: Traffic goes VPN → Tor (random) → Internet

---

### Example 6: Specific Tor Routing

**Use case**: Always use specific Tor instances in order

```conf
strict_chain
proxy_dns
tcp_read_time_out 15000
tcp_connect_time_out 8000

[ProxyList]
# Always route through Tor1 then Tor3
socks5 127.0.0.1 9050
socks5 127.0.0.1 9052
```

**Result**: Predictable Tor1 → Tor2 chaining (useful for testing).

---

## 🚀 Usage Examples

### Basic Commands

```bash
# Test connection
proxychains4 curl https://check.torproject.org

# Check your IP
proxychains4 curl https://api.ipify.org

# Run Firefox through Tor
proxychains4 firefox

# SSH through Tor
proxychains4 ssh user@example.com

# Git operations through Tor
proxychains4 git clone https://github.com/user/repo.git

# Wget downloads
proxychains4 wget https://example.com/file.zip

# Nmap scanning (TCP only!)
proxychains4 nmap -sT -Pn target.com
```

### Advanced Usage

#### Quiet Mode (Less Verbose)
```bash
proxychains4 -q curl https://api.ipify.org
```

#### Use Specific Config File
```bash
proxychains4 -f ~/my-custom-proxychains.conf curl https://api.ipify.org
```

#### Test Multiple Configurations
```bash
# Random selection
proxychains4 -f ~/. proxychains/random. conf curl https://api.ipify.org

# Strict chaining
proxychains4 -f ~/.proxychains/strict. conf curl https://api.ipify.org

# Dynamic chaining
proxychains4 -f ~/.proxychains/dynamic. conf curl https://api.ipify.org
```

---

## 🎯 Recommended Configurations by Use Case

### 🔹 General Browsing (Balance Speed & Anonymity)
```conf
dynamic_chain
chain_len = 1
proxy_dns
[ProxyList]
socks5 127.0.0.1 9999  # Use HAProxy for random selection
```

### 🔹 High Anonymity (Tor-over-Tor)
```conf
random_chain
chain_len = 3
proxy_dns
[ProxyList]
socks5 127.0.0.1 9050
socks5 127.0.0.1 9051
socks5 127.0.0.1 9052
socks5 127.0.0.1 9053
```

### 🔹 Testing & Development
```conf
strict_chain
proxy_dns
[ProxyList]
socks5 127.0.0.1 9050  # Always use Tor instance 1
```

### 🔹 Penetration Testing / Security Research
```conf
dynamic_chain
proxy_dns
tcp_read_time_out 20000
tcp_connect_time_out 10000
[ProxyList]
socks5 127.0.0.1 9050
socks5 127.0.0.1 9051
```

---

## 🔒 Security Considerations

### ✅ Best Practices

1. **Always use `proxy_dns`**
   ```conf
   proxy_dns  # Prevents DNS leaks
   ```

2. **Use SOCKS5, not SOCKS4**
   ```conf
   socks5 127.0.0.1 9050  # ✅ Good
   socks4 127.0.0.1 9050  # ❌ Outdated, less secure
   ```

3. **Test for leaks**
   ```bash
   # DNS leak test
   proxychains4 curl https://www.dnsleaktest.com/
   
   # IP leak test
   proxychains4 curl https://api.ipify.org
   ```

4. **Disable WebRTC in browsers**
    - Firefox: `about:config` → `media.peerconnection.enabled = false`
    - Chrome: Use uBlock Origin to block WebRTC

5. **Use HTTPS everywhere**
   ```bash
   # Bad (exit node can see traffic)
   proxychains4 curl http://example.com
   
   # Good (encrypted end-to-end)
   proxychains4 curl https://example.com
   ```

### ⚠️ Limitations

- **UDP not supported** - Proxychains only works with TCP
- **Not transparent** - Some applications may detect proxy usage
- **DNS leaks possible** - Some apps bypass proxy DNS settings
- **No ICMP** - Ping and traceroute won't work
- **Application-level leaks** - Browser fingerprinting still possible

### 🛡️ Hardening

```conf
# Add these options to your proxychains. conf

# Quieter output (doesn't help security, just cleaner logs)
quiet_mode

# Faster timeout for dead proxies
tcp_connect_time_out 5000

# Enable local network access (be careful!)
# localnet 127.0.0.0/255.0.0.0
```

---

## 🐛 Troubleshooting

### Problem: "proxychains4: command not found"

**Solution**:
```bash
# Install proxychains
sudo apt install proxychains4

# Or check if it's installed as 'proxychains'
proxychains curl https://api.ipify.org
```

---

### Problem: "connection refused" errors

**Solution**:
```bash
# 1. Check if container is running
docker ps | grep tor-anonymity

# 2. Check if ports are open
netstat -tulpn | grep -E "9050|9051|9052|9053"

# 3. Test direct connection without proxychains
curl -x socks5h://127.0.0.1:9050 https://api.ipify.org

# 4. Check Tor logs
docker-compose logs tor-loadbalancer | grep -i error
```

---

### Problem: Slow connections

**Solution**:
```conf
# Reduce chain length
random_chain
chain_len = 1  # Use only 1 proxy instead of multiple

# OR use HAProxy directly
[ProxyList]
socks5 127.0.0.1 9999  # HAProxy handles load balancing
```

---

### Problem: DNS leaks

**Solution**:
```bash
# 1. Ensure proxy_dns is enabled
grep proxy_dns ~/. proxychains/proxychains. conf

# 2. Test for leaks
proxychains4 curl https://www.dnsleaktest.com/

# 3. Check /etc/resolv.conf isn't overriding
cat /etc/resolv.conf
```

---

### Problem: Some applications don't work

**Solution**:
```bash
# Proxychains doesn't work with: 
# - Statically linked binaries
# - UDP-only applications
# - ICMP (ping)

# Workarounds:
# 1. Use Torsocks instead
sudo apt install torsocks
torsocks curl https://api.ipify.org

# 2. Use application's built-in proxy support
# Firefox: Settings → Network → SOCKS5: 127.0.0.1:9999
```

---

### Problem: "ERROR: ld.so. preload cannot be preloaded"

**Solution**:
```bash
# Proxychains uses LD_PRELOAD, which doesn't work with setuid binaries

# Option 1: Use torsocks
torsocks your-command

# Option 2: Run as regular user (not with sudo)
proxychains4 curl https://example.com

# Option 3: If you need sudo, configure app's proxy settings directly
```

---

## 📊 Testing Your Setup

### Complete Test Suite

```bash
#!/bin/bash
# Save as:  test-proxychains.sh

echo "🧪 Proxychains Configuration Test Suite"
echo "========================================"
echo ""

# Test 1: Real IP (without proxy)
echo "1️⃣ Your real IP:"
curl -s https://api.ipify.org
echo ""

# Test 2: Tor IP (with proxychains)
echo "2️⃣ Your Tor IP:"
proxychains4 -q curl -s https://api.ipify.org
echo ""

# Test 3: Tor Project verification
echo "3️⃣ Tor Project verification:"
proxychains4 -q curl -s https://check.torproject.org | grep -o "Congratulations.*Tor."
echo ""

# Test 4: Each Tor instance
echo "4️⃣ Testing all Tor instances:"
for port in 9050 9051 9052 9053; do
    ip=$(curl -s -x socks5h://127.0.0.1:$port https://api.ipify.org)
    echo "   Port $port: $ip"
done
echo ""

# Test 5: HAProxy (should show random IPs on repeated calls)
echo "5️⃣ Testing HAProxy random distribution (3 requests):"
for i in 1 2 3; do
    ip=$(curl -s -x socks5h://127.0.0.1:9999 https://api.ipify.org)
    echo "   Request $i: $ip"
done
echo ""

echo "✅ Test complete!"
echo ""
echo "⚠️  Your real IP and Tor IPs should be DIFFERENT!"
echo "⚠️  If they're the same, your proxy configuration has issues."
```

Run with:
```bash
chmod +x test-proxychains.sh
./test-proxychains. sh
```

---

## 🌐 Browser-Specific Configurations

### Firefox
```
Settings → General → Network Settings → Settings
• Manual proxy configuration
• SOCKS Host: 127.0.0.1
• Port: 9999
• SOCKS v5: ✓
• Proxy DNS when using SOCKS v5: ✓
```

### Chrome/Chromium
```bash
# Launch with proxy
google-chrome --proxy-server="socks5://127.0.0.1:9999"

# Or use extension:  FoxyProxy
```

### Command-line cURL
```bash
# SOCKS5 with DNS resolution via proxy
curl -x socks5h://127.0.0.1:9999 https://api.ipify.org

# HTTP proxy via Privoxy
curl -x http://127.0.0.1:8118 https://api.ipify.org
```

---

## 📚 Additional Resources

- **Proxychains GitHub**: https://github.com/haad/proxychains
- **Tor Project**:  https://www.torproject.org/
- **DNS Leak Test**: https://www.dnsleaktest.com/
- **IP Check**: https://check.torproject.org/

---

## 🎓 Summary

**Best configuration for most users:**
```conf
dynamic_chain
proxy_dns
tcp_read_time_out 15000
tcp_connect_time_out 8000

[ProxyList]
socks5 127.0.0.1 9999  # Use HAProxy for automatic load balancing
```

**High anonymity (Tor-over-Tor):**
```conf
random_chain
chain_len = 2
proxy_dns
tcp_read_time_out 15000
tcp_connect_time_out 8000

[ProxyList]
socks5 127.0.0.1 9050
socks5 127.0.0.1 9051
socks5 127.0.0.1 9052
socks5 127.0.0.1 9053
```

---

**Happy chaining! 🔗🔒**