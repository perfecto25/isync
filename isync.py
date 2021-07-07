#!/home/mreider/isync/venv/bin/python3
from loguru import logger
import sys
import time
import os
from inspect import getsourcefile
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from config import paths, remote


# Create Observer to watch directories
observer = Observer()

# Empty list of observers
observers = []

base_dir = os.path.dirname(getsourcefile(lambda:0))

logger.add(f"{base_dir}/isync.log", format="{time} {level} {message}", level="DEBUG")

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
        #os.system(f"rsync -azpP {event.src_path} {remote}:{remote_path}")

    def on_deleted(self, event):
        logger.info(f"DELETE {event.src_path}")
        #os.system(f"ssh {remote} rm -f {event.src_path}")

    # def checkFolderSize(self, src_path):
    #     if os.path.isdir(src_path):
    #         if os.path.getsize(src_path) > self.FILE_SIZE:
    #             print("Time to backup the dir")
    #     else:
    #         if os.path.getsize(src_path) > self.FILE_SIZE:
    #             print("very big file")


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
    
        while True:
            # Poll every second
            time.sleep(1)


       # for o in observers:
       #     o.unschedule_all()
       #     # Stop observer if interrupted
       #     o.stop()

       # for o in observers:
       #     # Wait until the thread terminates before exit
       #     o.join()
