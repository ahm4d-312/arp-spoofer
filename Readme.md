# ARP Spoofer

A simple ARP spoofing tool implemented in Python using **Scapy**.
## Requirements
- Python 3.8+
- Linux
- Root privileges
- Scapy
## Usage
```bash
sudo python3 arp.py -v <victim_ip> -i <interface>
```
### Arguments

| Argument            | Description                                |
| ------------------- | ------------------------------------------ |
| `-v`, `--victim`    | Victim IP address (required)               |
| `-i`, `--interface` | Network interface (required)               |
| `-g`, `--gateway`   | Gateway IP address, default is 192.168.1.1 |

---
## How it Works

1. Sends ARP requests to discover the MAC addresses of both the victim and the gateway.
2. Continuously sends forged ARP replies:
   - To the victim, claiming the attacker's MAC belongs to the gateway.
   - To the gateway, claiming the attacker's MAC belongs to the victim.
3. This causes both devices to send traffic through the attacker's machine.
4. When the program exits, it sends legitimate ARP replies multiple times to restore the original ARP tables.
## Example

```bash
#Because raw Ethernet frames are used, the script must be executed as root.
sudo python3 arp.py -v 192.168.1.31 -i wlan0 -g 192.168.1.1
```


