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


def show_item(dpg_tag: str | int):
    dpg.show_item(dpg_tag)
    animate.add('opacity', dpg_tag, 0, 1, [.57, .06, .61, .86], 10)
