import logging
import traceback
import re
import itertools


logger = logging.getLogger(__name__)
 
"""Collection of functions I find useful that do not have any more specific categories."""


def log_traceback(exc_type, exc_value, exc_traceback=None):
    """Logs traceback on single line - good for syslog servers. Works well with `sys.excepthook = log_traceback`"""
    logger.info("UNCAUGHT EXCEPT!")
    if not any([exc_type, exc_value, exc_traceback]):
        stack_trace = traceback.extract_stack()
        logger.exception("UNCAUGHT_EXCEPTION: %s", stack_trace)
    tb_strings = traceback.format_exception(exc_type, exc_value, exc_traceback)
    tb_single_line = []
    for line in tb_strings:
        if not line:
            continue
        line_fields = [field.strip() for field in line.strip().split('\n')]
        # Prevent issues with mysql over-escaping quoted strings in traceback
        # So if you need to put this log into MYSQL for some reason
        line_fields = [lf.replace("'", "") for lf in line_fields]
        for field in line_fields:
            tb_single_line.append(field)
    tb_one_line = " - ".join(tb_single_line)
    tb_one_line = f"SYS_EXCEPT_HOOK_CATCH: {tb_one_line}"
    msg = " - ".join([str(dat) for dat in [exc_type, exc_value, tb_one_line]])
    logger.error(msg)


def chunked_iterable(iterable, size):
    """Return chunks of an iterable based on requested size."""
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, size))
        if not chunk:
            break
        if isinstance(iterable, dict):
            yield {k: iterable[k] for k in chunk}
        else:
            yield chunk


def camel_to_snake(string):
    """Convert CamelCase to snake_case."""
    string = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', string)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', string).lower()
