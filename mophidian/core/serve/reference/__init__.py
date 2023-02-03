import os

from .app import start_cli_service

env = (os.environ.get("env") or "prod").lower()
is_dev = env == "dev" or env == "local"
port, autoreload_observer = start_cli_service(autoreload=is_dev)
if autoreload_observer:
    # move autoreload observer to the foreground so process won't exit
    # while reloading.
    autoreload_observer.join()