import asyncio
import config
import client
import ui

async def background_tasks():
   while True:
        if config.DEBUG:
            print("bg worker running")
        await asyncio.sleep(2)

async def main():
    if config.DEBUG:
        print("starting flet ui")
    worker = asyncio.create_task(background_tasks())
    await ui.start()

    if config.DEBUG:
        print("ui closed stopping bg tasks")

    worker.cancel()

if __name__ == "__main__":
    asyncio.run(main())
