#! /bin/env bash

LOG_FILE_NAME="call_history_bash.csv"

if [[ ! -f "$LOG_FILE_NAME" ]]; then
  # Creation of column names if the file does not exits
  echo "student_id;active_students;endpoint;inputs;outputs;started;finished" >$LOG_FILE_NAME
fi

data_list_1() {
  responses=(
    "one hundred forty five"
    "twenty thousand nine hundred fifty"
    "one hundred forty five"
    "nine hundred eighty three"
    "five million"
  )
  echo "${responses[$1]}"
}

data_list_2() {
  responses=(
    "Totally agree"
    "I like it"
    "No more"
    "I am not sure"
    "Never"
  )
  echo "${responses[$1]}"
}

# endpoints: "text2int" "intent-recognition"
# selected endpoint to test
endpoint="intent-recognition"

create_random_delay() {
  # creates a random delay for given arguments
  echo "scale=8; $RANDOM/32768*$1" | bc
}

simulate_student() {
  # Student simulator waits randomly between 0-10s after an interaction.
  # Based on 100 interactions per student
  for i in {1..100}; do

    random_value=$((RANDOM % 5))
    text=$(data_list_2 $random_value)
    data='{"data": ["'$text'"]}'

    start_=$(date +"%F %T.%6N")

    url="https://tangibleai-mathtext-fastapi.hf.space/$3"
    response=$(curl --silent --connect-timeout 30 --max-time 30 -X POST "$url" -H 'Content-Type: application/json' -d "$data")

    if [[ "$response" == *"Time-out"* ]]; then
      echo "$response" >>bad_response.txt
      response="504 Gateway Time-out"
    elif [[ -z "$response" ]]; then
      echo "No response" >>bad_response.txt
      response="504 Gateway Time-out"
    fi

    end_=$(date +"%F %T.%6N")

    printf "%s;%s;%s;%s;%s;%s;%s\n" "$1" "$2" "$3" "$data" "$response" "$start_" "$end_" >>$LOG_FILE_NAME
    sleep "$(create_random_delay 10)"

  done
}

echo "start: $(date)"

active_students=250 # the number of students using the system at the same time

i=1
while [[ "$i" -le "$active_students" ]]; do
  simulate_student "student$i" "$active_students" "$endpoint" &
  sleep "$(create_random_delay 1)" # adding a random delay between students
  i=$(("$i" + 1))
done

wait
echo "end: $(date)"
