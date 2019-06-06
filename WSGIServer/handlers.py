import os
import signal
import errno


# Predefine signal handlers for program scope
# TODO: Figure out where to put these

# The idea is to have each fork be a "worker", the same way gunicorn does it.


def _sigchld(signum, stack):
    # SIGCHLD happens when a child process exits.
    # In order for the parent to retrieve the exit status of a child, 
    # the entry remains in the process table even though the child is done.
    # aka a zombie process. To obtain the status, call "wait" on the process.
    # We must do this to avoid Zombie processes.
    
    # This triggers when SIGCHLD happens. Iterates over all done processes
    # (WNOHANG so that only done processes show up and we don't wait for undone ones)
    # Iterates over all done processes and "waits" them, which removes them from process table.
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
    return _HANDLERS.get(signal_name)


def initialize_handlers():
    # Set callbacks that run when a specific signal triggers. 
    for handler, callback in _HANDLERS.items():
        if hasattr(signal, handler):
            signal.signal(getattr(signal, handler), callback)

