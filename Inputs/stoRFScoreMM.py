################################################################################
# * The contents of this file are Teradata Public Content and have been released
# * to the Public Domain.
# * Please see license.txt file in the package for more information.
# * Alexander Kolovos and Tim Miller - May 2021 - v.2.0
# * Copyright (c) 2021 by Teradata
# * Licensed under BSD
#
# ##############################################################################
# TechBytes: Using Python with Teradata Vantage - Part 4 - Demo
# ------------------------------------------------------------------------------
# File: stoRFScoreMM.py
# ##############################################################################
#
# This TechBytes demo utilizes a use case to predict per state code partition
# the propensity of a financial services customer base to open a credit card
# account.
#
# The present file is the Python scoring script to be used with the SCRIPT
# table operator, as described in the use case "Micromodeling: Scaled,
# In-Database training and scoring of multiple models" of the Part 4
# "TBv2_Py-4-In_DB_Scripting.ipynb" notebook in this Using Python with Vantage
# TechByte.
#
################################################################################

import sys
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle
import base64

delimiter = ','

rowToScore = []

# Know your data: You must know in advance the number and data types of the
# incoming columns from the SQL Engine database!
# Note: When working with teradataml, you can inspect the data types of the
#       input table columns by creating a teradataml DataFrame form the table
#       on the client, and subsequently applying the dtypes method to the
#       DataFrame.
#
colNames = ['cust_id', 'income', 'age', 'tot_cust_years', 'tot_children',
            'female_ind', 'single_ind', 'married_ind', 'separated_ind',
            'state_code', 'ca_resident_ind', 'ny_resident_ind', 'tx_resident_ind',
            'il_resident_ind', 'az_resident_ind', 'oh_resident_ind',
            'ck_acct_ind', 'sv_acct_ind', 'cc_acct_ind',
            'ck_avg_bal', 'sv_avg_bal', 'cc_avg_bal', 'ck_avg_tran_amt',
            'sv_avg_tran_amt', 'cc_avg_tran_amt', 'q1_trans_cnt',
            'q2_trans_cnt', 'q3_trans_cnt', 'q4_trans_cnt']
#
# Of the above input columns, we need to ensure numeric ones are interpreted
# correctly as rows are streamed as strings into the script by the Database.
# If any numbers are streamed in scientific format that contains blanks,
# (such as "1 E002" for 100), the following Lambda functions remove blanks
# from the input string so that Python interprets the number correctly.
#
sciStrToFloat = lambda x: float("".join(x.split()))
sciStrToInt = lambda x: int(float("".join(x.split())))
# Use these Lambda functions in the following converters for each input culumn.
converters = { 0: sciStrToInt,
               1: sciStrToFloat,
               2: sciStrToInt,
               3: sciStrToInt,
               4: sciStrToInt,
               5: sciStrToInt,
               6: sciStrToInt,
               7: sciStrToInt,
               8: sciStrToInt,
              10: sciStrToInt,
              11: sciStrToInt,
              12: sciStrToInt,
              13: sciStrToInt,
              14: sciStrToInt,
              15: sciStrToInt,
              16: sciStrToInt,
              17: sciStrToInt,
              18: sciStrToInt,
              19: sciStrToFloat,
              20: sciStrToFloat,
              21: sciStrToFloat,
              22: sciStrToFloat,
              23: sciStrToFloat,
              24: sciStrToFloat,
              25: sciStrToInt,
              26: sciStrToInt,
              27: sciStrToInt,
              28: sciStrToInt}

# To choose the correct model, the script needs to know which state_code is
# being currently processed in the Database AMP it executes on. Start by
# reading just the first streamed row of data to extract the state_code.
#
try:
    line = input()
    # If the first row of data is blank, the AMP has no data. Exit gracefully.
    if line == '':
        sys.exit()
    else:
        allArgs = line.split(delimiter)
        args_1 = [int(x.replace(" ","")) for x in allArgs[0:1]]
        args_2 = [float(x.replace(" ","")) for x in allArgs[1:2]]
        args_3 = [int(x.replace(" ","")) for x in allArgs[2:9]]
        args_4 = [int(x.replace(" ","")) for x in allArgs[10:19]]
        args_5 = [float(x.replace(" ","")) for x in allArgs[19:25]]
        args_6 = [int(x.replace(" ","")) for x in allArgs[25:]]
        currStateCode = allArgs[9].strip()
        rowToScore = args_1 + args_2 + args_3 + [currStateCode] + args_4 + args_5 + args_6
except (EOFError):   # Exit gracefully if no input received at all
    sys.exit()

###
### Load appropriate model from input file
###
# Before you execute the following statement, replace <DBNAME> with the
# database name in the target Vantage Advanced SQL Engine where you have
# previously uploaded the model file to.
#
allStateModels = pd.read_csv('./TRNG_TECHBYTES/multipleModels_py.csv')

# Identify and isolate the model we need for the current state code
#
modelSerB64 = allStateModels.loc[
    allStateModels['State_Code'].str.strip() == currStateCode,
    ['Model'] ].iloc[0,0].strip()

# The input model is expected to be a string in encoded, serialized raw format.
# Follow the inverse process to obtain the model. First, decode the CLOB from
# base64 into serialized raw. Then, unserialize.
#
modelSerB64 = modelSerB64.partition("'")[2]
modelSer = base64.b64decode(modelSerB64)
currStateClassifier = pickle.loads(modelSer)

###
### Ingest and process the rest of the input data rows, nRowsIn at a pass
###
nRowsIn = 500

# To read input in chunks, the read_csv reader function must have the
# iterator argument set to True. The following assigns the function to
# an object that we name reader. The reader object will be used in the
# following with the get_chunk() function to read the data in chunks.
reader = pd.read_csv(sys.stdin, sep=delimiter, header=None, names=colNames,
                     index_col=False, iterator=True, converters=converters)

# Use try...except to produce an error if something goes wrong in the try block
try:

    while 1:

        try:
            # CAUTION: The following statement CONTINUES the row index count for
            #          the DataFrame from where the previous iteration stopped!
            dfToScore = reader.get_chunk(nRowsIn)
        except (EOFError, StopIteration):
            # Exit gracefully if no input received at all or iteration complete
            sys.exit()
        except:              # Raise an exception if other error encountered
            raise

        # Exit gracefully, if DataFrame is empty.
        if dfToScore.empty:
            sys.exit()

        # The first pass must also include the rowToScore list of the first row
        if rowToScore:
            dfToScore.loc[-1] = rowToScore
            dfToScore.index = dfToScore.index+1
            dfToScore = dfToScore.sort_index()
            rowToScore = []

        # Reset DataFrame index to start row index count from 0.
        dfToScore.reset_index(drop = True, inplace = True)

        ###
        ### Score the test table data with the given model
        ###
        predictor_columns = ["income", "age", "tot_cust_years", "tot_children",
                     "female_ind", "single_ind", "married_ind", "separated_ind",
                     "ck_acct_ind", "sv_acct_ind", "ck_avg_bal", "sv_avg_bal",
                     "ck_avg_tran_amt", "sv_avg_tran_amt", "q1_trans_cnt",
                     "q2_trans_cnt", "q3_trans_cnt", "q4_trans_cnt"]

        # Specify the rows to be scored by the model and call the predictor.
        X_test = dfToScore[predictor_columns]
        PredictionProba = currStateClassifier.predict_proba(X_test)

        dfOut = pd.concat([ dfToScore[['cust_id', 'state_code', 'cc_acct_ind']],
                            pd.DataFrame(data=PredictionProba, columns=['Prob0','Prob1'])
                          ], axis=1)

        # Send results to Advanced SQL Engine through stdout in expected format.
        for index, row in dfOut.iterrows():
            print(row['state_code'], delimiter, row['cust_id'], delimiter,
                  row['Prob0'], delimiter, row['Prob1'], delimiter,
                  row['cc_acct_ind'])

except (SystemExit):
    # Skip exception if system exit requested in try block
    pass
except:    # Specify in standard error any other error encountered
    print("Script Failure :", sys.exc_info()[0], file=sys.stderr)
    raise
    sys.exit()
