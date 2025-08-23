import os
import sys
import logging
from logging.handlers import TimedRotatingFileHandler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, 'app.log')

ROOT_LOG_LEVEL = logging.WARNING
PROJECT_LOGGER_NAME = "app"

DATE_FMT = "%Y-%m-%d %H:%M:%S"

def _rel(path: str) -> str:
    """Return *repo-relative* path or just the basename if outside repo."""
    try:
        p = os.path.relpath(path, BASE_DIR)
        return p if not p.startswith("..") else os.path.basename(path)
    except Exception:
        return os.path.basename(path)


_old_factory = logging.getLogRecordFactory()


def _record_factory(*a, **kw):  # type: ignore[override]
    r = _old_factory(*a, **kw)
    r.relativepath = _rel(r.pathname)
    return r


logging.setLogRecordFactory(_record_factory)

class PathAwareFormatter(logging.Formatter):
    def __init__(self, fmt_src: str, fmt_no_src: str, **kw):
        super().__init__(fmt_src, **kw)
        self.fmt_src, self.fmt_no_src = fmt_src, fmt_no_src

    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        hide = getattr(record, "hide_src", False) or record.name.startswith("uvicorn.")
        orig = self._style._fmt
        self._style._fmt = self.fmt_no_src if hide else self.fmt_src
        try:
            return super().format(record)
        finally:
            self._style._fmt = orig

# Templates
FILE_FMT_SRC = "%(asctime)s | %(levelname)-8s | %(relativepath)s:%(lineno)d | %(message)s"
FILE_FMT_NOSRC = "%(asctime)s | %(levelname)-8s | %(message)s"
CON_FMT_SRC = "%(levelname)-8s | %(relativepath)s:%(lineno)d | %(message)s"
CON_FMT_NOSRC = "%(levelname)-8s | %(message)s"

# Instantiate formatters
file_formatter = PathAwareFormatter(FILE_FMT_SRC, FILE_FMT_NOSRC, datefmt=DATE_FMT)
console_formatter = PathAwareFormatter(CON_FMT_SRC, CON_FMT_NOSRC, datefmt=DATE_FMT)

file_handler = TimedRotatingFileHandler(
    filename=LOG_FILE,
    when="midnight",
    interval=1,
    backupCount=30,
    encoding="utf-8",
)
file_handler.setLevel(logging.INFO)  # keep everything ≥ INFO
file_handler.setFormatter(file_formatter)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)  # show DEBUG locally
console_handler.setFormatter(console_formatter)


# Non-blocking queue setup
log_queue: Queue = Queue(-1)

queue_handler = QueueHandler(log_queue)
queue_listener = QueueListener(
    log_queue,
    file_handler,
    console_handler,
    respect_handler_level=True,
)
queue_listener.start()
atexit.register(queue_listener.stop)

# Root logger: tame 3rd-party noises
root_logger = logging.getLogger()
root_logger.handlers.clear()
root_logger.setLevel(ROOT_LOG_LEVEL)  # WARNING / ERROR only

# Project logger: owns the queue + handlers
project_logger = logging.getLogger(PROJECT_LOGGER_NAME)
project_logger.handlers.clear()
project_logger.setLevel(logging.DEBUG)  # full verbosity on project(app) level
project_logger.addHandler(queue_handler)
project_logger.propagate = False

# Make Uvicorn log through the same pipeline
for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
    uv = logging.getLogger(name)
    uv.handlers.clear()  # remove its defaults
    uv.addHandler(queue_handler)  # reuse our pipeline
    uv.setLevel(logging.INFO)  # or DEBUG/ERROR …
    uv.propagate = False  # don’t reach root

# Squash noisy libs
logging.getLogger("passlib.handlers.bcrypt").setLevel(logging.CRITICAL)

# Public object
logger = project_logger