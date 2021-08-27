#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time

os.system("apt install figlet")
os.system("clear")
os.system("figlet OTO IP - MAC MYS")
print("""
Bu araçla otomatik olarak IP - MAC  Adres değiştirebilirsiniz, değeri saniye olarak girin.
""")

sure = input("IP Değişim Süre(saniye) : ")

os.system("bash mac.sh")
print("Yeni ip Adres :")
print("-----------------------------")
os.system("python3 mystor.py -s")
print("-----------------------------")

while True:
	time.sleep(sure)
	os.system("bash mac.sh")
	print("Yeni ip Adres :")
	print("-----------------------------")
	os.system("python3 mystor.py -s")
	print("-----------------------------")
