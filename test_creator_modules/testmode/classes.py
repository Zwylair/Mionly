import json
from dataclasses import dataclass
import dearpygui.dearpygui as dpg
from test_creator_modules import classes


@dataclass
class TestModeRound(classes.Round):
    test_creator_registry_id: str
    test_object: classes.Test
    title: str
    round_text: str
    answers: list[str]
    correct_answer_index: int | None
    points_per_correct_answer: float
    dpg_window_creator_tag: str | int | None

    @staticmethod
    def init_empty():
        return TestModeRound('', classes.Test.init_empty(), '', '', [], 0, 0, 0)

    def preview(self, parent_item_tag: str | int):
        with dpg.group(parent=parent_item_tag):
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

            debug_text = dpg.add_text(
                default_value=f'[testmode] [{self.test_creator_registry_id}]',
                color=(140, 140, 140)
            )
            edit_button = dpg.add_button(
                label='Edit',
                callback=lambda: self.test_object.show_hidden_round_creator(self.dpg_window_creator_tag)
            )
            remove_button = dpg.add_button(label='Delete', callback=self.show_remove_request)
            arrow_button_up = dpg.add_button(arrow=True, direction=dpg.mvDir_Up, callback=self.move_up_this_test)
            arrow_button_down = dpg.add_button(arrow=True, direction=dpg.mvDir_Down, callback=self.move_down_this_test)

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
        Template:
            title: str
            round_text: str
            answers: dict['answer1': ..., 'answer2': ...]
            points_per_correct_answer: float = 1.0
        """
        return json.dumps({
            'title': self.title,
            'round_text': self.round_text,
            'answers': {answer: answer == self.answers[self.correct_answer_index] for answer in self.answers},
            'points_per_correct_answer': self.points_per_correct_answer,
        })

    def remove(self, remove_round_window: str | int):
        this_round_in_test_object = self.test_object.find_round_with_id(self.test_creator_registry_id)
        reversed_round_creators = {v: k for k, v in self.test_object.hidden_round_creators.items()}
        dpg_round_creator_window = reversed_round_creators[self.test_creator_registry_id]

        dpg.delete_item(dpg_round_creator_window)
        dpg.delete_item(remove_round_window)
        self.test_object.rounds.remove(this_round_in_test_object)
        self.test_object.hidden_round_creators.pop(dpg_round_creator_window)
        self.test_object.update_round_list()

    def show_remove_request(self):
        width, height = (300, 120)

        pos = (
            int(dpg.get_viewport_width() / 2 - width / 2),
            int(dpg.get_viewport_height() / 2 - height / 2)
        )

        with dpg.window(label='Round deletion', no_resize=True, width=width, height=height, pos=pos) as remove_round_window:
            dpg.add_text(default_value='Are you sure to delete this round?')

            with dpg.group(horizontal=True):
                dpg.add_button(label='Yes', callback=lambda: self.remove(remove_round_window))
                dpg.add_button(label='No', callback=lambda: dpg.delete_item(remove_round_window))

    def move_up_this_test(self):
        if not self.test_object.is_there_saved_round_with_id(self.test_creator_registry_id):
            return

        round_in_test_object = self.test_object.find_round_with_id(self.test_creator_registry_id)
        round_index = self.test_object.rounds.index(round_in_test_object)

        if round_index == 0:
            return

        self.test_object.rounds.insert(round_index - 1, round_in_test_object)
        self.test_object.rounds.pop(round_index + 1)
        self.test_object.update_round_list()

    def move_down_this_test(self):
        if not self.test_object.is_there_saved_round_with_id(self.test_creator_registry_id):
            return

        dummy = TestModeRound.init_empty()
        round_in_test_object = self.test_object.find_round_with_id(self.test_creator_registry_id)
        round_index = self.test_object.rounds.index(round_in_test_object)
        self.test_object.rounds.append(dummy)

        try:
            self.test_object.rounds[round_index + 2]
        except IndexError:
            self.test_object.rounds.remove(dummy)
            return
        except ValueError:
            self.test_object.rounds.append(round_in_test_object)
            self.test_object.rounds.pop(round_index)
        else:
            self.test_object.rounds.insert(round_index + 2, round_in_test_object)
            self.test_object.rounds.pop(round_index)

        self.test_object.rounds.remove(dummy)
        self.test_object.update_round_list()
