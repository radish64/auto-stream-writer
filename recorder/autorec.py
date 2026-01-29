import os
import math
import subprocess
import psycopg2
import time
import datetime as dt
from rclone_python import rclone
from rclone_python.remote_types import RemoteTypes

def getShow():
    con = psycopg2.connect(database="postgres", user='postgres', password='password', host='postgres', port=5432)
    cur = con.cursor()

    weekday = dt.datetime.weekday(dt.datetime.now())
    startTime = dt.datetime.now().strftime("%H")
    cur.execute("select * from shows where starttime = %s and weekday = %s", (startTime,weekday))
    show = cur.fetchall()
    print (startTime)
    if (len(show) > 0):
        return(show[0])
    else:
        return False
    con.close()
    
if __name__ == "__main__":
    print("Initializing Google Drive")
    rclone.set_config_file("./rclone.conf")
    print("Google Drive Initialized")
    print("Initializind Recorder")
    path='/recordings'
    stream_url = os.environ['STREAM_URL']
    rclone_drive = os.environ['RCLONE_DRIVE']
    if(not os.path.exists(path)):
        os.makedirs(path)
    while True:
        if(getShow()):
            show = getShow()
            print (f"Recording {show[1]}!")
            recording_filename = f"/recordings/{show[1]}-{dt.datetime.now().strftime('%Y-%m-%d')}.mp3"
            p = subprocess.Popen(["ffmpeg", "-i", steam_url, recording_filename])
            enddate = dt.date.min
            if (show[3] == 0):
                enddate=dt.date(1,1,2)
            showlength = math.floor(((dt.datetime.combine(enddate, dt.time(show[3],0,0)) - dt.datetime.min) - (dt.datetime.combine(dt.date.min, dt.datetime.now().time()) - dt.datetime.min)).total_seconds())
            time.sleep(showlength)
            p.terminate()
            rclone.mkdir(f'{rclone_drive}:{show[1]}')
            rclone.copy(recording_filename, f'{rclone_drive}:{show[1]}')
        else:
            print("Waiting for show...")
            time.sleep(1)
            

