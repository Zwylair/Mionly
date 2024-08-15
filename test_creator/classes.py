from dataclasses import dataclass
import dearpygui.dearpygui as dpg


class Round:
    test_creator_registry_id: str

    @staticmethod
    def init_empty():
        pass

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

    @staticmethod
    def init_empty():
        return Test([], '', {}, [])

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

    def find_round_with_id(self, round_id: str):
        return [i for i in self.rounds if i.test_creator_registry_id == round_id][0]

    def move_up_test_with_id(self, round_id: str):
        round_in_test_object = self.find_round_with_id(round_id)
        round_index = self.rounds.index(round_in_test_object)

        if round_index == 0:
            return

        self.rounds.insert(round_index - 1, round_in_test_object)
        self.rounds.pop(round_index + 1)
        self.update_round_list()

    def move_down_test_with_id(self, round_id: str):
        if not self.is_there_saved_round_with_id(round_id):
            return

        dummy = Round()
        round_in_test_object = self.find_round_with_id(round_id)
        round_index = self.rounds.index(round_in_test_object)
        self.rounds.append(dummy)

        try:
            self.rounds[round_index + 2]
        except IndexError:
            self.rounds.remove(dummy)
            return
        except ValueError:
            self.rounds.append(round_in_test_object)
            self.rounds.pop(round_index)
        else:
            self.rounds.insert(round_index + 2, round_in_test_object)
            self.rounds.pop(round_index)

        self.rounds.remove(dummy)
        self.update_round_list()
