from typing import Dict
import hashlib
import re

import aiohttp
import asyncio


def make_http_range_header(first_byte_position: int, last_byte_position: int):
    return {
        "Range": "bytes={:d}-{:d}".format(first_byte_position, last_byte_position),
    }


def parse_http_content_range_header(value: str):
    m = re.match(r"^bytes (\d+)-(\d+)/(\d+)$", value)
    return {
        "first_byte_position": int(m.group(1)),
        "last_byte_position": int(m.group(2)),
        "content_length": int(m.group(3)),
    }


async def get_range(
    session: aiohttp.ClientSession,
    url: str,
    first_byte_position: int,
    last_byte_position: int,
):
    headers = make_http_range_header(first_byte_position, last_byte_position)
    async with session.get(url, headers=headers) as response:
        body = await response.read()
        return {
            "status": response.status,
            "content_type": response.headers["content-type"],
            "content_length": response.headers["content-length"],
            "content_range": response.headers["Content-Range"],
            "body": body,
        }


async def get_hash_async(url: str, hash_size: int) -> Dict:
    async with aiohttp.ClientSession() as session:
        result = await get_range(session, url, 0, hash_size - 1)
        assert result["status"] == 206
        hash = hashlib.sha1(result["body"]).hexdigest()
        content_range = parse_http_content_range_header(result["content_range"])
        return {
            "url": url,
            "content_type": result["content_type"],
            "content_length": content_range["content_length"],
            "hash_size": hash_size,
            "hash": hash,
        }


def get_hash(url: str, hash_size: int) -> Dict:
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(get_hash_async(url, hash_size))


def get_extension(mime_type: str) -> str:
    return {"video/mp4": ".mp4"}[mime_type]


def get_object_info(url: str) -> Dict:
    hash_size = 1000 * 1000 * 10  # 10 MB
    hash_info = get_hash(url, hash_size)
    extension = get_extension(hash_info["content_type"])
    object_info = hash_info.copy()
    object_info["extension"] = extension
    object_info["object_id"] = hash_info["hash"] + extension
    return object_info
