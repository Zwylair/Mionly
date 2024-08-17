import json
import string
import random
from typing import Callable
from dataclasses import dataclass
import dearpygui.dearpygui as dpg
from test_creator import classes, animator, messageboxes
from test_creator.cyrillic_support import decode_string
from test_creator.language import loc
from settings import *

logger = logging.getLogger(__name__)
logging.basicConfig(format=LOGGING_FORMAT)
logger.setLevel(LOGGING_LEVEL)


def gen_random_id():
    return ''.join([random.choice(string.hexdigits) for _ in range(9)])


@dataclass
class TestModeRound(classes.Round):
    registry_id: str
    test_object_getter: Callable[[], classes.Test]
    title: str
    round_text: str
    answers: list[str]
    correct_answer_index: int | None
    points_per_correct_answer: float

    def open_round_editor(self):
        logger.debug(f'[Registry ID: {self.registry_id}] Clicked "Edit" button. Opening editor.')
        from test_creator.modules.testmode.round_creator import open_round_creator
        open_round_creator(self)

    def preview(self, parent_item_tag: str | int):
        logger.debug(f'[Registry ID: {self.registry_id}] Setting up round preview.')

        with dpg.group(parent=parent_item_tag):
            test_object = self.test_object_getter()
            title_object = dpg.add_text(self.title)

            dpg.add_text(self.round_text)
            dpg.add_spacer(height=7)
            dpg.add_text(loc('testmode.rc.answers') + ', '.join(self.answers))
            correct_answer_object = dpg.add_text(loc('testmode.classes.correct_answer') + self.answers[self.correct_answer_index])
            dpg.add_spacer(height=7)
            last_object = dpg.add_text(
                default_value=loc('testmode.classes.points_for_correct_answer_hint').format(self.points_per_correct_answer),
                color=(210, 210, 210)
            )

            debug_text = dpg.add_text(default_value=f'[testmode] [{self.registry_id}]', color=(140, 140, 140))
            edit_button = dpg.add_button(label=loc('testmode.classes.edit'), callback=self.open_round_editor)
            remove_button = dpg.add_button(label=loc('testmode.classes.delete'), callback=self.show_remove_request)
            arrow_button_up = dpg.add_button(
                arrow=True, direction=dpg.mvDir_Up,
                callback=lambda: test_object.move_up_round_with_id(self.registry_id)
            )
            arrow_button_down = dpg.add_button(
                arrow=True, direction=dpg.mvDir_Down,
                callback=lambda: test_object.move_down_round_with_id(self.registry_id)
            )

            dpg.bind_item_font(title_object, 'nunito_titles')
            dpg.render_dearpygui_frame()

            last_object_pos = dpg.get_item_pos(last_object)
            last_object_size = dpg.get_item_rect_size(last_object)
            title_object_pos = dpg.get_item_pos(title_object)
            debug_text_size = dpg.get_item_rect_size(debug_text)
            edit_button_size = dpg.get_item_rect_size(edit_button)
            correct_answer_object_pos = dpg.get_item_pos(correct_answer_object)
            remove_button_size = dpg.get_item_rect_size(remove_button)

            dpg.configure_item(
                debug_text,
                pos=[dpg.get_viewport_width() - 37 - debug_text_size[0], last_object_pos[1] - last_object_size[1] * 1.5]
            )
            dpg.configure_item(
                edit_button,
                pos=[dpg.get_viewport_width() - 37 - edit_button_size[0] - remove_button_size[0] - 5, title_object_pos[1]]
            )

            dpg.bind_item_theme(remove_button, 'red_button_theme')
            dpg.configure_item(
                remove_button,
                pos=[dpg.get_viewport_width() - 37 - remove_button_size[0], title_object_pos[1]]
            )

            dpg.configure_item(
                correct_answer_object,
                pos=[correct_answer_object_pos[0], correct_answer_object_pos[1] - last_object_size[1] + 7]
            )

            dpg.render_dearpygui_frame()

            remove_button_pos = dpg.get_item_pos(remove_button)
            edit_button_pos = dpg.get_item_pos(edit_button)
            remove_button_size = dpg.get_item_rect_size(remove_button)
            arrow_button_size = dpg.get_item_rect_size(arrow_button_up)

            dpg.configure_item(
                arrow_button_up,
                pos=[
                    edit_button_pos[0] + edit_button_size[0] + 5 + remove_button_size[0] - arrow_button_size[0],
                    remove_button_pos[1] + 30 + 7
                ]
            )
            dpg.configure_item(
                arrow_button_down,
                pos=[
                    edit_button_pos[0] + edit_button_size[0] + 5 + remove_button_size[0] - arrow_button_size[0],
                    remove_button_pos[1] + 60 + 7 + 5
                ]
            )

        dpg.add_separator(parent=parent_item_tag)

    def dumps(self) -> str:
        """
        Exports this round into json object (used on saving test)

        Template:
            title: str
            round_text: str
            answers: dict['answer1': True|False, 'answer2': True|False]
            points_per_correct_answer: float = 1.0
        """
        logger.debug(f'[Registry ID: {self.registry_id}] Dumping round.')

        return json.dumps({
            'title': decode_string(self.title),
            'round_text': decode_string(self.round_text),
            'answers': {decode_string(answer): index == self.correct_answer_index for index, answer in enumerate(self.answers)},
            'points_per_correct_answer': self.points_per_correct_answer,
        })

    @staticmethod
    def loads(file_entry: str, test_object_getter: Callable[[], classes.Test]):
        """Loads round from json-like object (reversed dumps())

        Template:
            title: str
            round_text: str
            answers: dict['answer1': True|False, 'answer2': True|False]
            points_per_correct_answer: float = 1.0"""

        registry_id = gen_random_id()
        logger.debug(f'[Registry ID: {registry_id}] Loading round from file entry...')
        loaded_round: dict = json.loads(file_entry)
        round_object = TestModeRound(
            registry_id=registry_id,
            test_object_getter=test_object_getter,
            title=loaded_round.get('title'),
            round_text=loaded_round.get('round_text'),
            answers=list(loaded_round.get('answers').keys()),
            correct_answer_index=next(iter([index for index, is_correct in enumerate(loaded_round.get('answers').values()) if is_correct]), None),
            points_per_correct_answer=loaded_round.get('points_per_correct_answer'),
        )
        logger.debug(f'Loaded round data: {round_object}')
        return round_object

    def remove(self, remove_round_window: str | int):
        """Deletes this round from test"""
        logger.debug(f'[Registry ID: {self.registry_id}] Round was removed from test.')

        test_object = self.test_object_getter()
        this_round_in_test_object = test_object.get_round_with_id(self.registry_id)

        test_object.rounds.remove(this_round_in_test_object)
        test_object.regenerate_round_previews()
        animator.close_item(remove_round_window)

    def show_remove_request(self):
        logger.debug(f'[Registry ID: {self.registry_id}] Showed remove request.')

        messageboxes.spawn_yes_no_window(
            text=loc('testmode.classes.round_deletion_text'),
            yes_button_callback=lambda tag: self.remove(tag)
        )
