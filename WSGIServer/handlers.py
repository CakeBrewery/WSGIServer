import os
import signal
import errno


# Predefine signal handlers for program scope
# TODO: Figure out where to put these

# The idea is to have each fork be a "worker", the same way gunicorn does it.


def _sigchld(signum, stack):
    # SIGCHLD indicates that a worker has stopped.
    # We must do this to avoid Zombie processes
    while True:
        try:
            # WNOHANG makes this non-blocking
            pid, status = os.waitpid(-1, os.WNOHANG)
        except OSError as e:
            if e.errno != errno.ECHILD:
                raise
            return

        if not pid:
            break


_HANDLERS = {
    'SIGCHLD': _sigchld
}


def get_handler(signal_name):
    return _HANDLERS(signal_name)


def initialize_handlers():
    for handler, callback in _HANDLERS.items():
        if hasattr(signal, handler):
            signal.signal(getattr(signal, handler), callback)

