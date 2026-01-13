import httpx
from collections import namedtuple


Response = namedtuple('Response', ['ok', 'status_code', 'format', 'data', 'error'])


def detect_format(content_type: str) -> str:
    content_type = content_type.lower()

    if "application/json" in content_type:
        return "json"
    if "text/csv" in content_type:
        return "csv"
    if "text/plain" in content_type:
        return "text"
    return "binary"


async def safe_request(method, url, *,headers=None, params=None, json=None, timeout=10) -> Response:
    async with httpx.AsyncClient() as client:

        try:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                timeout=timeout,
                json=json
            )

            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "")
            data_format = detect_format(content_type)

            if data_format == "json":
                data = response.json()
            elif data_format in ("csv", "text"):
                data = response.text
            else:
                data = response.content

            return Response(
                ok=True,
                status_code=response.status_code,
                format=data_format,
                data=data,
                error=None
            )

        except Exception as e:
            return Response(
                ok=False,
                status_code=None,
                format=None,
                data=None,
                error=str(e)
            )
    
