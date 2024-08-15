import json
from typing import Callable
from dataclasses import dataclass
import dearpygui.dearpygui as dpg
from test_creator import classes
from cyrillic_support import decode_string


@dataclass
class TestModeRound(classes.Round):
    registry_id: str
    test_object_getter: Callable[[], classes.Test]
    title: str
    round_text: str
    answers: list[str]
    correct_answer_index: int | None
    points_per_correct_answer: float
    dpg_window_creator_tag: str | int | None

    def open_round_editor(self):
        from test_creator.modules.testmode.round_creator import open_round_creator
        open_round_creator(self)

    def preview(self, parent_item_tag: str | int):
        with dpg.group(parent=parent_item_tag):
            test_object = self.test_object_getter()
            title_object = dpg.add_text(self.title)

            dpg.add_text(self.round_text)
            dpg.add_spacer(height=7)
            dpg.add_text('answers: ' + ', '.join(self.answers))
            correct_answer_object = dpg.add_text('correct answer: ' + self.answers[self.correct_answer_index])
            dpg.add_spacer(height=7)
            last_object = dpg.add_text(
                default_value=f'[{self.points_per_correct_answer} points per correct answer]',
                color=(210, 210, 210)
            )

            debug_text = dpg.add_text(default_value=f'[testmode] [{self.registry_id}]', color=(140, 140, 140))
            edit_button = dpg.add_button(label='Edit', callback=self.open_round_editor)
            remove_button = dpg.add_button(label='Delete', callback=self.show_remove_request)
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
                pos=[correct_answer_object_pos[0], correct_answer_object_pos[1] - last_object_size[1] + 5]
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

    def dump(self) -> str:
        """
        Exports this round into json object (used on saving test)

        Template:
            title: str
            round_text: str
            answers: dict['answer1': True|False, 'answer2': True|False]
            points_per_correct_answer: float = 1.0
        """
        return json.dumps({
            'title': decode_string(self.title),
            'round_text': decode_string(self.round_text),
            'answers': {decode_string(answer): index == self.correct_answer_index for index, answer in enumerate(self.answers)},
            'points_per_correct_answer': self.points_per_correct_answer,
        })

    def remove(self, remove_round_window: str | int):
        """Deletes this round from test"""

        test_object = self.test_object_getter()
        this_round_in_test_object = test_object.get_round_with_id(self.registry_id)

        dpg.delete_item(remove_round_window)
        test_object.rounds.remove(this_round_in_test_object)
        test_object.regenerate_round_previews()

    def show_remove_request(self):
        width, height = (300, 120)

        pos = (
            int(dpg.get_viewport_width() / 2 - width / 2),
            int(dpg.get_viewport_height() / 2 - height / 2)
        )

        with dpg.window(label='Round deletion', no_resize=True, width=width, height=height, pos=pos) as remove_round_window:
            dpg.add_text(default_value='Are you sure to delete this round?')

            with dpg.group(horizontal=True):
                yes_button = dpg.add_button(label='Yes', callback=lambda: self.remove(remove_round_window))
                no_button = dpg.add_button(label='No', callback=lambda: dpg.delete_item(remove_round_window))
                dpg.bind_item_theme(yes_button, 'red_button_theme')
                dpg.bind_item_theme(no_button, 'green_button_theme')
