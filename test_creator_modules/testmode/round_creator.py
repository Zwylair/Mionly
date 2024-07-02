import string
import random
import dearpygui.dearpygui as dpg
from test_creator_modules import classes
from test_creator_modules.messageboxes import spawn_warning

test_object: classes.Test | None = None


def gen_random_id():
    return ''.join([random.choice(string.hexdigits) for _ in range(9)])


def open_round_creator():
    from test_creator_modules.testmode import TestModeRound

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
        test_object=test_object,
        title='',
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

        if not new_answer:
            return

        if new_answer in round_object.answers:
            spawn_warning('Cannot add two identical answers!')
            return

        round_object.answers.append(new_answer)
        dpg.configure_item(f'{registry_prefix}_answer_combo', items=round_object.answers)
        dpg.configure_item(f'{registry_prefix}_correct_answer_combo', items=round_object.answers)
        dpg.set_value(f'{registry_prefix}_new_answer', '')

        if len(round_object.answers) == 1:
            dpg.set_value(f'{registry_prefix}_correct_answer', new_answer)

    def remove_answer():
        answer_to_remove = dpg.get_value(f'{registry_prefix}_remove_answer')

        if not answer_to_remove:
            return

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

        if len(round_object.answers) == 0:
            spawn_warning('You have not added any answers!')
            return

        try:
            correct_answer_index = round_object.answers.index(correct_answer)
        except ValueError:
            # will never happen. correct answer autosets with first added answer
            spawn_warning('You have not selected correct answer!')
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
        hide()

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

        dpg.add_input_text(hint='Round title', source=f'{registry_prefix}_title', width=350)
        dpg.add_input_text(source=f'{registry_prefix}_round_text', multiline=True, width=350, height=70)

        with dpg.group(horizontal=True):
            dpg.add_button(label='Add answer field', callback=insert_answer_field)
            dpg.add_text('only 1 answer field (___) allowed in this round', color=(140, 140, 140))

        dpg.add_separator()

        with dpg.group(horizontal=True):
            dpg.add_input_text(source=f'{registry_prefix}_new_answer', width=225)
            dpg.add_button(label='Add answer', callback=add_answer)

        with dpg.group(horizontal=True):
            dpg.add_combo(items=round_object.answers, tag=f'{registry_prefix}_answer_combo', source=f'{registry_prefix}_remove_answer', width=225)
            dpg.add_button(label='Remove answer', callback=remove_answer)

        with dpg.group(horizontal=True):
            dpg.add_text('Correct answer: ')
            dpg.add_combo(items=round_object.answers, tag=f'{registry_prefix}_correct_answer_combo', source=f'{registry_prefix}_correct_answer', width=125)

        with dpg.group(horizontal=True):
            dpg.add_text('Points per correct answer: ')
            dpg.add_input_float(source=f'{registry_prefix}_points_per_correct_answer', width=250, format='%.2f')

        dpg.add_separator()
        save_button = dpg.add_button(label='Save', callback=save)

        dpg.render_dearpygui_frame()

        dpg.configure_item(
            save_button,
            pos=[
                dpg.get_item_rect_size(round_creator_window)[0] - 8 - dpg.get_item_rect_size(save_button)[0],
                dpg.get_item_rect_size(round_creator_window)[1] - 8 - dpg.get_item_rect_size(save_button)[1]
            ]
        )
