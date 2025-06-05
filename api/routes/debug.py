import os

import httpx
from fastapi import APIRouter, Depends, Request
from fastapi.responses import PlainTextResponse

from utils import atimer, generate_key, send_to_bark

router = APIRouter(tags=["Debug"], prefix="/debug")


@router.get("/raise_error")
@atimer
async def raise_error():
    raise ValueError("Something went wrong!")
