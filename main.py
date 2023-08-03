import logging
from create_bot import bot, dp
import asyncio
from handlers import client
logger = logging.getLogger(__name__)


async def main() -> None:
    # dp.include_router(superadmin.router)
    # dp.include_router(admin.router)
    dp.include_router(client.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())