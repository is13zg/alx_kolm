from db import Database
import config
from utils import utils

db = Database(config.BD_name)
MIN_mode = False

interaction_json, answer_json = utils.update_interaction_answer()
menu_names, answer_names = utils.get_menu_names(interaction_json)
