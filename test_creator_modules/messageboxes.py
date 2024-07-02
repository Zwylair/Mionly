import dearpygui.dearpygui as dpg


def spawn_warning(text: str):
    width, height = [300, 70]

    pos = (
        int(dpg.get_viewport_width() / 2 - width / 2),
        int(dpg.get_viewport_height() / 2 - height / 2)
    )

    with dpg.window(label='Warning', no_resize=True, pos=pos):
        dpg.add_text(default_value=text, color=(255, 190, 190))


def spawn_info(text: str):
    width, height = [300, 70]

    pos = (
        int(dpg.get_viewport_width() / 2 - width / 2),
        int(dpg.get_viewport_height() / 2 - height / 2)
    )

    with dpg.window(label='Info', no_resize=True, pos=pos):
        dpg.add_text(default_value=text, color=(190, 230, 255))

