# Complete Torrc Configuration Reference

## Table of Contents
1. [Basic Client Options](#basic-client-options)
2. [SOCKS Proxy Configuration](#socks-proxy-configuration)
3. [Logging Options](#logging-options)
4. [System & Process Options](#system--process-options)
5. [Control Port Configuration](#control-port-configuration)
6. [Hidden Services](#hidden-services)
7. [Relay Configuration](#relay-configuration)
8. [Bridge Configuration](#bridge-configuration)
9. [Exit Policy Configuration](#exit-policy-configuration)
10. [Circuit & Path Selection](#circuit--path-selection)
11. [Performance & Bandwidth](#performance--bandwidth)
12. [Security & Privacy](#security--privacy)
13. [Network Configuration](#network-configuration)
14. [Directory Server Options](#directory-server-options)
15. [Advanced Options](#advanced-options)

---

## Basic Client Options

```
# Data directory for Tor state files
DataDirectory /var/lib/tor

# Use a specific Tor user
User debian-tor

# GeoIP database files
GeoIPFile /usr/share/tor/geoip
GeoIPv6File /usr/share/tor/geoip6
```

---

## SOCKS Proxy Configuration

```
# SOCKS proxy port (default: 9050)
SocksPort 9050
SocksPort 127.0.0.1:9050
SocksPort 192.168.0.1:9100
SocksPort 0  # Disable SOCKS port

# SOCKS listening address
SocksListenAddress 127.0.0.1:9050
SocksListenAddress [::1]:9050

# SOCKS policy
SocksPolicy accept 192.168.0.0/16
SocksPolicy accept6 FC00::/7
SocksPolicy reject *

# SOCKS timeout
SocksTimeout 2 minutes

# Virtual address network
VirtualAddrNetworkIPv4 10.192.0.0/10
VirtualAddrNetworkIPv6 [FC00::]/7

# DNS port for transparent DNS proxy
DNSPort 5353
DNSPort 127.0.0.1:5353

# Transparent proxy port
TransPort 9040
TransPort 127.0.0.1:9040

# NAT'd connections port
NATDPort 9090
```

---

## Logging Options

```
# Log levels: debug, info, notice, warn, err
Log notice file /var/log/tor/notices.log
Log info file /var/log/tor/tor.log
Log debug file /var/log/tor/debug.log
Log notice syslog
Log notice stderr
Log notice stdout

# Limit log file size
MaxLogFileSize 10 MB

# Truncate log files on startup
TruncateLogFile 1

# Safe logging (scrub sensitive info)
SafeLogging 1

# Log timezone
LogTimeGranularity 1 second

# Protocol warnings
ProtocolWarnings 1
```

---

## System & Process Options

```
# Run as daemon
RunAsDaemon 1

# PID file
PidFile /var/run/tor/tor.pid

# Change to user
User _tor

# Disable debugger attachment
DisableDebuggerAttachment 1

# Hardware acceleration
HardwareAccel 1

# Use multiple CPU cores
NumCPUs 4

# File permissions
CacheDirectoryGroupReadable 1
```

---

## Control Port Configuration

```
# Control port
ControlPort 9051
ControlPort 127.0.0.1:9051
ControlListenAddress 127.0.0.1:9051

# Control socket
ControlSocket /var/run/tor/control
ControlSocketsGroupWritable 1

# Authentication
HashedControlPassword 16:872860B76453A77D60CA2BB8C1A7042072093276A3D701AD684053EC4C
CookieAuthentication 1
CookieAuthFile /var/lib/tor/control_auth_cookie
CookieAuthFileGroupReadable 1

# Disable control port auth (INSECURE - only for testing)
# ControlPort 9051
# __OwningControllerProcess <PID>
```

---

## Hidden Services

```
# Basic hidden service
HiddenServiceDir /var/lib/tor/hidden_service/
HiddenServicePort 80 127.0.0.1:80
HiddenServicePort 22 127.0.0.1:22

# Hidden service with custom settings
HiddenServiceDir /var/lib/tor/my_service/
HiddenServicePort 80 127.0.0.1:8080
HiddenServiceVersion 3
HiddenServiceMaxStreams 10
HiddenServiceMaxStreamsCloseCircuit 1

# Client authorization (v3)
HiddenServiceDir /var/lib/tor/auth_service/
HiddenServicePort 80 127.0.0.1:80
HiddenServiceEnableIntroDoSDefense 1
HiddenServiceEnableIntroDoSRatePerSec 25
HiddenServiceEnableIntroDoSBurstPerSec 200

# Publish hidden service to different authorities
HiddenServicePublishIntroContentToAuthorities 1

# Single Onion Service (non-anonymous)
HiddenServiceSingleHopMode 1
HiddenServiceNonAnonymousMode 1

# Client-side hidden service auth
HidServAuth <onion-address> <auth-cookie>

# Directory for client keys
ClientOnionAuthDir /var/lib/tor/onion_auth
```

---

## Relay Configuration

```
# Basic relay setup
ORPort 9001
ORPort [2001:db8::1]:9001
ORPort 443 NoListen
ORPort 127.0.0.1:9090 NoAdvertise

# Advertised address
Address relay.example.com
OutboundBindAddress 10.0.0.5
OutboundBindAddressOR 10.0.0.5
OutboundBindAddressExit 10.0.0.6

# Relay identity
Nickname MyTorRelay
ContactInfo 0xFFFFFFFF Your Name <you@example.com>

# Relay flags
AssumeReachable 1
PublishServerDescriptor 1

# Family of relays
MyFamily $fingerprint1,$fingerprint2

# IPv6 support
ORPort [::]:9001 IPv6Only

# Bandwidth limits
RelayBandwidthRate 1 MB
RelayBandwidthBurst 2 MB
MaxAdvertisedBandwidth 500 KB
BandwidthRate 10 MB
BandwidthBurst 20 MB

# Accounting limits
AccountingMax 100 GB
AccountingStart day 00:00
AccountingStart week 1 00:00
AccountingStart month 1 00:00

# Reject certain connections
ReachableAddresses *:80,*:443
ReachableAddresses reject *:*
ReachableDirAddresses *:80
ReachableORAddresses *:443

# Server keys
ServerTransportPlugin obfs4 exec /usr/bin/obfs4proxy
ServerTransportListenAddr obfs4 0.0.0.0:9001
ExtORPort auto
```

---

## Bridge Configuration

```
# Act as a bridge
BridgeRelay 1

# Don't publish bridge descriptor
PublishServerDescriptor 0

# Bridge distribution method
BridgeDistribution none
BridgeDistribution https
BridgeDistribution email
BridgeDistribution moat

# Pluggable transport as bridge
ServerTransportPlugin obfs4 exec /usr/bin/obfs4proxy
ServerTransportListenAddr obfs4 0.0.0.0:9001
ExtORPort auto

# Client bridge usage
UseBridges 1
Bridge 127.0.0.1:9001
Bridge obfs4 127.0.0.1:9001 <fingerprint> cert=<cert> iat-mode=0
ClientTransportPlugin obfs4 exec /usr/bin/obfs4proxy
```

---

## Exit Policy Configuration

```
# Allow specific ports
ExitPolicy accept *:80
ExitPolicy accept *:443
ExitPolicy accept *:6660-6667  # IRC
ExitPolicy accept *:119  # NNTP

# Reject specific
ExitPolicy reject *:25  # SMTP
ExitPolicy reject *:119  # NNTP
ExitPolicy reject 192.168.0.0/16:*
ExitPolicy reject6 [FC00::]/7:*

# Default reject
ExitPolicy reject *:*

# Reduced exit policy
ReducedExitPolicy 1

# Allow connections to private networks
ExitPolicyRejectPrivate 0
ExitPolicyRejectLocalInterfaces 1

# IPv6 exit policy
IPv6Exit 1
```

---

## Circuit & Path Selection

```
# Entry nodes (guards)
EntryNodes {us},{de},{fr}
EntryNodes $fingerprint1,$fingerprint2
NumEntryGuards 3
NumPrimaryGuards 3

# Exit nodes
ExitNodes {nl},{se},{ch}
ExitNodes $fingerprint1,$fingerprint2
StrictNodes 1  # Never use nodes outside specified list

# Exclude nodes
ExcludeNodes {cn},{ru}
ExcludeNodes $fingerprint1
ExcludeExitNodes {us}

# Middle nodes
MiddleNodes {de},{fr}

# Circuit building
CircuitBuildTimeout 60 seconds
LearnCircuitBuildTimeout 1
CircuitIdleTimeout 1 hour
CircuitStreamTimeout 0
MaxCircuitDirtiness 10 minutes
MaxClientCircuitsPending 32
NewCircuitPeriod 30 seconds

# Path selection
EnforceDistinctSubnets 1
NodeFamily $fingerprint1,$fingerprint2

# Use specific bridges or guards
UseBridges 1
UseEntryGuards 1
NumDirectoryGuards 3

# Long-lived ports (use same circuit)
LongLivedPorts 21,22,706,1863,5050,5190,5222,5223,6523,6667,6697,8300

# Circuit priorities
CircuitPriorityHalflife 30 seconds
```

---

## Performance & Bandwidth

```
# Global bandwidth
BandwidthRate 10 MB
BandwidthBurst 20 MB
MaxAdvertisedBandwidth 5 MB

# Per-connection limits
PerConnBWRate 100 KB
PerConnBWBurst 200 KB

# Relay bandwidth
RelayBandwidthRate 1 MB
RelayBandwidthBurst 2 MB

# Connection limits
ConnLimit 1000
MaxClientCircuitsPending 128

# Kernel optimizations
ConstrainedSockets 1
ConstrainedSockSize 8192

# Connection padding
ConnectionPadding auto
ReducedConnectionPadding 0

# Bandwidth scheduling
TokenBucketRefillInterval 100 msec
```

---

## Security & Privacy

```
# Avoid disk writes
AvoidDiskWrites 1

# Disable prediction
__DisablePredictedCircuits 1

# Use microdescriptors
UseMicrodescriptors 1

# Download extra info
DownloadExtraInfo 1

# Sandbox mode (experimental)
Sandbox 1

# Dormant mode
DormantOnFirstStartup 0
DormantCanceledByStartup 1
DormantTimeoutEnabled 1

# Don't cache DNS
ServerDNSDetectHijacking 1
ServerDNSRandomizeCase 1

# Bridges and pluggable transports
UseBridges 1
ClientTransportPlugin obfs4 exec /usr/bin/obfs4proxy

# Onion service security
HiddenServiceMaxStreamsCloseCircuit 1
```

---

## Network Configuration

```
# Firewall/proxy settings
FascistFirewall 1
FirewallPorts 80,443
ReachableAddresses *:80,*:443

# HTTP/HTTPS proxy
HTTPSProxy 127.0.0.1:8080
HTTPSProxyAuthenticator username:password
HTTPProxy 127.0.0.1:8080
HTTPProxyAuthenticator username:password

# SOCKS proxy (for Tor to use)
Socks4Proxy 127.0.0.1:1080
Socks5Proxy 127.0.0.1:1080
Socks5ProxyUsername username
Socks5ProxyPassword password

# Prefer IPv6
ClientPreferIPv6ORPort 1
ClientPreferIPv6DirPort 1
ClientUseIPv4 1
ClientUseIPv6 1

# Outbound bind
OutboundBindAddress 10.0.0.5

# Advertised address
Address noname.example.com
DirAuthority address:port fingerprint
```

---

## Directory Server Options

```
# Directory port
DirPort 9030
DirPort 80 NoListen
DirPort 127.0.0.1:9091 NoAdvertise
DirListenAddress 0.0.0.0:9030

# Directory cache
DirCache 1

# Directory front page
DirPortFrontPage /etc/tor/tor-exit-notice.html

# Download schedules
FetchDirInfoEarly 1
FetchDirInfoExtraEarly 1
FetchHidServDescriptors 1
FetchServerDescriptors 1
FetchUselessDescriptors 0

# Directory authorities
DirAuthority authority-name address:port fingerprint
AlternateDirAuthority authority-name address:port fingerprint
AlternateBridgeAuthority authority-name address:port fingerprint

# V3 authority options
V3AuthVotingInterval 1 hour
V3AuthVoteDelay 5 minutes
V3AuthDistDelay 5 minutes
```

---

## Advanced Options

```
# Disable certain features
DisableAllSwap 1
DisableNetwork 0
DisableDebuggerAttachment 1

# Test network
TestingTorNetwork 1
ServerDNSAllowBrokenConfig 1

# Warnings
WarnUnsafeSocks 1

# Map addresses
MapAddress 1.2.3.4 5.6.7.8
AutomapHostsOnResolve 1
AutomapHostsSuffixes .onion,.exit

# Treat all .exit domains
AllowDotExit 0

# Allow invalid nodes
AllowSingleHopCircuits 0
AllowSingleHopExits 0

# Connection timeout
CircuitStreamTimeout 0
SocksTimeout 2 minutes

# Client optimizations
OptimisticData auto
UseOptimisticData auto

# Extend request handling
ExtendAllowPrivateAddresses 0

# Path bias
PathBiasCircThreshold 150
PathBiasNoticeRate 0.7
PathBiasWarnRate 0.5
PathBiasExtremeRate 0.3

# Guard settings
GuardLifetime 120 days

# Keepalive
KeepalivePeriod 5 minutes

# Dormant settings
DormantClientTimeout 24 hours
```

---

## Example Complete Configurations

### 1. Basic Client
```
SocksPort 9050
DataDirectory /var/lib/tor
Log notice file /var/log/tor/notices.log
```

### 2. Privacy-Focused Client
```
SocksPort 9050
DataDirectory /var/lib/tor
ExcludeNodes {us},{gb},{au},{ca},{nz}
StrictNodes 1
EntryNodes {se},{is},{ch}
ExitNodes {se},{is},{ch}
Log notice file /var/log/tor/notices.log
AvoidDiskWrites 1
```

### 3. Exit Relay
```
ORPort 9001
DirPort 9030
Nickname MyExitRelay
ContactInfo you@example.com
ExitPolicy accept *:80
ExitPolicy accept *:443
ExitPolicy reject *:*
RelayBandwidthRate 10 MB
RelayBandwidthBurst 20 MB
DataDirectory /var/lib/tor
```

### 4. Bridge with Pluggable Transport
```
BridgeRelay 1
PublishServerDescriptor 0
ORPort 9001
ServerTransportPlugin obfs4 exec /usr/bin/obfs4proxy
ServerTransportListenAddr obfs4 0.0.0.0:9001
ExtORPort auto
ContactInfo you@example.com
DataDirectory /var/lib/tor
```

### 5. Hidden Service
```
SocksPort 9050
HiddenServiceDir /var/lib/tor/my_website/
HiddenServicePort 80 127.0.0.1:8080
HiddenServiceVersion 3
DataDirectory /var/lib/tor
```

### 6. Using the Configuration from Your File
```
# From your uploaded config
ExitNodes {NG},{HK},{BR},{MX},{FR}
StrictNodes 1
EntryNodes {BR},{MX},{JP},{FR}
ControlPort 9051
CookieAuthentication 1
CookieAuthFileGroupReadable 1
DataDirectory /var/lib/tor
```

---

## Notes

- Many options have changed or been added in recent Tor versions
- Always consult the official documentation: https://www.torproject.org/docs/tor-manual.html
- Use `man tor` for the most up-to-date options for your version
- Test configurations carefully before deploying
- Some options are mutually exclusive or require other options to be set

For the latest comprehensive list, check the Tor manual for your specific version.