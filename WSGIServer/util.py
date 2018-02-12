import fcntl
import os


def close_on_exec(fd):
    """
    This works by OR the FD_CLOEXEC with the
    existing flags of file descriptor fd,
    and setting them back to fd. 

    FD_CLOEXEC is used to mark flag descriptors
    for closing when exec is called.
    So that when the context of the program changes
    due to an exec call, the file descriptor is closed.

    "When a file descriptor is allocated, this bit is initially
    cleared on the new file descriptor, meaning that descriptor
    will survive into the new program after exec." - gnu.org

    Works for socket fds as well.
    """
    flags = fcntl.fcntl(fd, fcntl.F_GETFD)
    flags |= fcntl.FD_CLOEXEC
    fcntl.fcntl(fd, fcntl.F_SETFD, flags)

