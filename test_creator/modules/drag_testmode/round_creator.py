import string
import random
from typing import Any, Callable
import dearpygui.dearpygui as dpg
from test_creator import classes, animator
from test_creator.messageboxes import spawn_warning
from test_creator.language import loc
from settings import *

logger = logging.getLogger(__name__)
logging.basicConfig(format=LOGGING_FORMAT)
logger.setLevel(LOGGING_LEVEL)
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
    from test_creator.modules.drag_testmode import DragTestModeRound, Answer
    logger.debug('Opened creator')
    test_object = test_object_getter()

    if from_round is None:
        # get not submitted rounds and show one of them
        unsaved_round_window = test_object.unsaved_rounds.get('drag_testmode')

        if unsaved_round_window is not None:
            logger.debug('There is not saved round. Showing creator window')
            animator.show_item(unsaved_round_window)
            return

        logger.debug('Setting up round template...')
        registry_id = gen_random_id()
        round_object = DragTestModeRound(
            registry_id=registry_id,
            test_object_getter=test_object_getter,
            title='Choose the correct answer:',
            round_text='A bee flies and has: ___.',
            answers=[Answer('wings', 1), Answer('claws', None), Answer('meat', None)],
            points_per_correct_answer=1.0,
        )
    else:
        from_round: DragTestModeRound
        round_object = from_round
        registry_id = round_object.registry_id

        logger.debug(f'Editor opened with given round id: {registry_id}')
    registry_prefix = f'testmode_{registry_id}'

    logger.debug(f'Registry id for new round: {registry_id}')
    logger.debug('Initializing window...')

    def insert_answer_field():
        logger.debug('Inserted answer field')
        round_text = dpg.get_value(f'{registry_prefix}_round_text')
        add = '___ ' if round_text.endswith(' ') else ' ___ '
        dpg.set_value(f'{registry_prefix}_round_text', round_text + add)

    def sort_answers():
        # sort answers by position
        round_object.answers = sorted(
            round_object.answers,
            key=lambda _answer: (_answer.position is None, _answer.position)
        )

    def add_answer():
        new_answer = dpg.get_value(f'{registry_prefix}_new_answer')

        if not new_answer:
            return

        if new_answer in [i.text for i in round_object.answers]:
            spawn_warning(loc('testmode.rc.repeating_answers'))
            return

        round_object.answers.append(Answer(new_answer, None))
        dpg.set_value(f'{registry_prefix}_new_answer', '')

        logger.debug(f'Added new answer: "{new_answer}"')
        sort_answers()
        setup_window_interface()

    def change_answer(answer_index: int, new_answer_text: str):
        round_object.answers[answer_index].text = new_answer_text

    def save():
        logger.debug('Saving round to test object...')
        title = dpg.get_value(f'{registry_prefix}_title')
        round_text = dpg.get_value(f'{registry_prefix}_round_text')
        points_per_correct_answer = dpg.get_value(f'{registry_prefix}_points_per_correct_answer')
        answer_field_count = len(round_text.split('___')) - 1
        answers_marked_as_correct_count = len([answer for answer in round_object.answers if answer.position is not None])
        all_answer_positions = list(range(1, len(round_object.answers) + 1))
        valid_answers = 0

        for answer in round_object.answers:
            if answer.position in all_answer_positions:
                valid_answers += 1

        if len(round_object.answers) == 0:
            logger.debug('Nah, there are no answers')
            spawn_warning(loc('testmode.rc.empty_answers'))
            return

        if answer_field_count > valid_answers:
            logger.debug('Nah, there are more answer fields than valid answers')
            spawn_warning(loc('drag_testmode.rc.too_much_answer_fields2'))
            return

        if valid_answers > answer_field_count:
            logger.debug('Nah, there are more valid answers than answer fields')
            spawn_warning(loc('drag_testmode.rc.too_much_correct_answers2'))
            return

        if answers_marked_as_correct_count > answer_field_count:
            logger.debug('Nah, there are more "correct" answers that answer fields')
            spawn_warning(loc('drag_testmode.rc.too_much_correct_answers'))
            return

        if answer_field_count > answers_marked_as_correct_count:
            logger.debug('Nah, there are more answer fields than "correct" answers')
            spawn_warning(loc('drag_testmode.rc.too_much_answer_fields'))
            return

        round_object.title = title
        round_object.round_text = round_text
        round_object.points_per_correct_answer = points_per_correct_answer

        # check if round already in test (user edits existing round) and refreshing it
        logger.debug('Checking if does the round already exists. And refresh if it does')

        same_round = test_object.get_round_with_id(round_object.registry_id)
        test_object.add_round(round_object) if same_round is None else test_object.refresh_round(round_object)
        test_object.unsaved_rounds.pop('drag_testmode') if test_object.unsaved_rounds.get('drag_testmode') == round_creator_window else None
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

        test_object.unsaved_rounds['testmode'] = round_creator_window
        animator.hide_item(round_creator_window)

    def setup_window_interface():
        logger.debug('Refreshing creator window interface')
        delete_all_item_children(round_creator_window)

        with dpg.group(parent=round_creator_window):
            dpg.add_input_text(hint=loc('testmode.rc.round_title'), source=f'{registry_prefix}_title', width=350)
            dpg.add_input_text(source=f'{registry_prefix}_round_text', width=350, height=70, multiline=True)
            dpg.add_button(label=loc('testmode.rc.add_answer_field'), callback=insert_answer_field)
            dpg.add_separator()

            # answer.position == int (!0)  :: MARKED AS CORRECT AND HAS CERTAIN POSITION
            # answer.position == 0         :: MARKED AS CORRECT, BUT THE POSITION IS NOT SET ("" element in combo)
            # answer.position == None      :: NOT MARKED AS CORRECT

            # spawn answer items
            dpg.add_text(loc('testmode.rc.answers'))
            answers_len = len(round_object.answers)
            all_answer_positions = list(range(1, answers_len + 1))

            for answer_index, answer in enumerate(round_object.answers):
                marked_as_correct = answer.position is not None

                # fucking PYTHON's lambda.
                # i can't just do something like:
                #
                #
                # for answer in round_object.answers:
                #     with dpg.group(horizontal=True):
                #         dpg.add_input_text(..., callback=lambda _, new_text: change_answer(index, new_text))
                #         dpg.add_button(..., callback=lambda: mark_callback(answer_index))
                #         dpg.add_button(..., callback=lambda: delete_answer(answer_index))
                #
                #     if marked_as_correct:
                #         ...
                #
                #
                # why?
                # because PYTHON bakes lambda with an answer_index LINK. so, when lambda is
                # called, it will do things only FOR CURRENT answer_index value, which equals
                # last index of the answers list when the for cycle ends. this is the reason
                # of this large trash-looking code, but there is no another way to avoid this.
                #
                # P.S.: i have tried copy.deepcopy() thing, but there is something you should know:
                #       PYTHON's optimization gives all variables that contains -5 to 255 ints links
                #       to them because of their overuse. it means, if i had executed
                #       `my_ten_percent_unlinked_int = copy.deepcopy(12)` my variable is still linked.
                #       Here is more info about it:
                #       https://www.codesansar.com/python-programming/integer-interning.htm

                def create_input_callback(index: int):
                    return lambda _, new_text: change_answer(index, new_text)

                def create_mark_button_callback(index: int):
                    def mark_callback():
                        logger.debug(f'Marked "{round_object.answers[index]}" as correct')
                        round_object.answers[index].position = 0
                        sort_answers()
                        setup_window_interface()

                    def unmark_callback():
                        logger.debug(f'Unmarked "{round_object.answers[index]}" as correct')
                        round_object.answers[index].position = None
                        sort_answers()
                        setup_window_interface()

                    return unmark_callback if marked_as_correct else mark_callback

                def create_delete_button_callback(index: int):
                    def callback():
                        logger.debug(f'Delete "{round_object.answers[index]}" answer')
                        if index == round_object.correct_answer_index:
                            round_object.correct_answer_index = 0
                        round_object.answers.pop(index)
                        setup_window_interface()

                    return callback

                def create_change_position_callback(index: int):
                    def callback():
                        changing_answer = round_object.answers[index]
                        new_position = dpg.get_value(f'{registry_prefix}_answer_{changing_answer.text}_pos_combo')
                        new_position = int(new_position) if new_position else None

                        logger.debug(f'Changing "{round_object.answers[index]}" answer position')

                        if new_position is None:
                            round_object.answers[index].position = None
                            return

                        # set '' position for exist answer
                        for round_answer in round_object.answers:
                            if round_answer.position == new_position:
                                round_answer.position = 0
                                break

                        changing_answer.position = new_position
                        sort_answers()

                        setup_window_interface()
                    return callback

                # this group made for spacing between "edit answer elements", "edit answer pos elements" and remove button
                with dpg.group(horizontal=True, horizontal_spacing=23):
                    with dpg.group(horizontal=True):
                        # edit answer elements
                        dpg.add_input_text(
                            default_value=answer.text,
                            width=250,
                            callback=create_input_callback(answer_index)
                        )

                        dpg.add_button(
                            label=loc('drag_testmode.rc.unmark_as_correct' if marked_as_correct else 'testmode.rc.mark_as_correct'),
                            callback=create_mark_button_callback(answer_index)
                        )

                    # edit answer pos elements
                    if marked_as_correct:
                        with dpg.group(horizontal=True):
                            dpg.add_text(loc('drag_testmode.rc.answer_pos_label'))
                            dpg.add_combo(
                                items=[''] + [str(pos) for pos in all_answer_positions],
                                default_value='' if answer.position == 0 or answer.position is None else str(answer.position),
                                width=70,
                                tag=f'{registry_prefix}_answer_{answer.text}_pos_combo',
                                callback=create_change_position_callback(answer_index)
                            )

                    # just remove answer button
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

    with dpg.window(label=loc('testmode.rc.add_round'), on_close=hide) as round_creator_window:
        setup_window_interface()
    animator.show_item(round_creator_window)
