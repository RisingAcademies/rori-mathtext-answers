import pandas as pd
from mathtext_fastapi.django_logging.django_app.models import Activity

lesson_list_file = "mathtext_fastapi/django_logging/etl/rori_lesson_list.csv"
open_line_params_file = (
    "mathtext_fastapi/django_logging/etl/rori_bkt_params_open_line.csv"
)
rising_line_params_file = (
    "mathtext_fastapi/django_logging/etl/rori_bkt_params_rising_line.csv"
)

# Read CSV files into Pandas DataFrames
lesson_list_df = pd.read_csv(lesson_list_file)
open_line_params_df = (
    pd.read_csv(open_line_params_file) if open_line_params_file else None
)
rising_line_params_df = (
    pd.read_csv(rising_line_params_file) if rising_line_params_file else None
)

for index, row in lesson_list_df.iterrows():
    activity_name = row["lesson_name"]
    lesson_type = "math_answer_api"

    # Initialize content as None
    content = {}

    # Check if open_line_params_df is available and contains data for the activity

    open_line_data = open_line_params_df[
        open_line_params_df["lesson_name"] == activity_name
    ]
    if not open_line_data.empty:
        params = open_line_data.iloc[0]
        content = {
            "bkt_params": {
                "+12065906259": {
                    "l0": float(params["L0"]),
                    "p_slip": float(params["S"]),
                    "p_guess": float(params["G"]),
                    "p_transit": float(params["T"]),
                }
            }
        }

    rising_line_data = rising_line_params_df[
        rising_line_params_df["lesson_name"] == activity_name
    ]
    if not rising_line_data.empty:
        params = rising_line_data.iloc[0]
        if not content:
            content["bkt_params"] = {}
        content["bkt_params"]["+12062587201"] = {
            "l0": float(params["L0"]),
            "p_slip": float(params["S"]),
            "p_guess": float(params["G"]),
            "p_transit": float(params["T"]),
        }

    activity, created = Activity.objects.get_or_create(
        name=activity_name,
        type=lesson_type,
        content=content if content else {},
    )
    activity.save()
