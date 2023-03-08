from transitions import Machine
from mathtext_fastapi.curriculum_mapper import build_curriculum_logic

all_states, all_transitions = build_curriculum_logic()

class GlobalStateManager(object):
    states = all_states

    transitions = all_transitions

    def __init__(
        self,
        initial_state='N1.1.1_G1',
    ):
        self.machine = Machine(
            model=self,
            states=GlobalStateManager.states,
            transitions=GlobalStateManager.transitions,
            initial=initial_state
        )
