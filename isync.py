from loguru import logger
import sys
import time
import os
import yaml
from dictor import dictor
from inspect import getsourcefile
from watchdog.observers.polling import PollingObserverVFS
from watchdog.events import FileSystemEventHandler
base_dir = os.path.dirname(getsourcefile(lambda:0))

with open(f"{base_dir}/config.yml", "r") as file:
    try:
        cfg = yaml.safe_load(file)
    except yaml.YAMLError as e:
        print(str(e))
        sys.exit(1)

# init logging
log_level = dictor(cfg, "log.level", "INFO").upper()
log_format = "{time} {level} [isync] {message}" 
logger.remove(0)

if dictor(cfg, "log.destination") == "console":
    logger.add(sys.stderr, format=log_format, level=log_level, colorize=True)
else:
    logger.add(dictor(cfg, 'log.destination'), 
    format=log_format, 
    level=log_level, 
    rotation="10 MB",
    retention="5 days", 
    compression="zip")

logger.debug(base_dir)
logger.info("d1")

# create a lookup dict
key_dict = {}
for sync in dictor(cfg, "syncs", checknone=True):

    source_path = dictor(cfg, f"syncs.{sync}.source_path", checknone=True)
    
    if not os.path.exists(source_path):
        logger.error(f"path {source_path} does not exist")
        sys.exit(1)
    
    if not dictor(cfg, f"syncs.{sync}.priv_key") and not dictor(cfg, f"defaults.priv_key"):
        logger.error(f"must provide SSH private key for sync '{sync}'")
        sys.exit(1)

    if source_path not in key_dict.keys():
        key_dict[source_path] = []

    # set ssh port
    if not dictor(cfg, f"syncs.{sync}.port"):
        if not dictor(cfg, "defaults.port"):
            cfg["syncs"][sync]["port"] = 22
        else:
            cfg["syncs"][sync]["port"] = dictor(cfg, "defaults.port")
    
    # set recurse
    if not dictor(cfg, f"syncs.{sync}.recurse"):
        if not dictor(cfg, "defaults.recurse"):
            cfg["syncs"][sync]["recurse"] = False
        else:
            cfg["syncs"][sync]["recurse"] = dictor(cfg, "defaults.recurse")
    
    # set simulate
    if not dictor(cfg, f"syncs.{sync}.simulate"):
        if not dictor(cfg, "defaults.simulate"):
            cfg["syncs"][sync]["simulate"] = True
        else:
            cfg["syncs"][sync]["simulate"] = dictor(cfg, "defaults.simulate")

    # set rsync opts
    if not dictor(cfg, f"syncs.{sync}.rsync_opts"):
        if not dictor(cfg, "defaults.rsync_opts"):
            cfg["syncs"][sync]["rsync_opts"] = "azP"
        else:
            cfg["syncs"][sync]["rsync_opts"] = dictor(cfg, "defaults.rsync_opts")

    key_dict[source_path].append(cfg["syncs"][sync])
    logger.warning(key_dict)

class MonitorFolder(FileSystemEventHandler):
    def on_created(self, event):
        remote_path = os.path.dirname(event.src_path)

        logger.info(f"CREATE rsync -azpP {event.src_path} {remote_path}")

    def on_modified(self, event):
        logger.debug(f"MODIFIED: {event.src_path}")
        remote_path = os.path.dirname(event.src_path)
        for sync in key_dict[event.src_path]:
            logger.debug(f"syncing {event.src_path} to {sync['remote_user']}@{sync['remote_host']}:{sync['remote_path']}")
            if sync['remote_host'] in ['localhost', '127.0.0.1']:
                cmd = f"rsync -azP {event.src_path} {sync['remote_path']}/"
            else:
                cmd = f"rsync -e 'ssh -p 22 -i {sync['priv_key']}' -azP {event.src_path} {sync['remote_user']}@{sync['remote_host']}:{sync['remote_path']}/"
#        os.system(f"rsync -azpP {event.src_path} {remote}:{remote_path}")
            logger.debug(cmd)

    def on_deleted(self, event):
        logger.info(f"DELETE {event.src_path}")
        #os.system(f"ssh {remote} rm -f {event.src_path}")

# Attach a logging event AKA FileSystemEventHandler
event_handler = MonitorFolder()

interval = dictor(cfg, "defaults.interval", default=20)
# Create Observer to watch directories
observer = PollingObserverVFS(stat=os.stat, listdir=os.listdir, polling_interval=interval)
observers = []

# Iterate through src paths and attach observers
for sync in cfg["syncs"]:
    source_path = dictor(cfg, f"syncs.{sync}.source_path").rstrip()
    recurse = dictor(cfg, f"syncs.{sync}.recurse")
    if not recurse:
        recurse = dictor(cfg, "defaults.recurse", default=False)
    # Schedules watching of a given path
    logger.info(f"adding path to observer {source_path}")
    observer.schedule(event_handler, source_path, recursive=True)

    # Add observable to list of observers
    observers.append(observer)

logger.warning(observers)

if __name__ == '__main__':

    observer.start()

    try:
        while True:
            # Poll every second
            time.sleep(100)
    except:
        observer.stop()
        observer.join()
