from aiogram.fsm.state import StatesGroup, State

class WaitReview(StatesGroup):
    GET_REVIEW_PHOTO = State()