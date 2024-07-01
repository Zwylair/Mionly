import dearpygui.dearpygui as dpg
import DearPyGui_DragAndDrop as dpg_dnd


def drop_handler(filelist: list[str]):
    ...


def setup():
    with dpg.theme() as hover_drag_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Border, (0, 180, 255), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_PopupBg, (25, 50, 75), category=dpg.mvThemeCat_Core)

    pos = (int(dpg.get_viewport_width() / 5), int(dpg.get_viewport_height() / 5))
    with dpg.window(modal=True, show=False, no_title_bar=True, no_resize=True, width=300, height=170, pos=pos) as drop_window:
        dpg.add_text('Drop here!', color=(190, 230, 255))

    def drop(data, keys):
        dpg.configure_item(drop_window, show=False)
        dpg.bind_item_theme(drop_window, '')
        dpg_dnd.set_drop_effect()

        drop_handler(data)

    def drag_over(keys):
        if dpg.is_item_hovered(drop_window):
            dpg.bind_item_theme(drop_window, hover_drag_theme)
            dpg_dnd.set_drop_effect(dpg_dnd.DROPEFFECT.MOVE)
        else:
            dpg.bind_item_theme(drop_window, '')
            dpg_dnd.set_drop_effect()

    def drag_enter(data, keys):
        dpg.configure_item(drop_window, show=True)

    def drag_leave():
        dpg.configure_item(drop_window, show=False)
        dpg.bind_item_theme(drop_window, '')

    dpg_dnd.set_drop(drop)
    dpg_dnd.set_drag_over(drag_over)
    dpg_dnd.set_drag_enter(drag_enter)
    dpg_dnd.set_drag_leave(drag_leave)
