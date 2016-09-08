#!/usr/bin/python

import argparse, json, os, psycopg2, sys, yaml

import lib.eversource as eversource
import lib.national_grid as nationalgrid

from datetime import datetime
from os import listdir
from os.path import isfile, join
from time import sleep

class PyBills:

    def __init__(self, eversource_dir, eversource_cache, nationalgrid_dir, nationalgrid_cache, db_info=None):

        self.eversource_cache = eversource_cache
        self.nationalgrid_cache = nationalgrid_cache
        self.eversource_dir = eversource_dir
        self.nationalgrid_dir = nationalgrid_dir

        # load Eversource cache
        if os.path.isfile(eversource_cache):
            with open(eversource_cache, 'r') as stream:
                try:
                    self.eversource_files_loaded = yaml.load(stream)
                except yaml.YAMLError as e:
                    raise e
        else:
            self.eversource_files_loaded = None

        # load National Grid cache
        if os.path.isfile(nationalgrid_cache):
            with open(nationalgrid_cache, 'r') as stream:
                try:
                    self.nationalgrid_files_loaded = yaml.load(stream)
                except yaml.YAMLError as e:
                    raise e
        else:
            self.nationalgrid_files_loaded = None

        # use database?
        self.db_conn = None
        if db_info is not None:
            try:
                self.db_conn = psycopg2.connect(
                    database=db_info['dbname'], 
                    user=db_info['dbuser'], 
                    password=db_info['dbpass'], 
                    host=db_info['dbhost'])
            except psycopg2.Error as e:
                print("Unable to connect to database!\n{:s}".format(str(e)))
                self.db_conn = None


    def start(self):

        if self.eversource_files_loaded is None:
            self.eversource_files_loaded = []

        print("Eversource directory: {:s}".format(self.eversource_dir))

        eversource_files = [f for f in listdir(self.eversource_dir) if isfile(join(self.eversource_dir, f))]
        eversource_files.sort()

        for f in eversource_files:

            if f not in self.eversource_files_loaded:
                eversource_file = "{:s}/{:s}".format(self.eversource_dir, f)
                eversource_data = eversource.parse_eversource_bill(eversource_file)

                # store in database
                if (eversource_data is not None) and (self.db_conn is not None):
                    print("energy_used_kwh = {:.2f}".format(eversource_data['energy_used_kwh']))
                    print("total_cost      = {:.2f}".format(eversource_data['total_cost']))
                    print("start_read_date = {:s}".format(eversource_data['start_read_date'].strftime("%Y-%m-%d")))
                    print("end_read_date   = {:s}".format(eversource_data['end_read_date'].strftime("%Y-%m-%d")))

                    cursor = self.db_conn.cursor()
                    cursor.execute("INSERT INTO electricity_bills (energy_used_kwh, total_cost, start_read_date, end_read_date, created_at, updated_at) VALUES (%s, %s, %s, %s, now(), now())", (
                                eversource_data['energy_used_kwh'],
                                eversource_data['total_cost'],
                                eversource_data['start_read_date'],
                                eversource_data['end_read_date'],
                            )
                        )
                    self.db_conn.commit()
                    cursor.close()

                    # cache the file
                    self.eversource_files_loaded.append(f)

        if self.eversource_files_loaded:
            with open(self.eversource_cache, 'w') as outfile:
                yaml.dump(self.eversource_files_loaded, outfile, default_flow_style=False)


        #=======================================================================


        if self.nationalgrid_files_loaded is None:
            self.nationalgrid_files_loaded = []

        print("National Grid directory: {:s}".format(self.nationalgrid_dir))

        nationalgrid_files = [f for f in listdir(self.nationalgrid_dir) if isfile(join(self.nationalgrid_dir, f))]
        nationalgrid_files.sort()

        for f in nationalgrid_files:

            if f not in self.nationalgrid_files_loaded:
                nationalgrid_file = "{:s}/{:s}".format(self.nationalgrid_dir, f)
                nationalgrid_data = nationalgrid.parse_nationalgrid_bill(nationalgrid_file)

                # store in database
                if (nationalgrid_data is not None) and (self.db_conn is not None):
                    print("heat_used_thm   = {:.2f}".format(nationalgrid_data['heat_used_thm']))
                    print("total_cost      = {:.2f}".format(nationalgrid_data['total_cost']))
                    print("start_read_date = {:s}".format(nationalgrid_data['start_read_date'].strftime("%Y-%m-%d")))
                    print("end_read_date   = {:s}".format(nationalgrid_data['end_read_date'].strftime("%Y-%m-%d")))

                    cursor = self.db_conn.cursor()
                    '''
                    cursor.execute("INSERT INTO gas_bills (heat_used_thm, total_cost, start_read_date, end_read_date, created_at, updated_at) VALUES (%s, %s, %s, %s, now(), now())", (
                                eversource_data['heat_used_thm'],
                                eversource_data['total_cost'],
                                eversource_data['start_read_date'],
                                eversource_data['end_read_date'],
                            )
                        )
                    self.db_conn.commit()
                    '''
                    cursor.close()

                    # cache the file
                    self.nationalgrid_files_loaded.append(f)

        if self.nationalgrid_files_loaded:
            with open(self.nationalgrid_cache, 'w') as outfile:
                yaml.dump(self.nationalgrid_files_loaded, outfile, default_flow_style=False)

        #=======================================================================

        print("Terminating...")



if __name__ == '__main__':
    
    # parse command-line arguments
    #===========================================================================
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-d", "--no-db", 
        help="Disables the use of a database store",
        action="store_true")
    args = arg_parser.parse_args()
    
    disable_database = args.no_db
    
    
    # start the application
    #===========================================================================

    # environment setup
    elec_bills_dir = os.environ['EBILLS_ELEC_PARSED']
    elec_cache = os.environ['EBILLS_ELEC_CACHE']
    gas_bills_dir = os.environ['EBILLS_GAS_PARSED']
    gas_cache = os.environ['EBILLS_GAS_CACHE']

    # parser service
    db_info = None
    if not disable_database:
        db_info = {
            'dbname': os.environ['PYBILLS_DB_NAME'],
            'dbuser': os.environ['PYBILLS_DB_USER'],
            'dbpass': os.environ['PYBILLS_DB_PASS'],
            'dbhost': os.environ['PYBILLS_DB_HOST'],
        }

    pybills = PyBills(elec_bills_dir, elec_cache, gas_bills_dir, gas_cache, db_info)
    pybills.start()
    
    sys.exit(0)
