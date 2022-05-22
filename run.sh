#!/bin/sh
# Copy .jpegs from Downloads within the last day (useful for AirDropped screenshots)
find ~/Downloads/*.jpeg -mtime -1 -exec cp {} ./images \;

# Remove old transactions
if [ -f "transactions.csv" ]; then 
    rm transactions.csv
fi

pipenv run python main.py --imagePath images/ --outputPath transactions.csv
if [ "$?" = "0" ]; then
    # Cleanup after success
    rm images/*
    rm transactions.csv
fi
