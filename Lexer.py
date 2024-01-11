from src.Regex import parse_regex

class Lexer:
    dfa_spec = {}
    spec = {}

    def __init__(self, spec: list[tuple[str, str]]) -> None:
        self.spec = spec
        self.dfa_spec = {}

        # Creating a DFA for each token
        for token_name, regex in spec:
            dfa = parse_regex(regex).thompson().subset_construction()
            self.dfa_spec[token_name] = dfa

    def lex(self, word: str) -> list[tuple[str, str]] | None:
        result = []
        matches = []

        line_number = 0
        char_index = 1
        initial_word_size = len(word)

        while word:
            for i in range(0, len(word) + 1):
                # Looking for all the tokens that match the current word.
                for token_name, dfa in self.dfa_spec.items():
                    # We do that for each prefix of the current word
                    # (increasing the prefix size each time by one)
                    if dfa.accept(word[:i]):
                        matches.append((token_name, word[:i]))


            if not matches:
                # We do this because we start counting from 1
                # and when the first char is not in the spec
                # it is supposed that it failed at the previous char.
                if not self.check_char_in_spec(word[0]):
                    char_index -= 1

                # Reached EOF without accepting any token.
                # (example: token: "(bc)+", words that end
                # with b reached EOF without accepting any token)
                if char_index >= initial_word_size:
                    char_index = -1 # Meaning EOF.
                return self.err_message(char_index, line_number)

            longest_match = self.get_longest_match(matches)
            result.append(longest_match)

            # Removing the longest match from the current word.
            word = word[len(longest_match[1]):]

            # Updating the line number and the char index.
            char_index += len(longest_match[1])
            nr_of_newlines = longest_match[1].count('\n')
            if nr_of_newlines > 0:
                line_number += nr_of_newlines
                # When we encounter a newline we reset the char index.
                initial_word_size -= char_index
                char_index = 1

            matches = []

        return result

    def err_message(self, char_index, line_nr):
        displayed_char_index_str = str(char_index)

        if char_index == -1:
            displayed_char_index_str = "EOF"

        if not line_nr:
            return [("", f"No viable alternative at character {displayed_char_index_str}, line 0")]
        else:
            return [
                ("", f"No viable alternative at character {displayed_char_index_str}, "
                    f"line {line_nr}")
            ]

        
    def check_char_in_spec(self, char: str) -> bool:
        return any(char in regex for (_, regex) in self.spec)

    def get_longest_match(self, matches: list[tuple[str, str]]) -> tuple[str, str]:
        longest_match = matches[0]
        for match in matches:
            if len(match[1]) > len(longest_match[1]):
                longest_match = match

        return longest_match
