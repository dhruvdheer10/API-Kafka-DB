# app/schemas/poll_request.py
from pydantic import BaseModel
from typing import List

class PollRequest(BaseModel):
    symbols: List[str]
    interval: int  # in seconds
    provider: str = "alpha_vantage"
