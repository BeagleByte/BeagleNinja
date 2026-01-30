#!/usr/bin/env python3
"""
Tor Bridge Auto-Configurator
Fetches fresh bridges, tests connectivity, and configures torrc automatically
"""

import requests
import re
import socket
import subprocess
import time
import sys
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

class TorBridgeManager:
    def __init__(self, torrc_path="/etc/tor/torrc1", control_port=9051):
        self.torrc_path = torrc_path
        self.control_port = control_port
        self.bridge_url = "https://bridges.torproject.org/bridges?transport=obfs4"

    def fetch_bridges(self) -> List[str]:
        """Fetch fresh obfs4 bridges from Tor Project"""
        try:
            print("Fetching fresh bridges from Tor Project...")
            response = requests.get(self.bridge_url, timeout=10)
            response.raise_for_status()

            # Extract bridge lines from HTML
            bridges = []
            # Pattern: obfs4 IP:PORT FINGERPRINT cert=... iat-mode=...
            pattern = r'obfs4\s+[\d\.]+:\d+\s+[A-F0-9]+\s+cert=[^\s]+(?:\s+iat-mode=\d+)?'

            matches = re.findall(pattern, response.text)
            bridges = [match.strip() for match in matches]

            if not bridges:
                print("⚠ Warning: No bridges found in response. Trying alternative parsing...")
                # Sometimes bridges are in pre tags or divs
                lines = response.text.split('\n')
                for line in lines:
                    if line.strip().startswith('obfs4'):
                        bridges.append(line.strip())

            print(f"✓ Found {len(bridges)} bridges")
            return bridges

        except Exception as e:
            print(f"✗ Error fetching bridges: {e}")
            return []

    def test_bridge_connectivity(self, bridge_line: str, timeout: int = 5) -> Tuple[str, bool]:
        """Test if a single bridge is reachable"""
        match = re.search(r'(\d+\.\d+\.\d+\.\d+):(\d+)', bridge_line)
        if not match:
            return bridge_line, False

        ip, port = match.groups()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, int(port)))
            sock.close()

            if result == 0:
                print(f"  ✓ {ip}:{port} - REACHABLE")
                return bridge_line, True
            else:
                print(f"  ✗ {ip}:{port} - UNREACHABLE")
                return bridge_line, False
        except Exception as e:
            print(f"  ✗ {ip}:{port} - ERROR: {e}")
            return bridge_line, False

    def test_all_bridges(self, bridges: List[str], max_workers: int = 5) -> List[str]:
        """Test multiple bridges concurrently"""
        print(f"\nTesting {len(bridges)} bridges (this may take a moment)...")

        reachable = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.test_bridge_connectivity, bridge): bridge
                       for bridge in bridges}

            for future in as_completed(futures):
                bridge_line, is_reachable = future.result()
                if is_reachable:
                    reachable.append(bridge_line)

        print(f"\n✓ Found {len(reachable)} reachable bridges out of {len(bridges)}")
        return reachable

    def read_torrc(self) -> List[str]:
        """Read current torrc file"""
        try:
            with open(self.torrc_path, 'r') as f:
                return f.readlines()
        except FileNotFoundError:
            print(f"⚠ torrc not found at {self.torrc_path}, creating new one")
            return []

    def write_torrc(self, lines: List[str]):
        """Write torrc file"""
        with open(self.torrc_path, 'w') as f:
            f.writelines(lines)

    def remove_bridge_config(self, lines: List[str]) -> List[str]:
        """Remove all bridge-related configuration"""
        filtered = []
        skip_next = False

        for line in lines:
            stripped = line.strip()
            # Skip bridge-related lines
            if any(stripped.startswith(keyword) for keyword in
                   ['UseBridges', 'Bridge ', 'ClientTransportPlugin']):
                continue
            # Skip comment about bridges
            if '# Bridge configuration' in line:
                continue
            # Skip EntryNodes (conflicts with bridges)
            if stripped.startswith('EntryNodes'):
                print("  Removing EntryNodes (conflicts with bridges)")
                continue

            filtered.append(line)

        return filtered

    def enable_bridges(self, bridges: List[str], limit: int = 3):
        """Configure torrc to use bridges"""
        print(f"\nConfiguring torrc with {min(len(bridges), limit)} bridges...")

        lines = self.read_torrc()
        lines = self.remove_bridge_config(lines)

        # Add bridge configuration
        lines.append('\n# Bridge configuration (auto-generated)\n')
        lines.append('UseBridges 1\n')
        lines.append('ClientTransportPlugin obfs4 exec /usr/bin/obfs4proxy\n')

        # Add bridges (limit to avoid too many)
        for bridge in bridges[:limit]:
            lines.append(f'Bridge {bridge}\n')

        self.write_torrc(lines)
        print(f"✓ Wrote {min(len(bridges), limit)} bridges to {self.torrc_path}")

    def disable_bridges(self):
        """Remove bridge configuration from torrc"""
        print("\nDisabling bridges, switching to direct connection...")

        lines = self.read_torrc()
        lines = self.remove_bridge_config(lines)

        self.write_torrc(lines)
        print(f"✓ Bridges disabled in {self.torrc_path}")

    def reload_tor(self, service_name="tor1"):
        """Reload Tor service"""
        try:
            print(f"\nReloading Tor ({service_name})...")
            subprocess.run(['supervisorctl', 'restart', service_name],
                           check=True, capture_output=True)
            print("✓ Tor restarted")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to restart Tor: {e}")
            return False

    def check_tor_status(self, wait_time: int = 30) -> bool:
        """Check if Tor has established a circuit"""
        print(f"\nWaiting {wait_time}s for Tor to establish circuit...")
        time.sleep(wait_time)

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect(('127.0.0.1', self.control_port))
            sock.send(b'GETINFO status/circuit-established\r\n')
            response = sock.recv(1024).decode()
            sock.close()

            if '250-status/circuit-established=1' in response:
                print("✓ Tor circuit established successfully!")
                return True
            else:
                print("✗ Tor circuit not established")
                return False
        except Exception as e:
            print(f"✗ Error checking Tor status: {e}")
            return False

    def auto_configure(self, test_bridges: bool = True, bridge_limit: int = 3):
        """Automatically fetch, test, and configure bridges"""
        print("=" * 60)
        print("Tor Bridge Auto-Configurator")
        print("=" * 60)

        # Fetch fresh bridges
        bridges = self.fetch_bridges()

        if not bridges:
            print("\n✗ No bridges available, switching to direct connection")
            self.disable_bridges()
            self.reload_tor()
            return False

        # Test bridge connectivity
        if test_bridges:
            reachable_bridges = self.test_all_bridges(bridges)
        else:
            print("\n⚠ Skipping bridge connectivity tests")
            reachable_bridges = bridges

        if not reachable_bridges:
            print("\n✗ No reachable bridges found, switching to direct connection")
            self.disable_bridges()
            self.reload_tor()
            return False

        # Configure torrc with working bridges
        self.enable_bridges(reachable_bridges, limit=bridge_limit)

        # Reload Tor
        if not self.reload_tor():
            return False

        # Check if Tor connects successfully
        if self.check_tor_status():
            print("\n" + "=" * 60)
            print("✓ SUCCESS: Tor is running with bridges!")
            print("=" * 60)
            return True
        else:
            print("\n" + "=" * 60)
            print("✗ FAILED: Bridges didn't work, falling back to direct")
            print("=" * 60)
            self.disable_bridges()
            self.reload_tor()
            return False


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 tor_bridge_manager.py auto          - Auto-fetch and configure")
        print("  python3 tor_bridge_manager.py fetch         - Just fetch and test bridges")
        print("  python3 tor_bridge_manager.py disable       - Disable bridges")
        print("  python3 tor_bridge_manager.py check         - Check Tor status")
        print("\nOptions:")
        print("  --torrc PATH          - Path to torrc file (default: /etc/tor/torrc1)")
        print("  --control-port PORT   - Tor control port (default: 9051)")
        print("  --no-test             - Skip bridge connectivity tests")
        print("  --limit N             - Max bridges to configure (default: 3)")
        sys.exit(1)

    command = sys.argv[1]

    # Parse options
    torrc_path = "/etc/tor/torrc1"
    control_port = 9051
    test_bridges = True
    bridge_limit = 3

    for i, arg in enumerate(sys.argv[2:], 2):
        if arg == "--torrc" and i + 1 < len(sys.argv):
            torrc_path = sys.argv[i + 1]
        elif arg == "--control-port" and i + 1 < len(sys.argv):
            control_port = int(sys.argv[i + 1])
        elif arg == "--no-test":
            test_bridges = False
        elif arg == "--limit" and i + 1 < len(sys.argv):
            bridge_limit = int(sys.argv[i + 1])

    manager = TorBridgeManager(torrc_path=torrc_path, control_port=control_port)

    if command == "auto":
        manager.auto_configure(test_bridges=test_bridges, bridge_limit=bridge_limit)

    elif command == "fetch":
        bridges = manager.fetch_bridges()
        if bridges:
            reachable = manager.test_all_bridges(bridges) if test_bridges else bridges
            print(f"\nReachable bridges ({len(reachable)}):")
            for bridge in reachable:
                print(f"  {bridge}")

    elif command == "disable":
        manager.disable_bridges()
        manager.reload_tor()

    elif command == "check":
        if manager.check_tor_status(wait_time=0):
            print("✓ Tor is connected")
            sys.exit(0)
        else:
            print("✗ Tor is NOT connected")
            sys.exit(1)

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()