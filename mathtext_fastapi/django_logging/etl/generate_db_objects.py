import pandas as pd
from pathlib import Path
from mathtext_fastapi.django_logging.django_app.models import Activity

DIR_PATH = Path(__file__).resolve().parent

lesson_list_file = DIR_PATH / "rori_lesson_list.csv"
open_line_params_file = DIR_PATH / "rori_bkt_params_rising_line.csv"
rising_line_params_file = DIR_PATH / "rori_bkt_params_rising_line.csv"


def generate_activity_db_objects():
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

        # Initialize properties as None
        properties = {}

        # Check if open_line_params_df is available and contains data for the activity

        open_line_data = open_line_params_df[
            open_line_params_df["lesson_name"] == activity_name
        ]
        if not open_line_data.empty:
            params = open_line_data.iloc[0]
            properties = {
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
            if not properties:
                properties["bkt_params"] = {}
            properties["bkt_params"]["+12062587201"] = {
                "l0": float(params["L0"]),
                "p_slip": float(params["S"]),
                "p_guess": float(params["G"]),
                "p_transit": float(params["T"]),
            }

        # Creates staging line data
        if not rising_line_data.empty:
            params = rising_line_data.iloc[0]
            if not properties:
                properties["bkt_params"] = {}
            properties["bkt_params"]["+12027737940"] = {
                "l0": float(params["L0"]),
                "p_slip": float(params["S"]),
                "p_guess": float(params["G"]),
                "p_transit": float(params["T"]),
            }

        activity, created = Activity.objects.get_or_create(
            name=activity_name,
            type=lesson_type,
            properties=properties if properties else {},
        )
        activity.save()


if __name__ == "__main__":
    generate_activity_db_objects()
