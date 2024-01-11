from .NFA import NFA

class Regex:
    def thompson(self) -> NFA[int]:
        raise NotImplementedError(
            'the thompson method of the Regex class should never be called')

class Character(Regex):
    __match_args__ = ("chr",)

    def __init__(self, character: str):
        self.chr = character
        self.symbols = set(character)

    def thompson(self) -> NFA[int]:
        # Thompson construction for characters or character ranges
        transitions = {(0, symbol): {1} for symbol in self.symbols}
        nfa = NFA(self.symbols, {0, 1}, 0, transitions, {1})
        return nfa

class Operator(Regex):
    __match_args__ = ("op",)

    def __init__(self, op: str, regex1: Regex = None, regex2: Regex = None):
        self.op = op
        self.regex1 = regex1
        self.regex2 = regex2

    def thompson(self) -> NFA[int]:
        raise NotImplementedError(
            'the thompson method of the Operator class should never be called')

    @staticmethod
    def priority(op: str) -> int:
        # Use a set for comparison
        if op in {'*', '+', '?'}:
            return 3
        elif op == "~":  # Concatenation. Used tilde instead of dot because dot appears in regexes.
            return 2
        elif op == "|":
            return 1
        return 0

class Concat(Regex):
    __match_args__ = ("regex1", "regex2")

    def __init__(self, regex1: Regex, regex2: Regex):
        self.regex1 = regex1
        self.regex2 = regex2

    def thompson(self) -> NFA[int]:
        nfa1 = self.regex1.thompson()
        nfa2 = self.regex2.thompson()

        # Remaping states for the second nfa in order to avoid conflicts.
        nfa2 = nfa2.remap_states(lambda x: x + max(nfa1.K) + 1)

        # Merge the NFAs by adding epsilon transitions from final
        # states of regex1 to the initial state of regex2.
        for state in nfa1.F:
            nfa1.d[(state, '')] = {nfa2.q0} | nfa1.d.get((state, ''), set())

        # Update final states.
        nfa1.F = nfa2.F

        # Merge states and transitions.
        nfa1.K.update(nfa2.K)
        nfa1.d.update(nfa2.d)

        # Add states to the alphabet.
        nfa1.S.update(nfa2.S)

        return nfa1

class Union(Regex):
    __match_args__ = ("regex1", "regex2")

    def __init__(self, regex1: Regex, regex2: Regex):
        self.regex1 = regex1
        self.regex2 = regex2
    def thompson(self) -> NFA[int]:
        nfa1 = self.regex1.thompson()
        nfa2 = self.regex2.thompson()

        new_initial_state = 0

        # Remap states of the nfas in order to avoid conflicts.
        nfa1 = nfa1.remap_states(lambda x: x + 1)
        remap_value_nfa2 = max(nfa1.K) + 1
        nfa2 = nfa2.remap_states(lambda x: x + remap_value_nfa2)
        
        # Build a new nfa that represents the union of nfa1 and nfa2.
        new_nfa = NFA(
            nfa1.S.union(nfa2.S),
            nfa1.K.union(nfa2.K).union({new_initial_state}),
            new_initial_state,
            {**nfa1.d, **nfa2.d},
            nfa1.F.union(nfa2.F)
        )

        # Add epsilon transitions from the new initial state
        # to the initial states of regex1 and regex2.
        new_nfa.d[(new_initial_state, '')] = {nfa1.q0, nfa2.q0}

        return new_nfa

class Star(Regex):
    __match_args__ = ("regex",)

    def __init__(self, regex: Regex):
        self.regex = regex

    def thompson(self) -> NFA[int]:
        nfa = self.regex.thompson()
        nfa = nfa.remap_states(lambda x: x + 1)

        old_initial_state = nfa.q0
        new_initial_state = 0

        nfa.K.add(new_initial_state)
        nfa.q0 = new_initial_state

        # Add epsilon transition from the final states to the old initial state.
        for state in nfa.F:
            nfa.d.setdefault((state, ''), set()).add(old_initial_state)

        # Final states from the received nfa are no longer final states.
        nfa.F = set()
        
        # Set the old initial state as the only final state.
        nfa.F.add(old_initial_state)

        # Add epsilon transition from the new initial state to the old initial state.
        nfa.d[(new_initial_state, '')] = {old_initial_state}

        return nfa


class Plus(Regex):
    __match_args__ = ("regex",)

    def __init__(self, regex: Regex):
        self.regex = regex

    def thompson(self) -> NFA[int]:
        # Implement Thompson construction for plus
        nfa = self.regex.thompson()

        # Add a new state for the loop
        old_initial_state = nfa.q0
        new_state = max(nfa.K) + 1
        nfa.K.add(new_state)

        # Add epsilon transition from the new state to the old initial state
        nfa.d[(new_state, '')] = {old_initial_state}

        # Add epsilon transition from the final states to the old initial state
        for state in nfa.F:
            nfa.d.setdefault((state, ''), set()).add(old_initial_state)

        # Add the new state to the set of final states
        nfa.F.add(new_state)

        return nfa
    
class Question(Regex):
    __match_args__ = ("regex",)

    def __init__(self, regex: Regex):
        self.regex = regex

    def thompson(self) -> NFA[int]:
        nfa = self.regex.thompson()
        # Adding the initial state to the set of final states.
        nfa.F.add(nfa.q0)

        return nfa
    
def isEscaped(regex: str, index: int) -> bool:
    if not index:
        return False
    else:
        return regex[index - 1] == '\\'
        
def isEscapedSpace(regex: str, index: int) -> bool:
    if not index:
        return False
    else:
        return regex[index - 1] == '\\' and regex[index] == ' '
    
def isEscapedOperator(regex: str, index: int) -> bool:
    if not index:
        return False
    else:
        return regex[index - 1] == '\\' and regex[index] in set("*|+?()")
    
# check if a character from a regex is situated inside a syntactic sugar
def isPartOfSyntacticSugar(regex: str, index: int) -> bool:
    if not index or len(regex) < 4:
        return False
    elif regex[index - 1] == '[' or \
        regex[index - 2] == '[' or \
        regex[index - 3] == '[' or \
        regex[index - 4] == '[':

        return True
    
    return False
    
def expand_syntactic_sugars(regex: str) -> str:
    regex = regex.replace("[a-z]", "(a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|y|z)")
    regex = regex.replace("[A-Z]", "(A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|Y|Z)")
    regex = regex.replace("[0-9]", "(0|1|2|3|4|5|6|7|8|9)")
    return regex

def add_concatenation_tilde(regex: list) -> str:
    special_chars = set("\n@-._/[]\\")
    high_priority_operators = set("*+?")
    new_regex = ""

    for i, char in enumerate(regex):
        is_alnum_or_special = (
            char.isalnum() or
            char in special_chars or
            char == '\\' or
            char == '(' or
            char == ":"
        )
        is_prev_alnum_or_special = (
            regex[i - 1].isalnum() or
            regex[i - 1] in special_chars or
            regex[i - 1] in high_priority_operators or
            regex[i - 2] == '\\' or
            regex[i - 1] == ')'
        )
        not_escaped = not isEscaped(regex, i)
        not_sugar = not isPartOfSyntacticSugar(regex, i)
        new_regex_not_empty = new_regex

        # should add points between every two valid chars(the valid chars are alphanumeric,
        # special chars and escaped chars)
        if (is_alnum_or_special and
            is_prev_alnum_or_special and
            not_escaped and
            not_sugar and
            new_regex_not_empty
        ):
            new_regex += '~'
            new_regex += char
        else:
            new_regex += char

    return new_regex
    
def handle_character(char, index, result_queue, regex):
    if (
        char in set("\n@-._/:")
        or char.isalnum()
        or isEscapedSpace(regex, index)
        or isEscapedOperator(regex, index)
    ):
        result_queue.append(Character(char))

def handle_opened_parenthesis(char, operator_stack):
    if char == '(':
        operator_stack.append(char)

def handle_closeed_parenthesis(char, operator_stack, result_queue):
    if char == ')':
        # Popping everything from the stack until the opening parenthesis is found.
        while operator_stack and operator_stack[-1] != '(':
            result_queue.append(Operator(operator_stack.pop()))
        operator_stack.pop()

def handle_question(char, result_queue):
    if char == '?':
        result_queue.append(Operator(char))

def handle_op(char, operator_stack, result_queue):
    if char in set("~*|+"):
        # Popping operators with higher priority from the stack.
        # The only exception is the opening parenthesis.
        while (
            operator_stack
            and operator_stack[-1] != '('
            and Operator.priority(operator_stack[-1]) >= Operator.priority(char)
        ):
            # Appending the popped operator to the result queue.
            result_queue.append(Operator(operator_stack.pop()))

        # Appending the current operator to the stack.
        operator_stack.append(char)

# Receives a list of regexes and returns a single regex of type Concat
def merge_regexes(regexes: list) -> Regex:
    merged_regex = regexes[0]

    for regex in regexes[1:]:
        merged_regex = Concat(merged_regex, regex)

    return merged_regex

def parse_regex(regex: str) -> Regex:
    result_queue = []
    operator_stack = []

    # Preprocess.
    regex = expand_syntactic_sugars(regex)
    regex = add_concatenation_tilde(regex)

    for index, char in enumerate(regex):
        handle_character(char, index, result_queue, regex)
        handle_question(char, result_queue)
        handle_opened_parenthesis(char, operator_stack)
        handle_closeed_parenthesis(char, operator_stack, result_queue)
        handle_op(char, operator_stack, result_queue)

    # Popping the remaining operators from the stack.
    while operator_stack:
        result_queue.append(Operator(operator_stack.pop()))

    operator_stack = []
    op_dict = {'*': Star, '+': Plus, '?': Question, '~': Concat, '|': Union}

    # Encapsulating the result queue into a single / few regexes.
    for token in result_queue:
        if isinstance(token, Character):
            operator_stack.append(token)
        # Each operator has a different number of operands. Some have 1, some have 2.
        elif isinstance(token, Operator) and token.op in op_dict:
            if token.op in {'~', '|'}:  # Operators with 2 operands.
                regex2, regex1 = operator_stack.pop(), operator_stack.pop()
                operator_stack.append(op_dict[token.op](regex1, regex2))
            else:  # Operators with 1 operand.
                operator_stack.append(op_dict[token.op](operator_stack.pop()))

    # Concat the remaining regexes.
    return merge_regexes(operator_stack)


    
