import os, re

from datetime import datetime

def parse_eversource_bill(filename):
    print("file: {:s}".format(filename))

    # parsed data
    eversource_data = {
    	'energy_used_kwh': 0.0,
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

    state = SEARCHING_READ_DATES
    count = 0


    with open(filename, 'r') as f:
        for line in f:
        	if (state == SEARCHING_READ_DATES) and re.match(r"Meter [0-9]+", line):
        		state = SEARCHING_END_READ_DATE

        	elif (state == SEARCHING_END_READ_DATE):
        		regex = re.match(r"([A-Za-z]{3} [0-9]{2}, [0-9]{4}).*", line)
        		date_string = regex.group(1)
        		eversource_data['end_read_date'] = datetime.strptime(date_string, "%b %d, %Y")
        		state = SEARCHING_START_READ_DATE

        	elif (state == SEARCHING_START_READ_DATE):
        		regex = re.match(r"([A-Za-z]{3} [0-9]{2}, [0-9]{4}).*", line)
        		date_string = regex.group(1)
        		eversource_data['start_read_date'] = datetime.strptime(date_string, "%b %d, %Y")
        		state = SEARCHING_ENERGY_USED
        		count = 0

        	elif (state == SEARCHING_ENERGY_USED) and re.match(r"[0-9]+$", line):
        		count += 1
        		if count == 3:
        			regex = re.match(r"([0-9]+).*", line)
        			eversource_data['energy_used_kwh'] = float(regex.group(1))
        			state = SEARCHING_TOTAL_COST

        	elif (state == SEARCHING_TOTAL_COST) and re.match(r"Total Cost of Electricity.*", line):
        		state = SEARCHING_TOTAL_COST_VALUE

        	elif (state == SEARCHING_TOTAL_COST_VALUE) and re.match(r"[0-9\.]+.*", line):
        		regex = re.match(r"([0-9\.]+).*", line)
        		eversource_data['total_cost'] = float(regex.group(1))
        		state = PARSING_DONE
        		break


    return eversource_data
