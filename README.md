# Lexer Implementation in Python

## Overview

This Python project involves building a lexer, a program that breaks down a string into tokens based on a provided specification. The implementation spans multiple stages, including the conversion of Non-Deterministic Finite Automata (NFA) to Deterministic Finite Automata (DFA) and the transformation of Regular Expressions (Regex) to NFAs using the Thompson Algorithm.

## Project Structure

The project skeleton consists of several classes:

1. **DFA (Deterministic Finite Automaton)**
   - Represents a DFA with fields for alphabet, states, initial state, transition function, and final states.
   - Methods include `accept` for word acceptance and an optional `remap_states` for state type transformation.

2. **NFA (Non-Deterministic Finite Automaton)**
   - Represents an NFA with methods like `epsilon_closure` and `subset_construction` for state computations.
   - Similar to DFA, with optional state type transformation through `remap_states`.

3. **Regex (Regular Expression)**
   - Implements the Thompson Algorithm for converting Regex to NFA, primarily through the `thompson` method.

4. **Lexer**
   - Implements the lexer, utilizing the converted NFAs to tokenize input based on a provided specification.
   - The `lex` method returns a list of tuples representing tokens and corresponding lexemes. In case of an error, a specific error message format is used.

## How to Use

1. Clone the repository: `git clone [repository_url]`
2. Navigate to the `src` directory: `cd src`
3. Implement the required methods in the provided skeleton.
4. Run tests using: `python3.12 -m unittest`

## Project Purpose

This project demonstrates proficiency in working with finite automata, regular expressions, and lexer implementation in Python. The provided skeleton offers a structured framework for completing each component of the project.

Feel free to explore and modify the code to meet specific requirements or use it as a foundation for similar projects.
