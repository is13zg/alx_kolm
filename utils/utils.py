import os

from create_bot import bot
import create_bot
import json
import inspect
import random
import string
import config
import asyncio
from aiogram.types import FSInputFile
import init_data


async def big_send(chat_id, content, sep="\n", tag=""):
    await bot.send_message(chat_id, f"!!! {tag} = len {len(content)} !!!", disable_notification=True)
    reply = sep.join(content)
    if len(reply) > 4096:
        await bot.send_message(chat_id, f"== {tag} BEGIN ==", disable_notification=True)

        while len(reply) > 4096:
            x = reply[:4096]
            i = x.rfind(sep)
            await bot.send_message(chat_id, x[:i], disable_notification=True)
            await asyncio.sleep(0.3)
            reply = reply[i:]
        if len(reply) > 0:
            await bot.send_message(chat_id, reply, disable_notification=True)

        await bot.send_message(chat_id, f"== {tag} END ==", disable_notification=True)
    else:
        await bot.send_message(chat_id, reply)


def unpuck_json(file_name: str) -> dict:
    try:
        with open(file_name, "r", encoding='utf-8') as jsonr:
            return json.load(jsonr)
    except Exception as e:
        create_bot.print_error_message(__name__, inspect.currentframe().f_code.co_name, e)



def get_menu_names(interaction_json: json):
    try:
        menus = dict()
        answers = dict()
        for k in interaction_json['menus']:
            for key, value in k.items():
                for item in value:
                    if item['type'] == 'menu':
                        menus[item['menu_name']] = item['text']
                    if item['type'] == 'text':
                        answers[item['answer']] = item['text']

        menus["menu0"] = "Начальное меню"
        return menus, answers
    except Exception as e:
        create_bot.print_error_message(__name__, inspect.currentframe().f_code.co_name, e)


def update_interaction_answer():
    return unpuck_json(config.Interaction_file_name), unpuck_json(config.Answers_file_name)


async def make_response_data(chat_id: int, data: list, frmt: str = "auto", send_name: str = "current_list") -> None:
    try:
        if len(data) == 0:
            await bot.send_message(chat_id, text=f"{send_name} is empty !!!", disable_notification=True)
            return
        if (frmt == 'f') or (frmt == "auto" and len(data) >= 100):
            with open(send_name + ".txt", "w", encoding='utf-8') as txtf:
                txtf.write("\n".join(list(map(lambda x: x.lower(), data))))
            await bot.send_document(chat_id, FSInputFile(send_name + ".txt"), disable_notification=True)
            os.remove(send_name + ".txt")

        elif (frmt == "msg") or (frmt == "auto" and len(data) < 100):
            await big_send(chat_id, data, tag=send_name)

    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)