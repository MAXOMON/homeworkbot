"""
Telegram bot launch module in a separate process
Example:
    $ python run_bot.py

import asyncio

from mrhomebot import bot
from testing_tools.answer.answer_processing import AnswerProcessing
from utils.init_app import init_app
from mrhomebot.configuration import DOMAIN, WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV


async def main():
    running telegram bot in infinite loop

    await asyncio.gather(
        bot.infinity_polling(request_timeout=90),
        AnswerProcessing(bot).run()
    )


if __name__ == "__main__":
    init_app()
    asyncio.run(main())
"""
import asyncio
import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from mrhomebot import bot
from testing_tools.answer.answer_processing import AnswerProcessing
from testing_tools.checker.task_processing import TaskProcessing
from utils.init_app import init_app
import telebot
import uvicorn
from dotenv import load_dotenv


load_dotenv()

API_TOKEN = os.getenv('BOT_TOKEN')
DOMAIN = os.getenv('DOMAIN')
PORT = 88
WEBHOOK_SSL_CERT = "../public.pem"
WEBHOO_SSL_PRIV = "../private.key"
LISTEN_IP = '0.0.0.0'

app = FastAPI(docs=None, redoc_url=None, docs_url=None)

@app.post(f'/{API_TOKEN}/run_bot')
async def process_webhook(update: dict):
    if update:
        update = telebot.types.Update.de_json(update)
        await bot.process_new_updates([update])

        return JSONResponse(content={'status': 'success'}, status_code=200)
    return JSONResponse(content={'status': 'no update'}, status_code=400)


async def set_webhook():
    await bot.remove_webhook()
    await bot.set_webhook(
        url=f"https://{DOMAIN}:{PORT}/{API_TOKEN}/run_bot",
        certificate=open(WEBHOOK_SSL_CERT, "r")
    )


if __name__ == "__main__":
    init_app()

    try:
        asyncio.run(set_webhook())
        uvicorn.run(app,
                    host=LISTEN_IP,
                    port=PORT,
                    ssl_certfile=WEBHOOK_SSL_CERT,
                    ssl_keyfile=WEBHOO_SSL_PRIV,
                    access_log=True)
    except:
        ...
    finally:
        asyncio.run(bot.close_session())
