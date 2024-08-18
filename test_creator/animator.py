import time
import dearpygui.dearpygui as dpg
import dearpygui_animate as animate


def close_item(dpg_tag: str | int):
    dpg.show_item(dpg_tag)
    animate.add('opacity', dpg_tag, 1, 0, [.57, .06, .61, .86], 10)
    time.sleep(1)
    dpg.delete_item(dpg_tag)


def hide_item(dpg_tag: str | int):
    dpg.show_item(dpg_tag)
    animate.add('opacity', dpg_tag, 1, 0, [.57, .06, .61, .86], 10)
    time.sleep(1)
    dpg.hide_item(dpg_tag)
    animate.add('opacity', dpg_tag, 0, 1, [.57, .06, .61, .86], 1)


def show_item(dpg_tag: str | int, spawn_at_center: bool = True):
    dpg.show_item(dpg_tag)
    animate.add('opacity', dpg_tag, 0, 1, [.57, .06, .61, .86], 10)

    if spawn_at_center and dpg.get_item_pos(dpg_tag) == [0, 0]:
        dpg.render_dearpygui_frame()
        dpg.render_dearpygui_frame()
        dpg.set_item_pos(
            dpg_tag,
            pos=[
                int(dpg.get_viewport_width() / 2 - dpg.get_item_width(dpg_tag) / 2 - 9),
                int(dpg.get_viewport_height() / 2 - dpg.get_item_height(dpg_tag) / 2 - 50)
            ]
        )
