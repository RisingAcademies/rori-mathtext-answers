import numpy as np
import pandas as pd
import re

from pathlib import Path


def read_and_preprocess_spreadsheet(file_name):
    """ Creates a pandas dataframe from the curriculum overview spreadsheet """
    DATA_DIR = Path(__file__).parent.parent / "mathtext_fastapi" / "data" / file_name
    script_df = pd.read_excel(DATA_DIR, engine='openpyxl')
    # Ensures the grade level columns are integers instead of floats
    script_df.columns = script_df.columns[:2].tolist() + script_df.columns[2:11].astype(int).astype(str).tolist() + script_df.columns[11:].tolist()
    script_df.fillna('', inplace=True)
    return script_df


def extract_skill_code(skill):
    """ Looks within a curricular skill description for its descriptive code

    Input
    - skill: str - a brief description of a curricular skill

    >>> extract_skill_code('A3.3.4 - Solve inequalities')
    'A3.3.4'
    >>> extract_skill_code('A3.3.2 - Graph linear equations, and identify the x- and y-intercepts or the slope of a line')
    'A3.3.2'
    """
    pattern = r'[A-Z][0-9]\.\d+\.\d+'
    result = re.search(pattern, skill)
    return result.group()


def build_horizontal_transitions(script_df):
    """ Build a list of transitional relationships within a curricular skill

    Inputs
    - script_df: pandas dataframe - an overview of the curriculum skills by grade level

    Output
    - horizontal_transitions: array of arrays - transition data with label, from state, and to state

    >>> script_df = read_and_preprocess_spreadsheet('curriculum_framework_for_tests.xlsx')
    >>> build_horizontal_transitions(script_df)
    [['right', 'N1.1.1_G1', 'N1.1.1_G2'], ['right', 'N1.1.1_G2', 'N1.1.1_G3'], ['right', 'N1.1.1_G3', 'N1.1.1_G4'], ['right', 'N1.1.1_G4', 'N1.1.1_G5'], ['right', 'N1.1.1_G5', 'N1.1.1_G6'], ['left', 'N1.1.1_G6', 'N1.1.1_G5'], ['left', 'N1.1.1_G5', 'N1.1.1_G4'], ['left', 'N1.1.1_G4', 'N1.1.1_G3'], ['left', 'N1.1.1_G3', 'N1.1.1_G2'], ['left', 'N1.1.1_G2', 'N1.1.1_G1'], ['right', 'N1.1.2_G1', 'N1.1.2_G2'], ['right', 'N1.1.2_G2', 'N1.1.2_G3'], ['right', 'N1.1.2_G3', 'N1.1.2_G4'], ['right', 'N1.1.2_G4', 'N1.1.2_G5'], ['right', 'N1.1.2_G5', 'N1.1.2_G6'], ['left', 'N1.1.2_G6', 'N1.1.2_G5'], ['left', 'N1.1.2_G5', 'N1.1.2_G4'], ['left', 'N1.1.2_G4', 'N1.1.2_G3'], ['left', 'N1.1.2_G3', 'N1.1.2_G2'], ['left', 'N1.1.2_G2', 'N1.1.2_G1']]
    """
    horizontal_transitions = []
    for index, row in script_df.iterrows():     
        skill_code = extract_skill_code(row['Knowledge or Skill'])

        rightward_matches = []
        for i in range(9):
            # Grade column
            current_grade = i+1
            if row[current_grade].lower().strip() == 'x':
                rightward_matches.append(i)
            
        for match in rightward_matches:
            if rightward_matches[-1] != match:
                horizontal_transitions.append([
                    "right",
                    f"{skill_code}_G{match}",
                    f"{skill_code}_G{match+1}"
                ])

        leftward_matches = []
        for i in reversed(range(9)):
            current_grade = i
            if row[current_grade].lower().strip() == 'x':
                leftward_matches.append(i)

        for match in leftward_matches:
            if leftward_matches[0] != match:
                horizontal_transitions.append([
                    "left",
                    f"{skill_code}_G{match}",
                    f"{skill_code}_G{match-1}"
                ])

    return horizontal_transitions


def gather_all_vertical_matches(script_df):
    """ Build a list of transitional relationships within a grade level across skills

    Inputs
    - script_df: pandas dataframe - an overview of the curriculum skills by grade level

    Output
    - all_matches: array of arrays - represents skills at each grade level

    >>> script_df = read_and_preprocess_spreadsheet('curriculum_framework_for_tests.xlsx')
    >>> gather_all_vertical_matches(script_df)
    [['N1.1.1', '1'], ['N1.1.2', '1'], ['N1.1.1', '2'], ['N1.1.2', '2'], ['N1.1.1', '3'], ['N1.1.2', '3'], ['N1.1.1', '4'], ['N1.1.2', '4'], ['N1.1.1', '5'], ['N1.1.2', '5'], ['N1.1.1', '6'], ['N1.1.2', '6']]
    """
    all_matches = []
    columns = ['1', '2', '3', '4', '5', '6', '7', '8', '9']

    for column in columns:
        for index, value in script_df[column].iteritems():
            row_num = index + 1
            if value == 'x':
                # Extract skill code
                skill_code = extract_skill_code(
                    script_df['Knowledge or Skill'][row_num-1]
                )

                all_matches.append([skill_code, column])
    return all_matches


def build_vertical_transitions(script_df):
    """ Build a list of transitional relationships within a grade level across skills

    Inputs
    - script_df: pandas dataframe - an overview of the curriculum skills by grade level

    Output
    - vertical_transitions: array of arrays - transition data with label, from state, and to state

    >>> script_df = read_and_preprocess_spreadsheet('curriculum_framework_for_tests.xlsx')
    >>> build_vertical_transitions(script_df)
    [['down', 'N1.1.1_G1', 'N1.1.2_G1'], ['down', 'N1.1.2_G1', 'N1.1.1_G1'], ['down', 'N1.1.1_G2', 'N1.1.2_G2'], ['down', 'N1.1.2_G2', 'N1.1.1_G2'], ['down', 'N1.1.1_G3', 'N1.1.2_G3'], ['down', 'N1.1.2_G3', 'N1.1.1_G3'], ['down', 'N1.1.1_G4', 'N1.1.2_G4'], ['down', 'N1.1.2_G4', 'N1.1.1_G4'], ['down', 'N1.1.1_G5', 'N1.1.2_G5'], ['down', 'N1.1.2_G5', 'N1.1.1_G5'], ['down', 'N1.1.1_G6', 'N1.1.2_G6'], ['up', 'N1.1.2_G6', 'N1.1.1_G6'], ['up', 'N1.1.1_G6', 'N1.1.2_G6'], ['up', 'N1.1.2_G5', 'N1.1.1_G5'], ['up', 'N1.1.1_G5', 'N1.1.2_G5'], ['up', 'N1.1.2_G4', 'N1.1.1_G4'], ['up', 'N1.1.1_G4', 'N1.1.2_G4'], ['up', 'N1.1.2_G3', 'N1.1.1_G3'], ['up', 'N1.1.1_G3', 'N1.1.2_G3'], ['up', 'N1.1.2_G2', 'N1.1.1_G2'], ['up', 'N1.1.1_G2', 'N1.1.2_G2'], ['up', 'N1.1.2_G1', 'N1.1.1_G1']]
    """
    vertical_transitions = []

    all_matches = gather_all_vertical_matches(script_df)

    # Downward
    for index, match in enumerate(all_matches):
        skill = match[0]
        row_num = match[1]
        if all_matches[-1] != match:
            vertical_transitions.append([
                "down",
                f"{skill}_G{row_num}",
                f"{all_matches[index+1][0]}_G{row_num}"
            ])

    # Upward
    for index, match in reversed(list(enumerate(all_matches))):
        skill = match[0]
        row_num = match[1]
        if all_matches[0] != match:
            vertical_transitions.append([
                "up",
                f"{skill}_G{row_num}",
                f"{all_matches[index-1][0]}_G{row_num}"
            ])
    
    return vertical_transitions


def build_all_states(all_transitions):
    """ Creates an array with all state labels for the curriculum

    Input
    - all_transitions: list of lists - all possible up, down, left, or right transitions in curriculum

    Output
    - all_states: list - a collection of state labels (skill code and grade number)
    
    >>> all_transitions = [['right', 'N1.1.1_G1', 'N1.1.1_G2'], ['right', 'N1.1.1_G2', 'N1.1.1_G3'], ['right', 'N1.1.1_G3', 'N1.1.1_G4'], ['right', 'N1.1.1_G4', 'N1.1.1_G5'], ['right', 'N1.1.1_G5', 'N1.1.1_G6'], ['left', 'N1.1.1_G6', 'N1.1.1_G5'], ['left', 'N1.1.1_G5', 'N1.1.1_G4'], ['left', 'N1.1.1_G4', 'N1.1.1_G3'], ['left', 'N1.1.1_G3', 'N1.1.1_G2'], ['left', 'N1.1.1_G2', 'N1.1.1_G1'], ['right', 'N1.1.2_G1', 'N1.1.2_G2'], ['right', 'N1.1.2_G2', 'N1.1.2_G3'], ['right', 'N1.1.2_G3', 'N1.1.2_G4'], ['right', 'N1.1.2_G4', 'N1.1.2_G5'], ['right', 'N1.1.2_G5', 'N1.1.2_G6'], ['left', 'N1.1.2_G6', 'N1.1.2_G5'], ['left', 'N1.1.2_G5', 'N1.1.2_G4'], ['left', 'N1.1.2_G4', 'N1.1.2_G3'], ['left', 'N1.1.2_G3', 'N1.1.2_G2'], ['left', 'N1.1.2_G2', 'N1.1.2_G1'], ['down', 'N1.1.1_G1', 'N1.1.2_G1'], ['down', 'N1.1.2_G1', 'N1.1.1_G1'], ['down', 'N1.1.1_G2', 'N1.1.2_G2'], ['down', 'N1.1.2_G2', 'N1.1.1_G2'], ['down', 'N1.1.1_G3', 'N1.1.2_G3'], ['down', 'N1.1.2_G3', 'N1.1.1_G3'], ['down', 'N1.1.1_G4', 'N1.1.2_G4'], ['down', 'N1.1.2_G4', 'N1.1.1_G4'], ['down', 'N1.1.1_G5', 'N1.1.2_G5'], ['down', 'N1.1.2_G5', 'N1.1.1_G5'], ['down', 'N1.1.1_G6', 'N1.1.2_G6'], ['up', 'N1.1.2_G6', 'N1.1.1_G6'], ['up', 'N1.1.1_G6', 'N1.1.2_G6'], ['up', 'N1.1.2_G5', 'N1.1.1_G5'], ['up', 'N1.1.1_G5', 'N1.1.2_G5'], ['up', 'N1.1.2_G4', 'N1.1.1_G4'], ['up', 'N1.1.1_G4', 'N1.1.2_G4'], ['up', 'N1.1.2_G3', 'N1.1.1_G3'], ['up', 'N1.1.1_G3', 'N1.1.2_G3'], ['up', 'N1.1.2_G2', 'N1.1.1_G2'], ['up', 'N1.1.1_G2', 'N1.1.2_G2'], ['up', 'N1.1.2_G1', 'N1.1.1_G1']]
    >>> build_all_states(all_transitions)
    ['N1.1.1_G1', 'N1.1.1_G2', 'N1.1.1_G3', 'N1.1.1_G4', 'N1.1.1_G5', 'N1.1.1_G6', 'N1.1.2_G1', 'N1.1.2_G2', 'N1.1.2_G3', 'N1.1.2_G4', 'N1.1.2_G5', 'N1.1.2_G6']
    """
    all_states = []
    for transition in all_transitions:
        for index, state in enumerate(transition):
            if index == 0:
                continue   
            if state not in all_states:
                all_states.append(state)
    return all_states


def build_curriculum_logic():
    script_df = read_and_preprocess_spreadsheet('Rori_Framework_v1.xlsx')
    horizontal_transitions = build_horizontal_transitions(script_df)
    vertical_transitions = build_vertical_transitions(script_df)
    all_transitions = horizontal_transitions + vertical_transitions
    all_states = build_all_states(all_transitions)
    return all_states, all_transitions
