#!/bin/bash -e

export PYTHONUNBUFFERED=1

export EBILLS_ELEC_CACHE="data/eversource.yml"
export EBILLS_GAS_CACHE="data/national.yml"

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

EBILL_ELEC_PREFIX="eversource"
EBILL_GAS_PREFIX="national"

# parse the pdf utility bills into text
#-------------------------------------------------------------------------------

# Eversource electricity bill
for f in $( ls ${EBILLS_ELEC_SOURCE}/${EBILL_ELEC_PREFIX}* ); do
    EBILL_PDF=$(basename $f)
    EBILL_TXT=$(echo $EBILL_PDF | sed -r 's/pdf$/txt/')
    EBILL_TXT_FILE="${EBILLS_ELEC_PARSED}/${EBILL_TXT}"
    
    # parse if it hasn't been done already
    if [[ ! -e "${EBILL_TXT_FILE}" ]]; then
        echo "Parsing ${f} into ${EBILL_TXT_FILE} ..."
        pdf2txt.py | sed 's/\x0C//g' | grep '[^[:blank:]]' > ${EBILL_TXT_FILE}
    fi
done

# National Grid electricity bill
for f in $( ls ${EBILLS_GAS_SOURCE}/${EBILL_GAS_PREFIX}* ); do
    EBILL_PDF=$(basename $f)
    EBILL_TXT=$(echo $EBILL_PDF | sed -r 's/pdf$/txt/')
    EBILL_TXT_FILE="${EBILLS_GAS_PARSED}/${EBILL_TXT}"
    
    # parse if it hasn't been done already
    if [[ ! -e "${EBILL_TXT_FILE}" ]]; then
        echo "Parsing ${f} into ${EBILL_TXT_FILE} ..."
        pdf2txt.py -F 1.0 ${f} | sed 's/\xC2\xA0/ /g' | grep '[^[:blank:]]' > ${EBILL_TXT_FILE}
    fi
done

LOG_BASEDIR="/opt/PyBills/log/"
LOG_FILE="pybills_$(date +%Y%m%d_%H%M%S).log"
LOG_FILENAME="${LOG_BASEDIR}${LOG_FILE}"

PYBILLS_DB_INFO_FILE="data/db_info.sh"

if [[ -e "$PYBILLS_DB_INFO_FILE" ]]; then
    source $PYBILLS_DB_INFO_FILE

    exec /usr/bin/python /opt/PyBills/pybills.py #> ${LOG_FILENAME} 2>&1

else
    printf "Missing '$PYBILLS_DB_INFO_FILE'\n"
    printf "Create the file with the following contents:\n\n"
    printf "  export PYBILLS_DB_NAME=<PostgreSQL database name>\n"
    printf "  export PYBILLS_DB_USER=<PostgreSQL user name>\n"
    printf "  export PYBILLS_DB_PASS=<PostgreSQL user password>\n"
    printf "  export PYBILLS_DB_HOST=<PostgreSQL hostname>\n"
    printf "\nReplace <...> with appropriate credentials to access your PostgreSQL database.\n\n"
    printf "Running PyBills with database disabled ...\n"
    
    exec /usr/bin/python /opt/PyBills/pybills.py --no-db #> ${LOG_FILENAME} 2>&1
fi
