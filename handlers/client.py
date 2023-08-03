from create_bot import bot
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Router
import init_data
from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Router
from aiogram.types import CallbackQuery
import config
import asyncio

import create_bot
import inspect

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from utils.ReviewState import WaitReview

router = Router()


class OrderReview(StatesGroup):
    getting_review_photo = State()
    choosing_food_size = State()


def get_needed_menu_from_json(menu_name: str) -> list:
    try:
        inter_dict = init_data.interaction_json
        if any(menu_name in d for d in inter_dict["menus"]):
            for menu in inter_dict["menus"]:
                if menu_name in menu:
                    return menu[menu_name]
        else:
            return []
    except Exception as e:
        create_bot.print_error_message(__name__, inspect.currentframe().f_code.co_name, e)


# gen_universal_callback_data
def get_universal_callback_data(item: dict) -> str:
    try:
        universal_callback_data = "UCD_" + item['type']
        if item['type'] == "text":
            universal_callback_data += "_" + item['answer']
        elif item['type'] == "menu":
            universal_callback_data += "_" + item['menu_name']
        elif item['type'] == "do":
            universal_callback_data += "_" + item['answer']
        elif "review" in item['type']:
            universal_callback_data += "_" + item['answer']
        return universal_callback_data
    except Exception as e:
        create_bot.print_error_message(__name__, inspect.currentframe().f_code.co_name, e)


def form_tlg_menu_items(menu_from_json: list = None, msgs_ids: list = None) -> InlineKeyboardMarkup:
    try:
        builder = InlineKeyboardBuilder()
        if menu_from_json is None:
            menu_from_json = []

        if msgs_ids is None:
            msgs_ids = []

        for item in menu_from_json:
            builder.row(InlineKeyboardButton(text=item['text'], callback_data=get_universal_callback_data(item)))
        if not init_data.MIN_mode:
            builder.row(InlineKeyboardButton(text="❌", callback_data="delete_msg#" + " ".join(msgs_ids)))
        return InlineKeyboardMarkup(inline_keyboard=builder.export())
    except Exception as e:
        create_bot.print_error_message(__name__, inspect.currentframe().f_code.co_name, e)



@router.message(WaitReview.GET_REVIEW_PHOTO)
async def command_start_handler(message: Message, state: FSMContext) -> None:
    try:
        if not message.photo:
            await state.set_state(WaitReview.GET_REVIEW_PHOTO)
            await message.answer("Пришлите фото/скриншот отзыва чтобы получить подарок!")
        else:
            await message.answer(text="Фото получено, будет выполнена проверка отзыва.")
            await state.clear()
            await asyncio.sleep(5)
            await message.answer(text="Ваш бонус")
            await message.answer(text="<pre>Выберите пособие:</pre>", parse_mode="HTML",
                                 reply_markup=form_tlg_menu_items(get_needed_menu_from_json("menu0")))

        return
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)


@router.callback_query(lambda callback_query: callback_query.data[:10] == "delete_msg")
async def process_callback_delete_msg(callback_query: CallbackQuery):
    try:
        await callback_query.message.delete()
        ls = callback_query.data.split("#")
        for ids in ls[1].split():
            await bot.delete_message(callback_query.message.chat.id, int(ids))
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)


@router.callback_query(lambda callback_query: callback_query.data[:3] == "UCD")
async def universal_callback_response(callback_query: CallbackQuery, state: FSMContext):
    try:
        cd_ls = callback_query.data.split("_")

        if cd_ls[1] == "menu":
            await bot.send_message(callback_query.from_user.id,
                                   text="<pre>Вы выбрали пункт меню:\n" + init_data.menu_names[cd_ls[2]] + "</pre>",
                                   parse_mode="HTML",
                                   reply_markup=form_tlg_menu_items(get_needed_menu_from_json(cd_ls[2])))
            await callback_query.answer()
        elif cd_ls[1] == "text":
            id1 = await bot.send_message(callback_query.from_user.id,
                                         text=f"<pre>{init_data.answer_names[cd_ls[2]]}</pre>",
                                         parse_mode="HTML")
            await bot.send_message(callback_query.from_user.id, text=init_data.answer_json[cd_ls[2]]["text"],
                                   reply_markup=form_tlg_menu_items(msgs_ids=[str(id1.message_id)]))
            await callback_query.answer()
        elif cd_ls[1] == "do":
            await bot.send_message(callback_query.from_user.id, init_data.answer_json[cd_ls[2]]["text"],
                                   reply_markup=form_tlg_menu_items())
            await callback_query.answer()
            return
        elif cd_ls[1] == "reviewtu":
            await bot.send_message(callback_query.from_user.id, init_data.answer_json[cd_ls[2]]["text"],
                                   reply_markup=form_tlg_menu_items())
            await state.set_state(WaitReview.GET_REVIEW_PHOTO)
            return
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)


@router.message(Command(commands=["start"]))
async def command_start_handler(message: Message) -> None:
    try:
        # регистрируем пользователя в базе
        if not init_data.db.reg_user_exists(message.from_user.id):
            init_data.db.add_reg_user_to_db(message.from_user.id)
        # отдаем пользователю меню
        await message.answer(text="<pre>Выберите пособие:</pre>", parse_mode="HTML",
                             reply_markup=form_tlg_menu_items(get_needed_menu_from_json("menu0")))
        return
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)





@router.message(Command(commands=["отзыв", "otziv"]))
async def command_reviev_handler(message: Message) -> None:
    try:
        # регистрируем пользователя в базе
        if not init_data.db.reg_user_exists(message.from_user.id):
            init_data.db.add_reg_user_to_db(message.from_user.id)

        if len(message.text.split()) <= 1:
            await message.answer(
                "Чтобы оставить отзыв или предложение напишите в данный чат: \n/отзыв [ваш отзыв] \n\n Пример: <pre>/отзыв пожалуйста публикуйте расписание мероприятий каждое утро. </pre> ",
                parse_mode="html")
            return

        caption = f"Отзыв от {message.from_user.username} {message.from_user.first_name} {message.from_user.last_name} \n"
        await bot.send_message(config.Support_chat_id, caption + message.text[7:])
        await message.reply(
            "Ваш отзыв получен. Спасибо за обратную связь. Отзыв не предполагает обратного ответа. ")
        return
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)
