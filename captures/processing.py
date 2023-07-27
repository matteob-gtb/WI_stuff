import numpy
import pandas as pd
import os 
from datetime import datetime
from datetime import timedelta 
import matplotlib.pyplot as plt

cestformat = "%B %d, %Y %H:%M:%S.%f"


log_file = open("probe_logs_output.txt","w")

captures = [p for p in os.listdir() if ".csv" in str(p)]



def log(in_str : str):
    log_file.write(in_str + os.linesep)


def get_tabular_name(file_name : str) -> str:
    if "wifi_on_screen_on_pw_off_aps_nearby" in file_name : return "XA"
    if "wifi_on_screen_on_pw_off" in file_name: return "A"
    if "wifi_on_screen_off_pw_off" in file_name : return "S"
    if "wifi_on_screen_on_pw_on" in file_name : return "PA"
    if "wifi_on_screen_off_pw_on" in file_name : return "PS"


BURST_DELAY_TOLERANCE_MS = 55 #ms

#there are better ways
def get_date(in_str : any) -> datetime:
    return datetime.strptime(str(in_str)[:-8],cestformat)



number_of_null_ssids = 0
number_of_probes_per_file = []
macs_per_file = []

random_bit_set = 0

for file_name in captures:
    log("Current file :"  + file_name)
    df = pd.read_csv(file_name)
    number_of_probes_per_file.append(len(df.index))
    #unique MAC address
    unique_macs = pd.unique(df['wlan.sa'])
    macs_per_file.append(len(unique_macs)) 

    signal_strenghts = [row['wlan_radio.signal_dbm'] for (i,row) in df.iterrows()]
    
    number_of_null_ssids += len(df[df['wlan.ssid'] == "<MISSING>"])


    plt.figure(5) # signal-strength of each probe
    x_axis_5 = range(len(signal_strenghts))
    plt.plot(x_axis_5,signal_strenghts,label = file_name)
    plt.title("Signal Strength of probes over time")
    plt.xlabel("Probe request n°")
    plt.ylabel("Signal strength [dBm]")
    plt.legend(loc='best')




    #frequenza delle richieste 
    
    last_date = get_date(df.iloc[len(df)-1]["frame.time"])
    first_Date = get_date(df.iloc[0]["frame.time"])

    seconds = (last_date-first_Date)/timedelta(minutes=1)
    log("Time elapsed between requests %d" % seconds)
    freq = len(df)/seconds
    log("Probe request frequency is : " + str(freq) + " req/min")

    burst_timestamp = []
    burst_rssi = []
    #numero di probe request per burst
    delay_between_probes_in_burst = []

    non_averaged_signal_strenght_arr = []

    for mac in unique_macs:
        if(int(mac[0:2],16) & 0b10) : random_bit_set += 1
        log("Current MAC : "+ mac)
        #iterate over all the macs and try to identify bursts
        same_mac_rows = df[df['wlan.sa'] == mac]
        min_date = get_date(same_mac_rows['frame.time'].min())
        ctr = 0
        sum_rssi = 0
        curr_delay_arr = []
        #burst detection to pair-wise
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
        log("Current burst [MAC : %s] has %d probe requests" % (mac,ctr))
    #plot 
    #for each burst plot the average delay between probe requests
    plt.figure(1) # delays figure
    burst_x_axis = range(len(delay_between_probes_in_burst))
    y_axis = [sum(p)/len(p) for p in delay_between_probes_in_burst]
    plt.plot(burst_x_axis,y_axis,label = file_name)
    plt.legend(loc='best')
    
    
    plt.figure(0)
    x_axis = range(len(burst_rssi))
    plt.plot(x_axis,burst_rssi,label = file_name)
    plt.legend(loc='best')

    sum_interval_btw_bursts = 0

    log("Sum bursts : " + str(burst_rssi))
    y_bursts = []
    for i in range(1,len(burst_timestamp)-1):
        curr_value = (burst_timestamp[i]-burst_timestamp[i-1])/timedelta(milliseconds=1)
        y_bursts.append((burst_timestamp[i]-burst_timestamp[i-1])/timedelta(seconds=1))
        sum_interval_btw_bursts += curr_value
        #log("Burst n° %d #%d [ms]" % (i,curr_value))
    plt.figure(4) # delays between bursts
    x_bursts = range(1,len(burst_timestamp)-1)
    plt.plot(x_bursts,y_bursts,label = file_name)
    plt.legend(loc='best')
    log("The average delay between consecutive bursts is %d ms" % (sum_interval_btw_bursts/(len(burst_timestamp)-1)))
    

    #end burst potenza segnale 

    #-> media segnale
    sum_rssi = 0
    for index,row in df.iterrows():
        sum_rssi += row['wlan_radio.signal_dbm']

    sum_rssi/=len(df)
    log("Average signal strenght : %d" % sum_rssi)

    real_mac = "64:70:33:22:59:EC"

    mac_contained = real_mac in unique_macs
    log("Real MAC is contained in the probes : " + str(mac_contained))
 
     #check real mac address -> frequenza MAC address

log("%d MAC addresses had their Local Bit Set, %s %% of total" % (random_bit_set,round(random_bit_set/sum(macs_per_file),2)*100))

print("%d MAC addresses had their Local Bit Set, %s %% of total" % (random_bit_set,round(random_bit_set/sum(macs_per_file),2)*100))

log("%d probes had a null SSID entry, %s %% of all the probes" % (number_of_null_ssids,round(number_of_null_ssids/sum(number_of_probes_per_file),2)*100))

print("%d probes had a null SSID entry, %s %% of all the probes" % (number_of_null_ssids,round(number_of_null_ssids/sum(number_of_probes_per_file),2)*100))

log_file.close()

plt.figure(4) # delays between bursts
plt.title("Delay between consecutive bursts [s]")
plt.xlabel("i-th burst")
plt.ylabel("Delay in seconds")



plt.figure(3) #macs per file
plt.bar([get_tabular_name(file_name) for file_name in captures],macs_per_file)
plt.title("Number of of unique MAC addresses per file")
plt.xlabel("File name")
plt.ylabel("N° of unique MAC addresses")



plt.figure(2) # probes per file
plt.bar([get_tabular_name(file_name) for file_name in captures],number_of_probes_per_file)
plt.title("Number of probes per file")
plt.xlabel("Tabular name")
plt.ylabel("N° of probes")

plt.figure(1)
plt.title("Average delay between consecutive probes in a burst [µs]")
plt.xlabel("Burst n°")
plt.ylabel("Average delay")

plt.figure(0)
plt.title("Average signal strength of the probes per burst")
plt.xlabel("Burst n°")
plt.ylabel("Average signal strength")
plt.show()

 