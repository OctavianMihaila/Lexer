from collections.abc import Callable
from dataclasses import dataclass
import functools


@dataclass
class DFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], STATE]
    F: set[STATE]


    def accept(self, word: str) -> bool:
        transitions = self.d

        def update_state(state, symbol): # Moving to the next state.
            return transitions.get((state, symbol), None)
        
        # Reducing the word to a single state. (functools.reduce is kind of a foldl in python).
        final_state = functools.reduce(update_state, word, self.q0)

        return final_state is not None and final_state in self.F

    def remap_states[OTHER_STATE](self, f: Callable[[STATE], 'OTHER_STATE']) -> 'DFA[OTHER_STATE]':
        # Appling the function f to each state of the DFA.
        new_S = {state: f(state) for state in self.K}
        states = new_S.values()
        new_q0 = f(self.q0)
        new_F = {f(state) for state in self.F}
        new_d = {(f(src), symbol): f(dest) for (src, symbol), dest in self.d.items()}

        return DFA(
            S=self.S,
            K=set(states),
            q0=new_q0,
            d=new_d,
            F=new_F
        )