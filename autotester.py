import subprocess


arr = [
    "python3 ./jumpcut.py -dm \"debug2.txt\" -c 180 -a _c180",
    "python3 ./jumpcut.py -dm \"debug2.txt\" -c 240 -a _c200",
    "python3 ./jumpcut.py -dm \"debug2.txt\" -c 240 -a _c220",
    "python3 ./jumpcut.py -dm \"debug2.txt\" -c 240 -a _c240",
    "python3 ./jumpcut.py -dm \"debug2.txt\" -c 260 -a _c260",
    "python3 ./jumpcut.py -dm \"debug2.txt\" -c 280 -a _c280",
]

for command in arr:
    subprocess.call("timeout 10", shell=True)
    subprocess.call("cls", shell=True)
    print(f"TASK {arr.index(command)+1}/{len(arr)}")
    print(f"TASK {command}")
    subprocess.call(command, shell=True)
