import subprocess
import sys

if len(sys.argv) == 1:
    print("Select a channel")
    exit(1)



subprocess.run(["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport","--channel=" + sys.argv[1]])