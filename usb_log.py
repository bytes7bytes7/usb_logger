from time import sleep
from logging.handlers import RotatingFileHandler
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from datetime import datetime
from win32api import GetLogicalDriveStrings, GetVolumeInformation
from win32file import GetDriveType
import win32con, logging, sys

logFile = 'logs.log'
allDrives=[]
observersMap = {}

def log(drive,status):
	time=datetime.now()
	year=str(time.year)
	month=str(time.month)
	day=str(time.day)
	hour=str(time.hour)
	minute=str(time.minute)
	if len(month) < 2:
		month = '0'+month
	if len(day) < 2:
		day = '0'+day
	if len(hour) < 2:
		hour = '0'+hour
	if len(minute)<2:
		minute = '0'+minute
	t=hour+':'+minute+'	'+day+'.'+month+'.'+year
	try:
		f=open(logFile,'a')
		f.write(t+'	'+status+' '+drive[0]+'	'+drive[1]+'\n')
		f.close()
	except:
		f=open(logFile)
		f.write(t+'	'+status+' '+drive[0]+'	'+drive[1]+'\n')
		f.close()


def getDrives():
	driveFiltersExamples = [
		(None, "All"),
		((win32con.DRIVE_REMOVABLE,), "Removable")
	]

	for (driveTypesTuple, displayText) in driveFiltersExamples:
		drivesStr = GetLogicalDriveStrings()
		drives = [item for item in drivesStr.split("\x00") if item]
		drives = [item[:3] for item in drives if driveTypesTuple is None or GetDriveType(item) in driveTypesTuple]
		break
	
	return drives


def startSpy(path):
	logging.basicConfig(
        handlers=[RotatingFileHandler(logFile, maxBytes=100000, backupCount=10)],
        level=logging.DEBUG,
        format="%(asctime)s	%(message)s",
        datefmt='%H:%M	%d.%m.%Y')
	event_handler = LoggingEventHandler()
	observer = Observer()
	observer.schedule(event_handler, path, recursive=True)
	observer.start()

	observersMap[path] =observer


def stopSpy(path):
	observer =	observersMap[path]
	observer.stop()
	observer.join()
	del observersMap[path]


while 1:
	sleep(1)
	drives = getDrives()
	for i in range(len(drives)-1,-1,-1):
		name=GetVolumeInformation(drives[i])[0]
		if name != '':
			drives[i]=(drives[i],name)
		else:
			del drives[i]
	if sorted(drives) != allDrives:
		for dr in drives:
			if dr not in allDrives:
				log(dr,'Added drive:')
				startSpy(dr[0])
		for dr in allDrives:
			if dr not in drives:
				log(dr,'Removed drive:')
				stopSpy(dr[0])

		allDrives=sorted(drives.copy())