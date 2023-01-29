import time
import json
import subprocess

while True:
    cmd = open("scheduler.json", "r")
    subprocess.run(json.loads(cmd.read())["command"], shell=True)
    time.sleep(30)
