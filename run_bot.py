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
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn.config
from mrhomebot import bot
from testing_tools.answer.answer_processing import AnswerProcessing
from utils.init_app import init_app
from mrhomebot.configuration import DOMAIN, WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV
import uvicorn


app = FastAPI()
answer_processing = AnswerProcessing(bot)


@app.post('/webhook')
async def webhook(request: Request):
    json_data = await request.json()
    update = bot.process_new_updates([json_data])
    await answer_processing.run()
    return JSONResponse(content={'status': 'success'}, status_code=200)


if __name__ == "__main__":
    init_app()

    bot.remove_webhook()
    bot.set_webhook(
        url=f"https://{DOMAIN}/webhook",
        certificate=open(WEBHOOK_SSL_CERT, 'rb')
    )
    uvicorn.run(app,
                host='0.0.0.0',
                port=8443,
                ssl_certfile=WEBHOOK_SSL_CERT,
                ssl_keyfile=WEBHOOK_SSL_PRIV)
