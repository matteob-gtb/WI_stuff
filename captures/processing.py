import numpy
import pandas as pd
import os
import pyshark
import time
from datetime import datetime
from datetime import timedelta
import random
import matplotlib.pyplot as plt

captures = [p for p in os.listdir() if ".csv" in str(p)]

cestformat = "%B %d, %Y %H:%M:%S.%f"



BURST_DELAY_TOLERANCE_MS = 55 #ms

#there are better ways
def get_date(in_str : any) -> datetime:
    return datetime.strptime(str(in_str)[:-8],cestformat)


for file_name in captures:
    print("Current file :"  + file_name)
    df = pd.read_csv(file_name)
    #unique MAC address
    unique_macs = pd.unique(df['wlan.sa'])
    print(unique_macs)
    print(len(unique_macs))

    #frequenza delle richieste 
    
    last_date = get_date(df.iloc[len(df)-1]["frame.time"])
    first_Date = get_date(df.iloc[0]["frame.time"])

    seconds = (last_date-first_Date).total_seconds()
    print("Time elapsed between requests %d" % seconds)
    freq = len(df)/seconds
    print("Probe request frequency is : " + str(freq))

    burst_timestamp = []
    burst_rssi = []
    #numero di probe request per burst
    delay_between_probes_in_burst = []
    for mac in unique_macs:
        print("Current MAC : "+ mac)
        #iterate over all the macs and try to identify bursts
        same_mac_rows = df[df['wlan.sa'] == mac]
        min_date = get_date(same_mac_rows['frame.time'].min())
        ctr = 0
        sum_rssi = 0
        curr_delay_arr = []
        #changed burst detection to pair-wise
        for index,same_mac in same_mac_rows.iterrows():
            date = get_date(same_mac["frame.time"])
            if (date-min_date)/timedelta(milliseconds=1) < BURST_DELAY_TOLERANCE_MS:
                ctr+=1
                sum_rssi += same_mac['wlan_radio.signal_dbm']
                if ctr != 1:
                    curr_delay_arr.append((date-min_date)/timedelta(microseconds=1))
                min_date = date # pair-wise detection
        if len(curr_delay_arr) > 0:
            delay_between_probes_in_burst.append(curr_delay_arr)
        burst_timestamp.append(min_date)
        burst_rssi.append(sum_rssi/ctr)
        print("Current burst [MAC : %s] has %d probe requests" % (mac,ctr))
    #plot 
    print("Delays")
    print(delay_between_probes_in_burst)
    x_axis = range(len(burst_rssi))
    plt.plot(x_axis,burst_rssi)
    plt.xlabel("Burst n°")
    plt.ylabel("Average signal strength")
    plt.title("Average signal strength of the probes per burst")
    plt.show()

    sum_interval_btw_bursts = 0

    print("Sum bursts : " + str(burst_rssi))

    for i in range(1,len(burst_timestamp)-1):
        #print(burst_timestamp[i-1])
        curr_value = (burst_timestamp[i]-burst_timestamp[i-1])/timedelta(milliseconds=1)
        sum_interval_btw_bursts += curr_value
        #print("Burst n° %d #%d [ms]" % (i,curr_value))

    print("The average delay between consecutive bursts is %d ms" % (sum_interval_btw_bursts/(len(burst_timestamp)-1)))
    

    #end burst potenza segnale 

    #-> media segnale
    sum_rssi = 0
    for index,row in df.iterrows():
        sum_rssi += row['wlan_radio.signal_dbm']

    sum_rssi/=len(df)
    print("Average signal strenght : %d" % sum_rssi)

    real_mac = "64:70:33:22:59:EC"

    mac_contained = real_mac in unique_macs
    print("Real MAC is contained in the probes : " + str(mac_contained))
 
     #check real mac address -> frequenza MAC address



   # print(df)
