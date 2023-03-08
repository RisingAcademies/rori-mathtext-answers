import numpy as np
import pandas as pd
import re

from pathlib import Path


def read_and_preprocess_spreadsheet():
    # path = list(Path.cwd().glob('Rori_Framework_v1.xlsx'))
    DATA_DIR = Path(__file__).parent.parent / "mathtext_fastapi" / "data" / "Rori_Framework_v1.xlsx"
    script_df = pd.read_excel(DATA_DIR, engine='openpyxl')
    script_df.columns = script_df.columns[:2].tolist() + script_df.columns[2:11].astype(int).astype(str).tolist() + script_df.columns[11:].tolist()
    script_df.fillna('', inplace=True)
    return script_df


def build_horizontal_transitions_by_row(direction, skill_code, row):
    match_arr = []
    sideways_transitions = []

    second_match = match+1
    if direction == 'left':
        second_match = match-1

    for i in range(9):
        # Grade column
        current_grade = i+1
        if row[current_grade].lower().strip() == 'x':
            match_arr.append(i)
            
    for match in match_arr:
        if match_arr[-1] != match:
            sideways_transitions.append([
                direction,
                f"{skill_code}_G{match}",
                f"{skill_code}_G{second_match}"
            ])
    return sideways_transitions


def extract_skill_code(skill):
    pattern = r'[A-Z][0-9]\.\d+\.\d+'
    result = re.search(pattern, skill)
    return result.group()


def build_horizontal_transitions(script_df):
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
    all_states = []
    for transition in all_transitions:
        for index, state in enumerate(transition):
            if index == 0:
                continue   
            if state not in all_states:
                all_states.append(state)
    return all_states


def build_curriculum_logic():
    script_df = read_and_preprocess_spreadsheet()
    horizontal_transitions = build_horizontal_transitions(script_df)
    vertical_transitions = build_vertical_transitions(script_df)
    all_transitions = horizontal_transitions + vertical_transitions
    all_states = build_all_states(all_transitions)
    return all_states, all_transitions
