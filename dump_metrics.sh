#!/usr/bin/env bash

DB_FILE="wumpus_metrics.db"
OUTPUT_FILE="game_metrics_$(date +%Y%m%d_%H%M%S).csv"

# check if database exists
if [ ! -f "$DB_FILE" ]; then
    echo "* Error: Database file $DB_FILE not found!"
    exit 1
fi

# export game metrics to CSV
sqlite3 -header -csv "$DB_FILE" "
    SELECT 
        m.timestamp,
        m.num_turns,
        m.rooms_explored,
        m.death_by_pit,
        m.death_by_wumpus,
        m.death_by_arrows,
        m.game_won,
        m.arrows_remaining,
        m.action_generation_errors,
        m.average_response_time,
        m.total_response_time
    FROM game_metrics m
    ORDER BY m.timestamp DESC;
" > "$OUTPUT_FILE"

echo "* Detailed metrics exported to $OUTPUT_FILE"
