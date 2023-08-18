# import unittest
# from pathlib import Path

# import pandas as pd
# from fastapi.testclient import TestClient

# from app import app

# # The raw file URL has to be used for GitLab.
# URL = "https://gitlab.com/tangibleai/community/mathtext/-/raw/main/mathtext/data/master_test_text2int.csv"

# DATA_DIR = Path(__file__).parent.parent / "mathtext_fastapi" / "data"
# print(DATA_DIR)

# client = TestClient(app)


# class TestStringMethods(unittest.TestCase):

#     def setUp(self):
#         """Creates a fastapi test client"""
#         self.client = TestClient(app)
#         self.df = pd.read_csv(URL)

#     def get_response_text2int(self, text):
#         """Makes a post request to the endpoint"""
#         r = None
#         try:
#             r = self.client.post("/text2int", json={"content": text}) \
#                 .json().get("message")
#         except:
#             pass
#         return r

#     def test_endpoint_text2int(self):
#         """Tests if endpoint is working"""
#         response = self.client.post("/text2int",
#                                     json={"content": "fourteen"}
#                                     )
#         self.assertEqual(response.status_code, 200)

#     def test_acc_score_text2int(self):
#         """Calculates accuracy score for endpoint"""

#         self.df["text2int"] = self.df["input"].apply(func=self.get_response_text2int)
#         self.df["score"] = self.df[["output", "text2int"]].apply(
#             lambda row: row[0] == row[1],
#             axis=1
#         )
#         self.df.to_csv(f"{DATA_DIR}/text2int_results.csv", index=False)
#         acc_score = self.df["score"].mean().__round__(2)

#         self.assertGreaterEqual(acc_score, 0.3, f"Accuracy score: '{acc_score}'. Value is too low!")


# if __name__ == '__main__':
#     unittest.main()
