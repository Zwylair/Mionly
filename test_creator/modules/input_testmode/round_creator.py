import string
import random
from typing import Any, Callable
import dearpygui.dearpygui as dpg
from test_creator import classes, animator
from shared_funcs.messageboxes import spawn_warning
from shared_funcs.language import loc
from settings import *
import log

logger = logging.getLogger(__name__)
logging.basicConfig(level=LOGGING_LEVEL, handlers=log.get_handler_for_me())
test_object_getter: Callable[[], classes.Test] | None = None


def gen_random_id():
    return ''.join([random.choice(string.hexdigits) for _ in range(9)])


def delete_all_item_children(item_tag: str | int):
    logger.debug(f'Deleting all children from {item_tag}')

    children = dpg.get_item_children(item_tag)
    for list_with_children in children.values():
        for child in list_with_children:
            dpg.delete_item(child)


def open_round_creator(from_round: Any = None):
    from test_creator.modules.input_testmode import InputTestModeRound
    logger.debug('Opened creator')
    test_object = test_object_getter()

    if from_round is None:
        # get not submitted rounds and show one of them
        unsaved_round_window = test_object.unsaved_rounds.get('input_testmode')

        if unsaved_round_window is not None:
            logger.debug('There is not saved round. Showing creator window')
            animator.show_item(unsaved_round_window)
            return

        logger.debug('Setting up round template...')
        registry_id = gen_random_id()
        round_object = InputTestModeRound(
            registry_id=registry_id,
            test_object_getter=test_object_getter,
            title='Choose the correct answer:',
            round_text='A bee flies and has: ___.',
            answers=['wings'],
            points_per_correct_answer=1.0,
        )
    else:
        from_round: InputTestModeRound
        round_object = from_round
        registry_id = round_object.registry_id

        logger.debug(f'Editor opened with given round id: {registry_id}')
    registry_prefix = f'input_testmode_{registry_id}'

    logger.debug(f'Registry id for new round: {registry_id}')
    logger.debug('Initializing window...')

    def insert_answer_field():
        logger.debug('Inserted answer field')
        round_text = dpg.get_value(f'{registry_prefix}_round_text')
        add = '___ ' if round_text.endswith(' ') else ' ___ '
        dpg.set_value(f'{registry_prefix}_round_text', round_text + add)

    def add_answer():
        new_answer = dpg.get_value(f'{registry_prefix}_new_answer')

        if not new_answer:
            return

        if new_answer in round_object.answers:
            spawn_warning(loc('testmode.rc.repeating_answers'))
            return

        round_object.answers.append(new_answer)
        dpg.set_value(f'{registry_prefix}_new_answer', '')

        logger.debug(f'Added new answer: "{new_answer}"')
        setup_window_interface()

    def change_answer(answer_index: int, new_answer_text: str):
        round_object.answers[answer_index] = new_answer_text

    def save():
        logger.debug('Saving round to test object...')
        title = dpg.get_value(f'{registry_prefix}_title')
        round_text = dpg.get_value(f'{registry_prefix}_round_text')
        points_per_correct_answer = dpg.get_value(f'{registry_prefix}_points_per_correct_answer')
        answer_field_count = len(round_text.split('___')) - 1
        answers_count = len(round_object.answers)

        if len(round_object.answers) == 0:
            logger.debug('Nah, there are no answers')
            spawn_warning(loc('testmode.rc.empty_answers'))
            return

        if answers_count > answer_field_count:
            logger.debug('Nah, there are more answers that answer fields')
            spawn_warning(loc('input_testmode.rc.too_much_answers'))
            return

        if answer_field_count > answers_count:
            logger.debug('Nah, there are more answer fields than answers')
            spawn_warning(loc('input_testmode.rc.too_much_answer_fields'))
            return

        round_object.title = title
        round_object.round_text = round_text
        round_object.points_per_correct_answer = points_per_correct_answer

        # check if round already in test (user edits existing round) and refreshing it
        logger.debug('Checking if does the round already exists. And refresh if it does')

        same_round = test_object.get_round_with_id(round_object.registry_id)
        test_object.add_round(round_object) if same_round is None else test_object.refresh_round(round_object)
        test_object.unsaved_rounds.pop('input_testmode') if test_object.unsaved_rounds.get('input_testmode') == round_creator_window else None
        test_object.regenerate_round_previews()
        close()

    def close():
        logger.debug('Closing...')
        delete_all_item_children(f'{registry_prefix}_registry')
        dpg.delete_item(f'{registry_prefix}_registry')
        animator.close_item(round_creator_window)

    def hide():
        logger.debug('Hiding creator window.')
        if from_round is not None:
            logger.debug('Window was for editing round. Closing window.')
            close()
            return

        test_object.unsaved_rounds['input_testmode'] = round_creator_window
        animator.hide_item(round_creator_window)

    def setup_window_interface():
        logger.debug('Refreshing creator window interface')
        delete_all_item_children(round_creator_window)

        def create_input_callback(index: int):
            return lambda _, new_text: change_answer(index, new_text)

        def create_delete_button_callback(index: int):
            def callback():
                logger.debug(f'Delete "{round_object.answers[index]}" answer')
                round_object.answers.pop(index)
                setup_window_interface()

            return callback

        with dpg.group(parent=round_creator_window):
            dpg.add_input_text(hint=loc('testmode.rc.round_title'), source=f'{registry_prefix}_title', width=350)
            dpg.add_input_text(source=f'{registry_prefix}_round_text', width=350, height=70, multiline=True)
            dpg.add_button(label=loc('testmode.rc.add_answer_field'), callback=insert_answer_field)
            dpg.add_separator()

            dpg.add_text(loc('testmode.rc.answers'))

            for answer_index, answer in enumerate(round_object.answers):
                with dpg.group(horizontal=True):
                    dpg.add_input_text(
                        default_value=answer,
                        width=250,
                        callback=create_input_callback(answer_index)
                    )

                    remove_answer_button = dpg.add_button(label='X', callback=create_delete_button_callback(answer_index))
                dpg.bind_item_theme(remove_answer_button, 'red_button_theme')

            with dpg.group(horizontal=True):
                dpg.add_input_text(source=f'{registry_prefix}_new_answer', width=250)
                dpg.add_button(label=loc('testmode.rc.add'), callback=add_answer)

            dpg.add_text(loc('testmode.rc.points_for_correct_answer_hint'))
            dpg.add_input_float(source=f'{registry_prefix}_points_per_correct_answer', width=250, format='%.2f')
            dpg.add_separator()
            dpg.add_button(label=loc('creator.save'), callback=save)

    logger.debug('Setting up registry...')
    with dpg.value_registry(tag=f'{registry_prefix}_registry'):
        dpg.add_string_value(tag=f'{registry_prefix}_title', default_value=round_object.title)
        dpg.add_string_value(tag=f'{registry_prefix}_round_text', default_value=round_object.round_text)
        dpg.add_float_value(tag=f'{registry_prefix}_points_per_correct_answer', default_value=round_object.points_per_correct_answer)
        dpg.add_string_value(tag=f'{registry_prefix}_new_answer')

    with dpg.window(label=loc('input_testmode.__init__.add_round_button'), on_close=hide) as round_creator_window:
        setup_window_interface()
    animator.show_item(round_creator_window)
