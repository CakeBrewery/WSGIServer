import os
import signal


# Predefine signal handlers for program scope
# TODO: Figure out where to put these


def _sigchld(signum, stack):
    print('TEST')
    while True:
        try:
            # WNOHANG makes this non-blocking
            pid, status = os.waitpid(-1, os.WNOHANG)
        except OSError:
            return

        if pid == 0:
            return


_HANDLERS = {
    'SIGCHLD': _sigchld
}


def get_handler(signal_name):
    return _HANDLERS(signal_name)


def initialize_handlers():
    for handler, callback in _HANDLERS.items():
        if hasattr(signal, handler):
            signal.signal(getattr(signal, handler), callback)

