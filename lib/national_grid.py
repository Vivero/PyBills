import os, re

from datetime import datetime

def parse_nationalgrid_bill(filename):
    print("file: {:s}".format(filename))

    # parsed data
    nationalgrid_data = {
        'heat_used_thm': 0.0,
        'total_cost': 0.0,
        'start_read_date': None,
        'end_read_date': None,
    }

    # define a state machine
    PARSING_DONE = 0
    SEARCHING_READ_DATES = 1
    SEARCHING_END_READ_DATE = 2
    SEARCHING_START_READ_DATE = 3
    SEARCHING_ENERGY_USED = 4
    SEARCHING_TOTAL_COST = 5
    SEARCHING_TOTAL_COST_VALUE = 6

    state = SEARCHING_ENERGY_USED
    count = 0


    with open(filename, 'r') as f:
        for line in f:
            if (state == SEARCHING_ENERGY_USED) and re.match(r"In [0-9]+ days.*", line):
                regex = re.match(r"In [0-9]+ days you used ([0-9]+).*", line)
                nationalgrid_data['heat_used_thm'] = float(regex.group(1))
                state = SEARCHING_END_READ_DATE

            elif (state == SEARCHING_END_READ_DATE):
                regex = re.match(r"([0-9]{2}/[0-9]{2}/[0-9]{4}) reading.*", line)
                date_string = regex.group(1)
                nationalgrid_data['end_read_date'] = datetime.strptime(date_string, "%m/%d/%Y")
                state = SEARCHING_START_READ_DATE

            elif (state == SEARCHING_START_READ_DATE):
                regex = re.match(r"([0-9]{2}/[0-9]{2}/[0-9]{4}) reading.*", line)
                date_string = regex.group(1)
                nationalgrid_data['start_read_date'] = datetime.strptime(date_string, "%m/%d/%Y")
                state = SEARCHING_TOTAL_COST

    with open(filename, 'r') as f:
        for line in f:

            if (state == SEARCHING_TOTAL_COST) and re.match(r"please pay.*", line, re.IGNORECASE):
                state = SEARCHING_TOTAL_COST_VALUE

            elif (state == SEARCHING_TOTAL_COST_VALUE) and re.match(r"\$.*", line):
                regex = re.match(r"\$([0-9\.]+).*", line)
                nationalgrid_data['total_cost'] = float(regex.group(1))
                state = PARSING_DONE
                break


    return nationalgrid_data
