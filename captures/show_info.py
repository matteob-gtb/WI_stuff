import os
import numpy
import pandas as pd
import sys
import matplotlib

captures = []
csvs = []
for file in os.listdir(os.curdir):
        if file.endswith(".pcapng"):
            captures.append(file)
            csvs.append(file.replace(".pcapng",".csv"))

if len(sys.argv) == 2 and sys.argv[1] == "create_csv":
    to_csv = "tshark -r \"%s\" -R \"wlan.fc.type_subtype == 0x04 && wlan_radio.signal_dbm >= -50\" -2 -T fields -e frame.number -e frame.time -e wlan.sa -e wlan.da -e wlan_radio.signal_dbm -E header=y -E separator=, -E quote=d -E occurrence=f > %s"
    for f in captures:
        os.system(to_csv % (f,f.replace(".pcapng",".csv")))

import pandas as pd

file = csvs[3]
print("Opening %s" % file)
df = pd.read_csv(file)

unique_sa = pd.unique(df['wlan.sa'])
print('There were ' +str(len(unique_sa)) + ' source MAC addresses')


probes_per_mac = df.groupby(['wlan.sa'])

for mac_group,items_in_group in probes_per_mac:
    #print(mac_group)

print(df)

import matplotlib.pyplot as plt

fig = plt.figure(figsize=(8,8))
plt.hist('wlan.sa',probes_per_mac)
plt.xlabel('IAT (s)')
plt.ylabel('Frequency')
plt.grid(visible=True)
plt.show()
