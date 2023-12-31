"""https://zetcode.com/python/concurrent-http-requests/"""

import asyncio
import random
import time
import pandas as pd
import httpx
from os.path import exists

NUMBER_OF_CALLS = 1

headers = {"Content-Type": "application/json; charset=utf-8"}

# base_url = "https://tangibleai-mathtext-fastapi.hf.space/{endpoint}"
base_url = "http://localhost:7860/run/{endpoint}"

DATA_LIST = [{
    "endpoint": "text2int",
    "test_data": [
        "one hundred forty five",
        "twenty thousand nine hundred fifty",
        "one hundred forty five",
        "nine hundred eighty three",
        "five million",
    ]}, {
    "endpoint": "text2int-preprocessed",
    "test_data": [
        "one hundred forty five",
        "twenty thousand nine hundred fifty",
        "one hundred forty five",
        "nine hundred eighty three",
        "five million",
    ]}, {
    "endpoint": "sentiment-analysis",
    "test_data": [
        "Totally agree",
        "I like it",
        "No more",
        "I am not sure",
        "Never",
    ]
}]


# async call to endpoint
async def call_api(url, data, call_number, number_of_calls):
    json = {"data": [data]}
    async with httpx.AsyncClient() as client:
        start = time.perf_counter()  # Used perf_counter for more precise result.
        response = await client.post(url=url, headers=headers, json=json, timeout=30)
        end = time.perf_counter()
        return {
            "endpoint": url.split("/")[-1],
            "test data": data,
            "status code": response.status_code,
            "response": response.json().get("data"),
            "call number": call_number,
            "number of calls": number_of_calls,
            "start": start.__round__(4),
            "end": end.__round__(4),
            "delay": (end - start).__round__(4)
        }


async def main(number_of_calls=NUMBER_OF_CALLS, data_lists=DATA_LIST):
    results = []
    for data_list in data_lists:
        calls = []
        for call_number in range(1, number_of_calls + 1):
            url = base_url.format(endpoint=data_list["endpoint"])
            data = random.choice(data_list["test_data"])
            calls.append(call_api(url, data, call_number, number_of_calls))
        r = await asyncio.gather(*calls)
        results.extend(r)
    return results


if __name__ == '__main__':
    start = time.perf_counter()
    results = asyncio.run(main())
    end = time.perf_counter()
    print(end-start)
    df = pd.DataFrame(results)

    if exists("call_history.csv"):
        df.to_csv(path_or_buf="call_history.csv", mode="a", header=False, index=False)
    else:
        df.to_csv(path_or_buf="call_history.csv", mode="w", header=True, index=False)
