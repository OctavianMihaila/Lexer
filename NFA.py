from .DFA import DFA

from dataclasses import dataclass
from collections.abc import Callable
from collections import deque

EPSILON = ''  # this is how epsilon is represented by the checker in the transition function of NFAs


@dataclass
class NFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], set[STATE]]
    F: set[STATE]

    def compute_epsilon_closure(self, state: STATE,
                                 epsilon_closure_result: set[STATE],
                                   visited_states: set[STATE]) -> None:
        visited_states.add(state)
        epsilon_closure_result.add(state)

        # Those are the states reachable from the current state on epsilon transitions.
        epsilon_transition_states = self.d.get((state, EPSILON), set())

        # Getting epsilon closure of each state reachable
        #from the current state on epsilon transitions.
        unvisited_states = [s for s in epsilon_transition_states if s not in visited_states]
        for s in unvisited_states:
            self.compute_epsilon_closure(s, epsilon_closure_result, visited_states)

    def epsilon_closure(self, state: STATE) -> set[STATE]:
        epsilon_closure_result = set()
        visited_states = set()

        self.compute_epsilon_closure(state, epsilon_closure_result, visited_states)

        return epsilon_closure_result
    

    def compute_next_states_epsilon_closure(self, current_state, symbol):
        # Get all the states that can be reached from the current state on the given symbol.
        next_states = set().union(*(self.d.get((state, symbol), set()) for state in current_state))
        # Compute the epsilon closure of all the states
        # that can be reached from the current state on the given symbol.
        # * is used to unpack the set of sets into a single set (iterable).
        # Union is used to merge all the sets into a single set(with no duplicates).
        next_states_epsilon_closure = set().union(*(self.epsilon_closure(state)
                                                     for state in next_states))

        return next_states_epsilon_closure

    def add_new_state_to_dfa(self, new_state, dfa_states, queue):
        if new_state not in dfa_states:
            dfa_states.add(new_state)
            queue.append(new_state)

    def process_symbol_transition(self, current_state, symbol, dfa_states, queue, dfa_transitions):
        next_states_epsilon_closure = self.compute_next_states_epsilon_closure(current_state,
                                                                                symbol)

        new_state = frozenset(next_states_epsilon_closure)
        self.add_new_state_to_dfa(new_state, dfa_states, queue)

        dfa_transitions[(current_state, symbol)] = new_state

    def subset_construction(self) -> 'DFA':
        start_state = frozenset(self.epsilon_closure(self.q0))
        dfa_states = {start_state}
        dfa_transitions = {}
        dfa_final_states = set()

        # Used to hold the states that are yet to be processed.
        queue = deque([start_state])

        while queue:
            current_state = queue.popleft()

            # Check if the current state is a final state.
            for state in self.F:
                if state in current_state:
                    dfa_final_states.add(current_state)
                    break

            # Get all the symbols that can be used to transition from the current state
            symbols = {symbol for state, symbol in self.d.keys() if state in current_state}
            symbols.discard(EPSILON) # Remove '' from the set of symbols. Not needed for now.

            # Perform the transition for each symbol that can be
            # used to transition from the current state.
            for symbol in symbols:
                self.process_symbol_transition(current_state, symbol,
                                                dfa_states, queue, dfa_transitions)
                
        # Add the epsilon transition back to the DFA.
        dfa_states.add(frozenset(EPSILON))

        # Add the missing transitions to the DFA.
        for state in dfa_states:
            for symbol in self.S:
                if (state, symbol) not in dfa_transitions:
                    dfa_transitions[(state, symbol)] = frozenset(EPSILON)

        return DFA(self.S, dfa_states, start_state, dfa_transitions, dfa_final_states)

    def remap_states[OTHER_STATE](self, f: Callable[[STATE], OTHER_STATE]) -> 'NFA[OTHER_STATE]':
        new_states = {state: f(state) for state in self.K}
        new_q0 = f(self.q0)
        new_F = {f(state) for state in self.F}
        new_d = {(f(state), symbol): {f(next_state) for next_state in next_states}
                    for (state, symbol), next_states in self.d.items()}

        return NFA(
                S=self.S,
                K=set(new_states.values()),
                q0=new_q0,
                d=new_d,
                F=new_F)