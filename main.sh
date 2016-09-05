#!/bin/bash -e

export PYTHONUNBUFFERED=1

EBILLS_INFO_FILE="data/ebills_info.sh"

if [[ -e "$EBILLS_INFO_FILE" ]]; then
    source $EBILLS_INFO_FILE
else
    printf "Missing '$EBILLS_INFO_FILE'\n"
    printf "Create the file with the following contents:\n\n"
    printf "  export EBILLS_ELEC_SOURCE=<pdf bills from Eversource>\n"
    printf "  export EBILLS_ELEC_PARSED=<output directory for parsed Eversource bills>\n"
    printf "  export EBILLS_GAS_SOURCE=<pdf bills from National Grid>\n"
    printf "  export EBILLS_GAS_PARSED=<output directory for parsed National Grid bills>\n"
    printf "\nReplace <...> with appropriate directories.\n\n"
    exit 1
fi



LOG_BASEDIR="/opt/PyBills/log/"
LOG_FILE="pybills_$(date +%Y%m%d_%H%M%S).log"
LOG_FILENAME="${LOG_BASEDIR}${LOG_FILE}"

PYBILLS_DB_INFO_FILE="data/db_info.sh"

if [[ -e "$PYBILLS_DB_INFO_FILE" ]]; then
    source $PYBILLS_DB_INFO_FILE

    exec /usr/bin/python /opt/PyBills/pybills.py > ${LOG_FILENAME} 2>&1

else
    printf "Missing '$PYBILLS_DB_INFO_FILE'\n"
    printf "Create the file with the following contents:\n\n"
    printf "  export PYBILLS_DB_NAME=<PostgreSQL database name>\n"
    printf "  export PYBILLS_DB_USER=<PostgreSQL user name>\n"
    printf "  export PYBILLS_DB_PASS=<PostgreSQL user password>\n"
    printf "  export PYBILLS_DB_HOST=<PostgreSQL hostname>\n"
    printf "\nReplace <...> with appropriate credentials to access your PostgreSQL database.\n\n"
    printf "Running PyBills with database disabled ...\n"
    
    exec /usr/bin/python /opt/PyBills/pybills.py --no-db > ${LOG_FILENAME} 2>&1
fi
