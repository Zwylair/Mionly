from dataclasses import dataclass
import dearpygui.dearpygui as dpg


class Round:
    test_creator_registry_id: str

    def preview(self, parent_item_tag: str | int):
        pass

    def dump(self) -> str:
        pass


@dataclass
class Test:
    rounds: list[Round]
    dpg_window_for_round_previews: str | int
    hidden_round_creators: dict[str | int, str]  # dpg_tag: round_id
    restricted_parent_children_to_remove: list[str | int]

    def update_round_list(self):
        children = dpg.get_item_children(self.dpg_window_for_round_previews)[1]
        children = [i for i in children if i not in self.restricted_parent_children_to_remove]

        for child in children:
            dpg.delete_item(child)

        for test_round in self.rounds:
            test_round.preview(self.dpg_window_for_round_previews)

    def is_there_saved_round_with_id(self, round_id: str):
        """Leaves rounds with same id in list.
        if list not empty (len >= 1) bool would be True. False otherwise"""
        return bool([i for i in self.rounds if i.test_creator_registry_id == round_id])

    @staticmethod
    def show_hidden_round_creator(dpg_tag: str | int):
        if not dpg.is_item_shown(dpg_tag):
            dpg.show_item(dpg_tag)
