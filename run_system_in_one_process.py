"""
The module for launching both the bot 
and the testing verification system in one process.
Example:
    $ python run_system_in_one_process.py
"""
import asyncio
import os
from pathlib import Path
from multiprocessing import Process
from threading import Thread
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
WEBHOOK_SSL_CERT = "public.pem"
WEBHOO_SSL_PRIV = "private.key"
LISTEN_IP = '0.0.0.0'

app = FastAPI(docs=None, redoc_url=None, docs_url=None)

temp_path = Path.cwd()
temp_path = Path(temp_path.joinpath(os.getenv("TEMP_REPORT_DIR")))
dockers_run = int(os.getenv("AMOUNT_DOKER_RUN"))


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

def run_uvicorn():
    uvicorn.run(app,
                host=LISTEN_IP,
                port=PORT,
                ssl_certfile=WEBHOOK_SSL_CERT,
                ssl_keyfile=WEBHOO_SSL_PRIV,
                access_log=True)

async def run_processing():
    temp_path = Path.cwd()
    temp_path = Path(temp_path.joinpath(os.getenv("TEMP_REPORT_DIR")))
    dockers_run = int(os.getenv("AMOUNT_DOKER_RUN"))

    await asyncio.gather(
        AnswerProcessing(bot).run(),
        TaskProcessing(temp_path, dockers_run).run(),
    )

def run_asyncio_processing():
    asyncio.run(run_processing())


if __name__ == "__main__":
    init_app()
    try:
        uvicorn_process = Process(target=run_uvicorn)
        uvicorn_process.start()
        asyncio.run(set_webhook())
        run_asyncio_processing()
        uvicorn_process.join()
    except:
        ...
    finally:
        uvicorn_process.join()
        uvicorn_process.close()
        asyncio.run(
            bot.close_session()
        )
    
