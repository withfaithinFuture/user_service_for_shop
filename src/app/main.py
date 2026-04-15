from dotenv import load_dotenv

load_dotenv()

import asyncio
import logging

import uvicorn

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)-20s - %(levelname)-8s - %(message)s",
    datefmt="%H:%M:%S",
)


async def main() -> None:
    uvicorn.run(
        "src.app.application:get_app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        factory=True,
        reload_dirs=["/app/src"],
    )


if __name__ == "__main__":
    asyncio.run(main())
