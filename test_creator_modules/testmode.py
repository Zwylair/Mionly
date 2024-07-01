import json
import string
import random
from dataclasses import dataclass
import dearpygui.dearpygui as dpg
from test_creator_modules import classes

test_object: classes.Test | None = None


def setup(test_obj: classes.Test):
    global test_object
    test_object = test_obj

    spawn_round_creator_button()


def spawn_round_creator_button():
    dpg.add_button(label='Add testmode round', callback=open_round_creator)


@dataclass
class TestModeRound(classes.Round):
    test_creator_registry_id: str
    title: str
    round_text: str
    answers: list[str]
    correct_answer_index: int | None
    points_per_correct_answer: float
    dpg_window_creator_tag: str | int | None

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
                callback=lambda: test_object.show_hidden_round_creator(self.dpg_window_creator_tag)
            )

            dpg.render_dearpygui_frame()
            last_object_pos = dpg.get_item_pos(last_object)
            last_object_size = dpg.get_item_rect_size(last_object)
            title_object_pos = dpg.get_item_pos(title_object)
            debug_text_size = dpg.get_item_rect_size(debug_text)
            edit_button_size = dpg.get_item_rect_size(edit_button)
            correct_answer_object_pos = dpg.get_item_pos(correct_answer_object)

            dpg.configure_item(
                debug_text,
                pos=[dpg.get_viewport_width() - 20 - debug_text_size[0], last_object_pos[1] - 22]
            )
            dpg.configure_item(
                edit_button,
                pos=[dpg.get_viewport_width() - 20 - edit_button_size[0], title_object_pos[1]]
            )

            dpg.configure_item(
                correct_answer_object,
                pos=[correct_answer_object_pos[0], correct_answer_object_pos[1] - (last_object_size[1] / 2)]
            )

            dpg.render_dearpygui_frame()

        dpg.add_separator(parent=parent_item_tag)
        dpg.bind_item_font(title_object, 'nunito_titles')

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


def gen_random_id():
    return ''.join([random.choice(string.hexdigits) for _ in range(9)])


def open_round_creator():
    # get not submitted rounds and show one of them
    for dpg_window_tag, round_id in test_object.hidden_round_creators.items():
        if not test_object.is_there_saved_round_with_id(round_id):
            dpg.show_item(dpg_window_tag)
            return

    # opening multiple round creators causes conflicts in the registry. using id avoids this
    registry_id = gen_random_id()
    registry_prefix = f'testmode_{registry_id}'

    round_object = TestModeRound(
        test_creator_registry_id=registry_id,
        title='Choose the correct answer:',
        round_text='',
        answers=[],
        correct_answer_index=None,
        points_per_correct_answer=1.0,
        dpg_window_creator_tag=None,
    )

    def insert_answer_field():
        round_text = dpg.get_value(f'{registry_prefix}_round_text')

        if '___' not in round_text:
            add = '___ ' if round_text.endswith(' ') else ' ___ '
            dpg.set_value(f'{registry_prefix}_round_text', round_text + add)

    def add_answer():
        new_answer = dpg.get_value(f'{registry_prefix}_new_answer')

        if new_answer in round_object.answers:
            return

        round_object.answers.append(new_answer)
        dpg.configure_item(f'{registry_prefix}_answer_combo', items=round_object.answers)
        dpg.configure_item(f'{registry_prefix}_correct_answer_combo', items=round_object.answers)
        dpg.set_value(f'{registry_prefix}_new_answer', '')

        if len(round_object.answers) == 1:
            dpg.set_value(f'{registry_prefix}_correct_answer', new_answer)

    def remove_answer():
        answer_to_remove = dpg.get_value(f'{registry_prefix}_remove_answer')
        round_object.answers.remove(answer_to_remove)
        dpg.configure_item(f'{registry_prefix}_answer_combo', items=round_object.answers)
        dpg.configure_item(f'{registry_prefix}_correct_answer_combo', items=round_object.answers)
        dpg.set_value(f'{registry_prefix}_remove_answer', '')

        if len(round_object.answers) == 1:
            dpg.set_value(f'{registry_prefix}_correct_answer', round_object.answers[0])

        elif len(round_object.answers) == 0:
            dpg.set_value(f'{registry_prefix}_correct_answer', '')

        elif answer_to_remove == dpg.get_value(f'{registry_prefix}_correct_answer'):
            dpg.set_value(f'{registry_prefix}_correct_answer', round_object.answers[0])

    def save():
        title = dpg.get_value(f'{registry_prefix}_title')
        round_text = dpg.get_value(f'{registry_prefix}_round_text')
        correct_answer = dpg.get_value(f'{registry_prefix}_correct_answer')

        try:
            correct_answer_index = round_object.answers.index(correct_answer)
        except ValueError:
            return

        points_per_correct_answer = dpg.get_value(f'{registry_prefix}_points_per_correct_answer')

        round_object.title = title
        round_object.round_text = round_text
        round_object.correct_answer_index = correct_answer_index
        round_object.points_per_correct_answer = points_per_correct_answer
        round_object.dpg_window_creator_tag = round_creator_window

        # check if round already in test (user edits existing round)
        same_round = [i for i in test_object.rounds if i.test_creator_registry_id == round_object.test_creator_registry_id]
        if not same_round:
            test_object.rounds.append(round_object)
        else:
            same_round_index = test_object.rounds.index(same_round[0])
            test_object.rounds[same_round_index] = round_object
        test_object.update_round_list()

    def hide():
        test_object.hidden_round_creators[round_creator_window] = round_object.test_creator_registry_id
        dpg.hide_item(round_creator_window)

    with dpg.value_registry():
        dpg.add_string_value(tag=f'{registry_prefix}_title', default_value='Choose the correct answer:')
        dpg.add_string_value(tag=f'{registry_prefix}_round_text', default_value='A bee flies and has: ___.')
        dpg.add_string_value(tag=f'{registry_prefix}_correct_answer', default_value='wings')
        dpg.add_float_value(tag=f'{registry_prefix}_points_per_correct_answer', default_value=round_object.points_per_correct_answer)
        dpg.add_string_value(tag=f'{registry_prefix}_new_answer')
        dpg.add_string_value(tag=f'{registry_prefix}_remove_answer')
        round_object.answers = ['wings', 'claws', 'meat']

    with dpg.window(label='Testmode', no_title_bar=True, width=420, height=300) as round_creator_window:
        dpg.add_input_text(hint='Round title', source=f'{registry_prefix}_title', width=250)
        dpg.add_input_text(source=f'{registry_prefix}_round_text', multiline=True, width=250, height=50)

        with dpg.group(horizontal=True):
            dpg.add_button(label='Add answer field', callback=insert_answer_field)
            dpg.add_text('only 1 answer field allowed in this round', color=(140, 140, 140))

        dpg.add_separator()

        with dpg.group(horizontal=True):
            dpg.add_input_text(source=f'{registry_prefix}_new_answer', width=125)
            dpg.add_button(label='Add answer', callback=add_answer)

        with dpg.group(horizontal=True):
            dpg.add_combo(items=round_object.answers, tag=f'{registry_prefix}_answer_combo', source=f'{registry_prefix}_remove_answer', width=125)
            dpg.add_button(label='Remove answer', callback=remove_answer)

        with dpg.group(horizontal=True):
            dpg.add_text('Correct answer: ')
            dpg.add_combo(items=round_object.answers, tag=f'{registry_prefix}_correct_answer_combo', source=f'{registry_prefix}_correct_answer', width=125)

        with dpg.group(horizontal=True):
            dpg.add_text('Points per correct answer: ')
            dpg.add_input_float(source=f'{registry_prefix}_points_per_correct_answer', width=150, format='%.2f')

        dpg.add_separator()

        save_button = dpg.add_button(label='Save', callback=save)
        close_button = dpg.add_button(label='X', tag=f'{registry_prefix}_close_button', callback=hide)

        dpg.render_dearpygui_frame()

        dpg.configure_item(
            save_button,
            pos=[
                dpg.get_item_rect_size(round_creator_window)[0] - 8 - dpg.get_item_rect_size(save_button)[0],
                dpg.get_item_rect_size(round_creator_window)[1] - 8 - dpg.get_item_rect_size(save_button)[1]
            ]
        )

        dpg.configure_item(
            close_button,
            pos=[dpg.get_item_rect_size(round_creator_window)[0] - 8 - dpg.get_item_rect_size(close_button)[0], 7]
        )
