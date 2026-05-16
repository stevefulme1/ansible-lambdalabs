"""EDA event source plugin for Lambda Labs instance state changes."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import asyncio
import json
from typing import Any

from aiohttp import ClientSession, ClientTimeout


async def main(queue: asyncio.Queue, args: dict[str, Any]) -> None:
    """Poll the Lambda Labs API for instance state changes.

    Emits events:
      - instance_launched
      - instance_terminated
      - instance_error
      - gpu_degraded

    Args:
        queue: EDA event queue.
        args: Plugin arguments — api_key, poll_interval, instance_filter.
    """
    api_key = args["api_key"]
    poll_interval = int(args.get("poll_interval", 60))
    instance_filter = args.get("instance_filter")
    base_url = "https://cloud.lambda.ai/api/v1/instances"

    headers = {
        "Authorization": "Bearer {0}".format(api_key),
        "Accept": "application/json",
    }

    previous_states: dict[str, str] = {}

    timeout = ClientTimeout(total=30)

    async with ClientSession(headers=headers, timeout=timeout) as session:
        while True:
            try:
                async with session.get(base_url) as resp:
                    body = await resp.json()
                    instances = body.get("data", [])

                if instance_filter:
                    instances = [
                        i for i in instances
                        if i.get("name", "").startswith(instance_filter)
                        or i.get("id") == instance_filter
                    ]

                current_ids = set()

                for inst in instances:
                    iid = inst.get("id")
                    if not iid:
                        continue
                    current_ids.add(iid)

                    status = inst.get("status", "unknown")
                    prev = previous_states.get(iid)

                    if prev is None:
                        # First observation — treat active as launched
                        if status == "active":
                            await queue.put(
                                {
                                    "lambda_event": {
                                        "type": "instance_launched",
                                        "instance_id": iid,
                                        "instance": inst,
                                    }
                                }
                            )
                    elif status != prev:
                        if status == "active" and prev in ("booting", "unhealthy"):
                            await queue.put(
                                {
                                    "lambda_event": {
                                        "type": "instance_launched",
                                        "instance_id": iid,
                                        "instance": inst,
                                    }
                                }
                            )
                        elif status == "terminated":
                            await queue.put(
                                {
                                    "lambda_event": {
                                        "type": "instance_terminated",
                                        "instance_id": iid,
                                        "instance": inst,
                                    }
                                }
                            )
                        elif status == "unhealthy":
                            await queue.put(
                                {
                                    "lambda_event": {
                                        "type": "gpu_degraded",
                                        "instance_id": iid,
                                        "instance": inst,
                                    }
                                }
                            )
                        elif status == "error":
                            await queue.put(
                                {
                                    "lambda_event": {
                                        "type": "instance_error",
                                        "instance_id": iid,
                                        "instance": inst,
                                    }
                                }
                            )

                    previous_states[iid] = status

                # Detect disappeared instances (terminated externally)
                for gone_id in set(previous_states) - current_ids:
                    if previous_states[gone_id] != "terminated":
                        await queue.put(
                            {
                                "lambda_event": {
                                    "type": "instance_terminated",
                                    "instance_id": gone_id,
                                    "instance": {"id": gone_id},
                                }
                            }
                        )
                    del previous_states[gone_id]

            except Exception as exc:
                await queue.put(
                    {
                        "lambda_event": {
                            "type": "instance_error",
                            "error": str(exc),
                        }
                    }
                )

            await asyncio.sleep(poll_interval)


if __name__ == "__main__":

    class _MockQueue:
        async def put(self, item):
            print(json.dumps(item, indent=2))

    asyncio.run(main(_MockQueue(), {"api_key": "test", "poll_interval": "5"}))
