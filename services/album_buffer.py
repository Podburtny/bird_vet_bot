import asyncio
from collections import defaultdict


class AlbumBuffer:
    def __init__(self) -> None:
        self._items: dict[str, list] = defaultdict(list)
        self._tasks: dict[str, asyncio.Task] = {}
        self._locks: dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)

    async def add(self, media_group_id: str, item, delay: float, callback) -> None:
        async with self._locks[media_group_id]:
            self._items[media_group_id].append(item)

            old_task = self._tasks.get(media_group_id)
            if old_task:
                old_task.cancel()

            self._tasks[media_group_id] = asyncio.create_task(
                self._flush_after_delay(media_group_id, delay, callback)
            )

    async def _flush_after_delay(self, media_group_id: str, delay: float, callback) -> None:
        try:
            await asyncio.sleep(delay)

            async with self._locks[media_group_id]:
                items = self._items.pop(media_group_id, [])
                self._tasks.pop(media_group_id, None)

            if items:
                await callback(items)

        except asyncio.CancelledError:
            return