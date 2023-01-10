import math
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

log_files = [
    'call_history_sentiment_1_bash.csv',
    'call_history_text2int_1_bash.csv',
]

for log_file in log_files:
    path_ = f"./data/{log_file}"
    df = pd.read_csv(filepath_or_buffer=path_, sep=";")
    df["finished_ts"] = df["finished"].apply(
        lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f").timestamp())
    df["started_ts"] = df["started"].apply(
        lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f").timestamp())
    df["elapsed"] = df["finished_ts"] - df["started_ts"]

    df["success"] = df["outputs"].apply(lambda x: 0 if "Time-out" in x else 1)

    student_numbers = sorted(df['active_students'].unique())

    bins_dict = dict()  # bins size for each group
    min_finished_dict = dict()  # zero time for each group

    for student_number in student_numbers:
        # for each student group calculates bins size and zero time
        min_finished = df["finished_ts"][df["active_students"] == student_number].min()
        max_finished = df["finished_ts"][df["active_students"] == student_number].max()
        bins = math.ceil(max_finished - min_finished)
        bins_dict.update({student_number: bins})
        min_finished_dict.update({student_number: min_finished})
        print(f"student number: {student_number}")
        print(f"min finished: {min_finished}")
        print(f"max finished: {max_finished}")
        print(f"bins finished seconds: {bins}, minutes: {bins / 60}")

    df["time_line"] = None
    for student_number in student_numbers:
        # calculates time-line for each student group
        df["time_line"] = df.apply(
            lambda x: x["finished_ts"] - min_finished_dict[student_number]
            if x["active_students"] == student_number
            else x["time_line"],
            axis=1
        )

    # creates a '.csv' from the dataframe
    df.to_csv(f"./data/processed_{log_file}", index=False, sep=";")

    result = df.groupby(['active_students', 'success']) \
        .agg({
        'elapsed': ['mean', 'median', 'min', 'max'],
        'success': ['count'],
    })

    print(f"Results for {log_file}")
    print(result, "\n")

    title = None
    if "sentiment" in log_file.lower():
        title = "API result for 'sentiment-analysis' endpoint"
    elif "text2int" in log_file.lower():
        title = "API result for 'text2int' endpoint"

    for student_number in student_numbers:
        # Prints percentage of the successful and failed calls
        try:
            failed_calls = result.loc[(student_number, 0), 'success'][0]
        except:
            failed_calls = 0
        successful_calls = result.loc[(student_number, 1), 'success'][0]
        percentage = (successful_calls / (failed_calls + successful_calls)) * 100
        print(f"Percentage of successful API calls for {student_number} students: {percentage.__round__(2)}")

    rows = len(student_numbers)

    fig, axs = plt.subplots(rows, 2)  # (rows, columns)

    for index, student_number in enumerate(student_numbers):
        # creates a boxplot for each test group
        data = df[df["active_students"] == student_number]
        axs[index][0].boxplot(x=data["elapsed"])  # axs[row][column]
        # axs[index][0].set_title(f'Boxplot for {student_number} students')
        axs[index][0].set_xlabel(f'student number {student_number}')
        axs[index][0].set_ylabel('Elapsed time (s)')

        # creates a histogram for each test group
        axs[index][1].hist(x=data["elapsed"], bins=25)  # axs[row][column]
        # axs[index][1].set_title(f'Histogram for {student_number} students')
        axs[index][1].set_xlabel('seconds')
        axs[index][1].set_ylabel('Count of API calls')

    fig.suptitle(title, fontsize=16)

    fig, axs = plt.subplots(rows, 1)  # (rows, columns)

    for index, student_number in enumerate(student_numbers):
        # creates a histogram and shows API calls on a timeline for each test group
        data = df[df["active_students"] == student_number]

        print(data["time_line"].head(10))

        axs[index].hist(x=data["time_line"], bins=bins_dict[student_number])  # axs[row][column]
        # axs[index][1].set_title(f'Histogram for {student_number} students')
        axs[index].set_xlabel('seconds')
        axs[index].set_ylabel('Count of API calls')

    fig.suptitle(title, fontsize=16)

plt.show()
