#!/opt/isync/venv/bin/python3
from loguru import logger
import sys
import time
import os
from inspect import getsourcefile
from watchdog.observers.polling import PollingObserverVFS
from watchdog.events import FileSystemEventHandler
from config import paths, remote, interval


# Create Observer to watch directories
observer = PollingObserverVFS(stat=os.stat, listdir=os.listdir,polling_interval=interval)


# Empty list of observers
observers = []

base_dir = os.path.dirname(getsourcefile(lambda:0))

logger.add(f"{base_dir}/isync.log", format="{time} {level} {message}", level="DEBUG", rotation="10 MB", compression="zip")

# check if files exist
for path in paths:
    if not os.path.exists(path):
        logger.error(f"path {path} does not exist")
        sys.exit(1)

class MonitorFolder(FileSystemEventHandler):
    def on_created(self, event):
        remote_path = os.path.dirname(event.src_path)
        logger.info(f"CREATE rsync -azpP {event.src_path} {remote}:{remote_path}")

    def on_modified(self, event):
        remote_path = os.path.dirname(event.src_path)
        logger.info(f"MODIFY  rsync -azpP {event.src_path} {remote}:{remote_path}")
        os.system(f"rsync -azpP {event.src_path} {remote}:{remote_path}")

    def on_deleted(self, event):
        logger.info(f"DELETE {event.src_path}")
        #os.system(f"ssh {remote} rm -f {event.src_path}")

# Attach a logging event AKA FileSystemEventHandler
event_handler = MonitorFolder()

# Iterate through paths and attach observers
for line in paths:

    # Convert line into string and strip newline character
    targetPath = str(line).rstrip()

    # Schedules watching of a given path
    observer.schedule(event_handler, targetPath, recursive=True)

    # Add observable to list of observers
    observers.append(observer)



if __name__ == '__main__':
       
        observer.start()
        try:
            while True:
                # Poll every second
                time.sleep(100)
        except:
            observer.stop()

        observer.join()
