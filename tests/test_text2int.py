import unittest

from fastapi.testclient import TestClient

from app import app

TEST_DATA_FILE = "data/test_data_text2int.csv"

client = TestClient(app)


class TestStringMethods(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_1(self):
        response = self.client.post("/text2int",
                                    json={"content": "fourteen"}
                                    )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.json()["message"]), "14")

    def test_2(self):
        response = self.client.post("/text2int",
                                    json={"content": "one thousand four hundred ninety two"}
                                    )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.json()["message"]), "1492")

    def test_3(self):
        response = self.client.post("/text2int",
                                    json={"content": "Fourteen Hundred Ninety-Two"}
                                    )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.json()["message"]), "1492")

    def test_4(self):
        response = client.post("/text2int",
                               json={"content": "forteen"}
                               )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.json()["message"]), "14")

    def test_5(self):
        response = client.post("/text2int",
                               json={"content": "seventeen-thousand and seventy two"}
                               )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.json()["message"]), "17072")

    def test_6(self):
        response = client.post("/text2int",
                               json={"content": "two hundred and nine"}
                               )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.json()["message"]), "209")


if __name__ == '__main__':
    unittest.main()
