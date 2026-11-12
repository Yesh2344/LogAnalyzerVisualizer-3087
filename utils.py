import re
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Regular expression for the Common Log Format
LOG_PATTERN = re.compile(
    r'(?P<host>\S+) '               # host %h
    r'(?P<ident>\S*) '              # ident %l (unused)
    r'(?P<authuser>\S*) '           # authuser %u
    r'\[(?P<datetime>[^\]]+)\] '    # datetime %t
    r'"(?P<request>[^"]*)"\s'       # request "%r"
    r'(?P<status>\d{3}) '           # status %>s
    r'(?P<size>\S+)'                # size %b (may be '-')
)

# Example datetime format: 10/Oct/2000:13:55:36 -0700
DATETIME_FORMAT = "%d/%b/%Y:%H:%M:%S %z"

def parse_log_line(line: str) -> Optional[Dict[str, Any]]:
    """
    Parse a single log line.
    Returns a dict with keys: host, ident, authuser, datetime, method, path,
    protocol, status, size. Returns None if line cannot be parsed.
    """
    match = LOG_PATTERN.match(line)
    if not match:
        logger.debug("Failed to match log line: %s", line.strip())
        return None

    data = match.groupdict()
    try:
        # Parse datetime
        dt = datetime.strptime(data["datetime"], DATETIME_FORMAT)
    except ValueError as exc:
        logger.debug("Datetime parse error: %s (%s)", exc, data["datetime"])
        return None

    # Split request into method, path, protocol
    request_parts = data["request"].split()
    method, path, protocol = (request_parts + ["", "", ""])[:3]

    size = data["size"]
    size = int(size) if size.isdigit() else 0

    return {
        "host": data["host"],
        "ident": data["ident"] or None,
        "authuser": data["authuser"] or None,
        "timestamp": dt.isoformat(),
        "method": method,
        "path": path,
        "protocol": protocol,
        "status": int(data["status"]),
        "size": size,
    }

def parse_log_file(filepath: str) -> List[Dict[str, Any]]:
    """
    Parse an entire log file.
    Returns a list of dicts, one per successfully parsed line.
    """
    logs = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line_number, line in enumerate(f, 1):
                parsed = parse_log_line(line)
                if parsed:
                    logs.append(parsed)
                else:
                    logger.warning("Unparsable line %d in %s", line_number, filepath)
    except FileNotFoundError:
        logger.error("Log file not found: %s", filepath)
        raise
    except Exception as exc:
        logger.exception("Error while reading log file.")
        raise
    logger.info("Parsed %d log entries from %s", len(logs), filepath)
    return logs

def filter_logs_by_datetime(
    logs: List[Dict[str, Any]],
    start: Optional[datetime],
    end: Optional[datetime]
) -> List[Dict[str, Any]]:
    """Return logs whose timestamp falls between start and end (inclusive)."""
    def in_range(entry):
        ts = datetime.fromisoformat(entry["timestamp"])
        if start and ts < start:
            return False
        if end and ts > end:
            return False
        return True
    return [log for log in logs if in_range(log)]

def filter_logs_by_status(
    logs: List[Dict[str, Any]],
    status_code: int
) -> List[Dict[str, Any]]:
    """Return logs matching a specific HTTP status code."""
    return [log for log in logs if log["status"] == status_code]