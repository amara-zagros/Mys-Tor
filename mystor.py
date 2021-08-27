#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import getopt
from requests import get
import subprocess
import time
import signal
from stem import Signal
from stem.control import Controller
from packaging import version

VERSION = "3"

IP_API = "https://api.ipify.org/?format=json"



class bcolors:

    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RED = '\033[31m'
    YELLOW = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    BGRED = '\033[41m'
    WHITE = '\033[37m'


def t():
    current_time = time.localtime()
    ctime = time.strftime('%H:%M:%S', current_time)
    return '[' + ctime + ']'


def sigint_handler(signum, frame):
    print("User interrupt ! shutting down")
    stop_mystor()


def logo():
    print(bcolors.RED + bcolors.BOLD)
    print("""
  $$\   $$\                     
  $$ |  $$ |                    
  $$ |  $$ | $$$$$$\  $$\   $$\ 
  $$$$$$$$ |$$  __$$\ $$ |  $$ |
  $$  __$$ |$$$$$$$$ |$$ |  $$ |
  $$ |  $$ |$$   ____|$$ |  $$ |
  $$ |  $$ |\$$$$$$$\ \$$$$$$$ |
  \__|  \__| \_______| \____$$ |
                      $$\   $$ |
                      \$$$$$$  |
                       \______/ 
 	{V} - Gelismis Mys Tor

    """.format(V=VERSION))
    print(bcolors.ENDC)


def usage():
    logo()
    print("""
    Mys Tor kullanım:
    -s    --start       Başlat Mys Tor
    -r    --switch      Yeni tor çıkış düğümü iste
    -x    --stop        Durdur Mys Tor
    -h    --help        Yardım
    -u    --update      Güncelleme

    """)
    sys.exit()


def ip():
    while True:
        try:
            jsonRes = get(IP_API).json()
            ipTxt = jsonRes["ip"]
        except:
            continue
        break
    return ipTxt


def check_root():
    if os.geteuid() != 0:
        print("Root Izninizin Olması Gerek Lütfen sudo python3 mystor.py Olarak Deneyiniz.")
        sys.exit(0)


signal.signal(signal.SIGINT, sigint_handler)

TorrcCfgString = \
    """
VirtualAddrNetwork 10.0.0.0/10
AutomapHostsOnResolve 1
TransPort 9040
DNSPort 5353
ControlPort 9051
RunAsDaemon 1
"""

resolvString = 'nameserver 1.1.1.1'

Torrc = '/etc/tor/torghostrc'
resolv = '/etc/resolv.conf'


def start_mystor():
    print(t() + ' Guncellemek icin python3 mystor.py -u')
    os.system('sudo cp /etc/resolv.conf /etc/resolv.conf.bak')
    if os.path.exists(Torrc) and TorrcCfgString in open(Torrc).read():
        print(t() + ' Torrc dosyası zaten yapılandırılmış')
    else:

        with open(Torrc, 'w') as myfile:
            print(t() + ' Torcc dosyası yazma')
            myfile.write(TorrcCfgString)
            print(bcolors.GREEN + '[done]' + bcolors.ENDC)
    if resolvString in open(resolv).read():
        print(t() + ' DNS resolv.conf dosyası zaten yapılandırılmış.')
    else:
        with open(resolv, 'w') as myfile:
            print(t() + ' DNS resolv.conf dosyası yapılandırılıyor.. '),
            myfile.write(resolvString)
            print(bcolors.GREEN + '[done]' + bcolors.ENDC)

    print(t() + ' Tor Servisi Durduruluyor'),
    os.system(' service tor stop')
    os.system(' fuser -k 9051/tcp > /dev/null 2>&1')
    print(bcolors.GREEN + '[done]' + bcolors.ENDC)
    print(t() + ' Yeni tor arka plan programı başlatma '),
    os.system('sudo -u debian-tor tor -f /etc/tor/torghostrc > /dev/null'
              )
    print(bcolors.GREEN + '[done]' + bcolors.ENDC)
    print(t() + ' iptables kurallarını ayarlama'),

    iptables_rules = \
        """
	NON_TOR="192.168.1.0/24 192.168.0.0/24"
	TOR_UID=%s
	TRANS_PORT="9040"

	iptables -F
	iptables -t nat -F

	iptables -t nat -A OUTPUT -m owner --uid-owner $TOR_UID -j RETURN
	iptables -t nat -A OUTPUT -p udp --dport 53 -j REDIRECT --to-ports 5353
	for NET in $NON_TOR 127.0.0.0/9 127.128.0.0/10; do
	 iptables -t nat -A OUTPUT -d $NET -j RETURN
	done
	iptables -t nat -A OUTPUT -p tcp --syn -j REDIRECT --to-ports $TRANS_PORT

	iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
	for NET in $NON_TOR 127.0.0.0/8; do
	 iptables -A OUTPUT -d $NET -j ACCEPT
	done
	iptables -A OUTPUT -m owner --uid-owner $TOR_UID -j ACCEPT
	iptables -A OUTPUT -j REJECT
	""" \
        % subprocess.getoutput('id -ur debian-tor')

    os.system(iptables_rules)
    print(bcolors.GREEN + '[done]' + bcolors.ENDC)
    print(t() + ' Geçerli IP alınıyor...')
    print(t() + ' IP Adresiniz : ' + bcolors.GREEN + ip() + bcolors.ENDC)


def stop_mystortor():
    print(bcolors.RED + t() + 'Durduruluyor Mys tor' + bcolors.ENDC)
    print(t() + ' iptables temizleniyor, varsayılana sıfırlanıyor'),
    os.system('mv /etc/resolv.conf.bak /etc/resolv.conf')
    IpFlush = \
        """
	iptables -P INPUT ACCEPT
	iptables -P FORWARD ACCEPT
	iptables -P OUTPUT ACCEPT
	iptables -t nat -F
	iptables -t mangle -F
	iptables -F
	iptables -X
	"""
    os.system(IpFlush)
    os.system(' fuser -k 9051/tcp > /dev/null 2>&1')
    print(bcolors.GREEN + '[done]' + bcolors.ENDC)
    print(t() + ' Ağ yöneticisini yeniden başlatılıyor'),
    os.system('service network-manager restart')
    print(bcolors.GREEN + '[done]' + bcolors.ENDC)
    print(t() + ' Geçerli IP alınıyor...')
    time.sleep(3)
    print(t() + '  IP Adresiniz : ' + bcolors.GREEN + ip() + bcolors.ENDC)


def switch_tor():
    print(t() + ' Lütfen bekle...')
    time.sleep(7)
    print(t() + ' Yeni devre isteniyor...'),
    with Controller.from_port(port=9051) as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM)
    print(bcolors.GREEN + '[done]' + bcolors.ENDC)
    print(t() + ' Geçerli IP alınıyor...')
    print(t() + ' IP Adresiniz : ' + bcolors.GREEN + ip() + bcolors.ENDC)


def check_update():
    print(t() + ' Güncellemeler kontrol ediliyor...')
    jsonRes = get(LATEST_RELEASE_API).json()
    newversion = jsonRes["tag_name"][1:]
    print(newversion)
    if version.parse(newversion) > version.parse(VERSION):
        print(t() + bcolors.GREEN + ' Yeni güncelleme mevcut!' + bcolors.ENDC)
        print(t() + ' Mevcut Mys Tor sürümünüz : ' + bcolors.GREEN + VERSION + bcolors.ENDC)
        print(t() + ' En son Mys Tor sürümü mevcut : ' + bcolors.GREEN + newversion + bcolors.ENDC)
        yes = {'yes', 'y', 'ye', ''}
        no = {'no', 'n'}

        choice = input(
            bcolors.BOLD + "En son sürümü indirmek ve Git deposundan derlemek ister misiniz? [Y/n]" + bcolors.ENDC).lower()
        if choice in yes:
            os.system(
                'cd /tmp && git clone  https://github.com/asper-tool/oto-ip')
            os.system(' sudo ./indir.sh')
        elif choice in no:
            print(t() + " Kullanıcı tarafından iptal edilen güncelleme")
        else:
            print("Lütfen yanıtlayın 'yes' or 'no'")
    else:
        print(t() + " Mys TOR güncel!")


def main():
    check_root()
    if len(sys.argv) <= 1:
        check_update()
        usage()
    try:
        (opts, args) = getopt.getopt(sys.argv[1:], 'srxhu', [
            'start', 'stop', 'switch', 'help', 'update'])
    except (getopt.GetoptError):
        usage()
        sys.exit(2)
    for (o, a) in opts:
        if o in ('-h', '--help'):
            usage()
        elif o in ('-s', '--start'):
            start_mystor()
        elif o in ('-x', '--stop'):
            stop_mystortor()
        elif o in ('-r', '--switch'):
            switch_tor()
        elif o in ('-u', '--update'):
            check_update()
        else:
            usage()


if __name__ == '__main__':
    main()
