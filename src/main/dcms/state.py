"""Process-wide mutable state (contest timing, WebSocket clients)."""

import datetime
from typing import Dict, Optional

from fastapi import WebSocket

clients: Dict[str, WebSocket] = {}
contest_active = False
contest_start_time: Optional[datetime.datetime] = None
contest_end_time: Optional[datetime.datetime] = None
penalty_time = 20
