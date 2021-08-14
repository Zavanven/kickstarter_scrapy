# It is meant to run with countries.json as argument
# Run with -F "\"" as separator
# gawk -F "\"" -f greater_than_2400.awk countries.json
match($11, /[0-9]+/, matches) && matches[0] > 2400 {print $4 "\t"  matches[0]}
