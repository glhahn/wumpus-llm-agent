#!/usr/bin/env bash

NUM_TRIALS=30
STRATEGY_ID=$1

if [ -z "$STRATEGY_ID" ]; then
    echo "Usage: ./run_trials.sh"
    exit 1
fi

echo "Running $NUM_TRIALS trials"

for i in $(seq 1 $NUM_TRIALS); do
    echo -e "\nTrial $i of $NUM_TRIALS"
    ./run_game.sh
    sleep 2  # short delay between trials
done

echo -e "\n* Completed $NUM_TRIALS trials."
