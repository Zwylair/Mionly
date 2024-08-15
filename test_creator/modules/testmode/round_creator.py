import string
import random
from typing import Any
import dearpygui.dearpygui as dpg
from test_creator import classes
from test_creator.messageboxes import spawn_warning

test_object: classes.Test | None = None


def gen_random_id():
    return ''.join([random.choice(string.hexdigits) for _ in range(9)])


def delete_all_item_children(item_tag: str | int):
    children = dpg.get_item_children(item_tag)
    for list_with_children in children.values():
        for child in list_with_children:
            dpg.delete_item(child)


def open_round_creator(from_round: Any = None):
    from test_creator.modules.testmode import TestModeRound

    if from_round is None:
        # get not submitted rounds and show one of them
        unsaved_round_window = test_object.unsaved_rounds.get('testmode')

        if unsaved_round_window is not None:
            dpg.show_item(unsaved_round_window)
            return

        registry_id = gen_random_id()
        round_object = TestModeRound(
            registry_id=registry_id,
            test_object=test_object,
            title='Choose the correct answer:',
            round_text='A bee flies and has: ___.',
            answers=['wings', 'claws', 'meat'],
            correct_answer_index=0,
            points_per_correct_answer=1.0,
            dpg_window_creator_tag=None,
        )
    else:
        from_round: TestModeRound

        round_object = from_round
        registry_id = round_object.registry_id
    registry_prefix = f'testmode_{registry_id}'

    def insert_answer_field():
        round_text = dpg.get_value(f'{registry_prefix}_round_text')

        if '___' not in round_text:
            add = '___ ' if round_text.endswith(' ') else ' ___ '
            dpg.set_value(f'{registry_prefix}_round_text', round_text + add)

    def add_answer():
        new_answer = dpg.get_value(f'{registry_prefix}_new_answer')

        if not new_answer:
            return

        if new_answer in round_object.answers:
            spawn_warning('Cannot add two identical answers!')
            return

        round_object.answers.append(new_answer)
        new_answer_index = len(round_object.answers) - 1  # will be the latest in the list
        dpg.set_value(f'{registry_prefix}_new_answer', '')

        if len(round_object.answers) == 1:
            dpg.set_value(f'{registry_prefix}_correct_answer_index', new_answer_index)
        setup_window_interface()

    def change_answer(answer_index: int, new_answer_text: str):
        round_object.answers[answer_index] = new_answer_text

    def save():
        title = dpg.get_value(f'{registry_prefix}_title')
        round_text = dpg.get_value(f'{registry_prefix}_round_text')
        correct_answer = dpg.get_value(f'{registry_prefix}_correct_answer')
        points_per_correct_answer = dpg.get_value(f'{registry_prefix}_points_per_correct_answer')

        if len(round_object.answers) == 0:
            spawn_warning('You have not added any answers!')
            return

        round_object.title = title
        round_object.round_text = round_text
        round_object.correct_answer = correct_answer
        round_object.points_per_correct_answer = points_per_correct_answer
        round_object.dpg_window_creator_tag = round_creator_window

        # check if round already in test (user edits existing round) and refreshing it
        same_round = test_object.get_round_with_id(round_object.registry_id)
        test_object.add_round(round_object) if same_round is None else test_object.refresh_round(round_object)
        test_object.unsaved_rounds.pop('testmode') if test_object.unsaved_rounds.get('testmode') == round_creator_window else None
        test_object.regenerate_round_previews()
        close()

    def close():
        delete_all_item_children(f'{registry_prefix}_registry')
        dpg.delete_item(f'{registry_prefix}_registry')
        dpg.delete_item(round_creator_window)

    def hide():
        if from_round is not None:
            close()
            return

        test_object.unsaved_rounds['testmode'] = round_creator_window
        dpg.hide_item(round_creator_window)

    def setup_window_interface():
        delete_all_item_children(round_creator_window)

        with dpg.group(parent=round_creator_window):
            dpg.add_input_text(hint='Round title', source=f'{registry_prefix}_title', width=350)
            dpg.add_input_text(source=f'{registry_prefix}_round_text', multiline=True, width=350, height=70)

            with dpg.group(horizontal=True):
                dpg.add_button(label='Add field for answer', callback=insert_answer_field)
                dpg.add_text('only 1 field for answer (___) allowed in this round', color=(140, 140, 140))

            dpg.add_separator()

            # spawn answer items
            dpg.add_text('Answers:')

            for answer_index, answer_text in enumerate(round_object.answers):
                with dpg.group(horizontal=True):
                    marked_as_correct = answer_index == round_object.correct_answer_index

                    def create_input_callback(index):
                        return lambda _, new_text: change_answer(index, new_text)

                    def create_mark_button_callback(index):
                        def callback():
                            round_object.correct_answer_index = index
                            setup_window_interface()

                        return callback

                    def create_delete_button_callback(index):
                        def callback():
                            if index == round_object.correct_answer_index:
                                round_object.correct_answer_index = 0
                            round_object.answers.pop(index)
                            setup_window_interface()

                        return callback

                    dpg.add_input_text(
                        default_value=answer_text,
                        width=250,
                        callback=create_input_callback(answer_index)
                    )

                    dpg.add_button(
                        label='Marked as correct answer' if marked_as_correct else 'Mark as correct answer',
                        enabled=not marked_as_correct,
                        callback=create_mark_button_callback(answer_index)
                    )

                    remove_answer_button = dpg.add_button(label='X', callback=create_delete_button_callback(answer_index))
                    dpg.bind_item_theme(remove_answer_button, 'red_button_theme')

            with dpg.group(horizontal=True):
                dpg.add_input_text(source=f'{registry_prefix}_new_answer', width=250)
                dpg.add_button(label='Add', callback=add_answer)

            with dpg.group(horizontal=True):
                dpg.add_text('Correct answer reward points: ')
                dpg.add_input_float(source=f'{registry_prefix}_points_per_correct_answer', width=250, format='%.2f')

            dpg.add_separator()

            with dpg.group(horizontal=True):
                dpg.add_button(label='Save', callback=save)

    with dpg.value_registry(tag=f'{registry_prefix}_registry'):
        dpg.add_string_value(tag=f'{registry_prefix}_title', default_value=round_object.title)
        dpg.add_string_value(tag=f'{registry_prefix}_round_text', default_value=round_object.round_text)
        dpg.add_int_value(tag=f'{registry_prefix}_correct_answer_index', default_value=round_object.correct_answer_index)
        dpg.add_float_value(tag=f'{registry_prefix}_points_per_correct_answer', default_value=round_object.points_per_correct_answer)
        dpg.add_string_value(tag=f'{registry_prefix}_new_answer')
        dpg.add_string_value(tag=f'{registry_prefix}_remove_answer')

    window_size = (620, 370)
    viewport_size = (dpg.get_viewport_width(), dpg.get_viewport_height())

    with dpg.window(
            label='Add testmode round', on_close=hide,
            width=window_size[0], height=window_size[1],
            pos=[
                int(viewport_size[0] / 2 - window_size[0] / 2),
                int(viewport_size[1] / 2 - window_size[1] / 2 - 50)
            ]
    ) as round_creator_window:
        setup_window_interface()
