#root_url="localhost:7860"
root_url="https://cetinca-fastapi-ep.hf.space"

ep="/"
url=$root_url$ep
data=''

response=$(curl --silent -X GET "$url" -H 'Content-Type: application/json')

echo "URL: $url"
echo "Data: $data"
echo "Response: $response"
echo

sleep 0.1

ep="/hello"
url=$root_url$ep
data='{"content":"Rori"}'

response=$(curl --silent -X POST "$url" -H 'Content-Type: application/json' -d "$data")

echo "URL: $url"
echo "Data: $data"
echo "Response: $response"
echo

sleep 0.5

ep="/sentiment-analysis"
url=$root_url$ep
data='{"content":"I am happy with it!"}'

response=$(curl --silent -X POST "$url" -H 'Content-Type: application/json' -d "$data")

echo "URL: $url"
echo "Data: $data"
echo "Response: $response"
echo

sleep 0.5

ep="/text2int"
url=$root_url$ep
data='{"content":"one hundred forty two"}'

response=$(curl --silent -X POST "$url" -H 'Content-Type: application/json' -d "$data")

echo "URL: $url"
echo "Data: $data"
echo "Response: $response"
echo
