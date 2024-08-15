from dataclasses import dataclass, field
import dearpygui.dearpygui as dpg


class Round:
    registry_id: str

    @staticmethod
    def init_empty():
        pass

    def preview(self, parent_item_tag: str | int):
        pass

    def dump(self) -> str:
        pass


@dataclass
class Test:
    rounds: list[Round] = field(default_factory=lambda: [])
    dpg_window_for_round_previews: str | int = field(default_factory=lambda: 0)
    restricted_parent_children_to_remove: list[str | int] = field(default_factory=lambda: [])
    unsaved_rounds: dict[str, str | int] = field(default_factory=lambda: {})  # creator_tag: dpg_tag

    def regenerate_round_previews(self):
        children = dpg.get_item_children(self.dpg_window_for_round_previews)[1]
        children = [i for i in children if i not in self.restricted_parent_children_to_remove]

        for child in children:
            dpg.delete_item(child)

        for test_round in self.rounds:
            test_round.preview(self.dpg_window_for_round_previews)

    def get_round_with_id(self, round_id: str) -> Round | None:
        return next(iter([i for i in self.rounds if i.registry_id == round_id]), None)

    def add_round(self, round_object: Round):
        self.rounds.append(round_object)

    def refresh_round(self, round_object: Round):
        same_round = self.get_round_with_id(round_object.registry_id)
        if same_round is None:
            self.add_round(round_object)
            return

        same_round_index = self.rounds.index(same_round)
        self.rounds[same_round_index] = round_object

    def move_up_round_with_id(self, round_id: str):
        round_in_test_object = self.get_round_with_id(round_id)
        round_index = self.rounds.index(round_in_test_object)

        if round_index == 0:
            return

        self.rounds.insert(round_index - 1, round_in_test_object)
        self.rounds.pop(round_index + 1)
        self.regenerate_round_previews()

    def move_down_round_with_id(self, round_id: str):
        dummy = Round()
        round_in_test_object = self.get_round_with_id(round_id)
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
        self.regenerate_round_previews()
