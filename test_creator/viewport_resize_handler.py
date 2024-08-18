from typing import Callable, Any
import dearpygui.dearpygui as dpg


added_handlers: list[Callable[[], Any]] = []


def setup():
    dpg.set_viewport_resize_callback(resize_handler)


def add_handler(handler: Callable[[], Any]):
    added_handlers.append(handler)


def remove_handler(handler: Callable[[], Any]):
    added_handlers.remove(handler)


def resize_handler():
    for handler in added_handlers:
        handler()
