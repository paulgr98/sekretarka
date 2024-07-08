import asyncio

from g4f import api
from uvicorn import Config, Server


async def run_api():
    app = api.create_app()
    config = Config(app, host="localhost", port=1337, log_level="info")
    server = Server(config)
    await server.serve()


if __name__ == '__main__':
    asyncio.run(run_api())
