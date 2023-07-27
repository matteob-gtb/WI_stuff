import os
import subprocess


command_str = " -r \"%s.pcapng\" -R \"wlan.fc.type_subtype == 0x04 && wlan_radio.signal_dbm > -30\" -2 -T fields -e frame.number -e frame.time -e wlan.sa -e wlan.da -e wlan_radio.signal_dbm -e wlan.ssid -E header=y -E separator=, -E quote=d -E occurrence=f > %s.csv"


for file in [p for p in os.listdir() if ".pcapng" in str(p)]:
   raw_name = str(file).removesuffix(".pcapng")
   os.system("tshark"  +  command_str % (raw_name,raw_name))
        