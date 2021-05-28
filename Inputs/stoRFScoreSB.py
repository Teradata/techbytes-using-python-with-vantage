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
# File: stoRFScoreSB.py
# ##############################################################################
#
# This TechBytes demo utilizes a use case to predict the propensity of a
# financial services customer base to open a credit card account.
#
# The present file is the Python scoring script to be used with the SCRIPT
# table operator, as described in the use case "BYOM: In-Database scoring with
# external Python model" of the Part 4 "TBv2_Py-4-In_DB_Scripting.ipynb"
# notebook in this Using Python with Vantage TechByte.
#
################################################################################

import sys
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle
import base64

###
### Read input
###

delimiter = ','
inputData = []

for line in sys.stdin.read().splitlines():
    line = line.split(delimiter)
    inputData.append(line)

###
### If no data received, gracefully exit rather than producing an error later.
###

if not inputData:
    sys.exit()

###
### Set up input DataFrame according to input schema
###

# Know your data: You must know in advance the number and data types of the
# incoming columns from the database!
# For numeric columns, the database sends in floats in scientific format with a
# blank space when the exponential is positive; e.g., 1.0 is sent as 1.000E 000.
# The following input data read deals with any such blank spaces in numbers.

columns = ['cust_id', 'income', 'age', 'tot_cust_years', 'tot_children',
           'female_ind', 'single_ind', 'married_ind', 'separated_ind',
           'state_code', 'ca_resident_ind', 'ny_resident_ind', 'tx_resident_ind',
           'il_resident_ind', 'az_resident_ind', 'oh_resident_ind',
           'ck_acct_ind', 'sv_acct_ind', 'cc_acct_ind',
           'ck_avg_bal', 'sv_avg_bal', 'cc_avg_bal', 'ck_avg_tran_amt',
           'sv_avg_tran_amt', 'cc_avg_tran_amt', 'q1_trans_cnt',
           'q2_trans_cnt', 'q3_trans_cnt', 'q4_trans_cnt']

df = pd.DataFrame(inputData, columns=columns)
#df = pd.DataFrame.from_records(inputData, exclude=['nRow', 'model'], columns=columns)
del inputData

df['cust_id'] = pd.to_numeric(df['cust_id'])

df['income'] = df['income'].apply(lambda x: "".join(x.split()))
df['income'] = pd.to_numeric(df['income'])

df['age'] = pd.to_numeric(df['age'])
df['tot_cust_years'] = pd.to_numeric(df['tot_cust_years'])
df['tot_children'] = pd.to_numeric(df['tot_children'])
df['female_ind'] = pd.to_numeric(df['female_ind'])
df['single_ind'] = pd.to_numeric(df['single_ind'])
df['married_ind'] = pd.to_numeric(df['married_ind'])
df['separated_ind'] = pd.to_numeric(df['separated_ind'])
df['ca_resident_ind'] = pd.to_numeric(df['ca_resident_ind'])
df['ny_resident_ind'] = pd.to_numeric(df['ny_resident_ind'])
df['tx_resident_ind'] = pd.to_numeric(df['tx_resident_ind'])
df['il_resident_ind'] = pd.to_numeric(df['il_resident_ind'])
df['az_resident_ind'] = pd.to_numeric(df['az_resident_ind'])
df['oh_resident_ind'] = pd.to_numeric(df['oh_resident_ind'])

df['ck_acct_ind'] = pd.to_numeric(df['ck_acct_ind'])
df['sv_acct_ind'] = pd.to_numeric(df['sv_acct_ind'])
df['cc_acct_ind'] = pd.to_numeric(df['cc_acct_ind'])

df['ck_avg_bal'] = df['ck_avg_bal'].apply(lambda x: "".join(x.split()))
df['ck_avg_bal'] = pd.to_numeric(df['ck_avg_bal'])
df['sv_avg_bal'] = df['sv_avg_bal'].apply(lambda x: "".join(x.split()))
df['sv_avg_bal'] = pd.to_numeric(df['sv_avg_bal'])
df['cc_avg_bal'] = df['cc_avg_bal'].apply(lambda x: "".join(x.split()))
df['cc_avg_bal'] = pd.to_numeric(df['cc_avg_bal'])

df['ck_avg_tran_amt'] = df['ck_avg_tran_amt'].apply(lambda x: "".join(x.split()))
df['ck_avg_tran_amt'] = pd.to_numeric(df['ck_avg_tran_amt'])
df['sv_avg_tran_amt'] = df['sv_avg_tran_amt'].apply(lambda x: "".join(x.split()))
df['sv_avg_tran_amt'] = pd.to_numeric(df['sv_avg_tran_amt'])
df['cc_avg_tran_amt'] = df['cc_avg_tran_amt'].apply(lambda x: "".join(x.split()))
df['cc_avg_tran_amt'] = pd.to_numeric(df['cc_avg_tran_amt'])

df['q1_trans_cnt'] = pd.to_numeric(df['q1_trans_cnt'])
df['q2_trans_cnt'] = pd.to_numeric(df['q2_trans_cnt'])
df['q3_trans_cnt'] = pd.to_numeric(df['q3_trans_cnt'])
df['q4_trans_cnt'] = pd.to_numeric(df['q4_trans_cnt'])

###
### Load model from input file
###
# Before you execute the following statement, replace <DBNAME> with the
# database name in the target Vantage Advanced SQL Engine where you have
# previously uploaded the model file to.
#
fIn = open('./RFmodel_py.out', 'rb')   # 'rb' for reading binary file
classifierPklB64 = fIn.read()
fIn.close()

# Decode and unserialize from imported format
classifierPkl = base64.b64decode(classifierPklB64)
classifier = pickle.loads(classifierPkl)

###
### Score the test table data with the given model
###
predictor_columns = ["income", "age", "tot_cust_years", "tot_children",
                     "female_ind", "single_ind", "married_ind", "separated_ind",
                     "ck_acct_ind", "sv_acct_ind", "ck_avg_bal", "sv_avg_bal",
                     "ck_avg_tran_amt", "sv_avg_tran_amt", "q1_trans_cnt",
                     "q2_trans_cnt", "q3_trans_cnt", "q4_trans_cnt"]

# Specify the rows to be scored by the model and call the predictor.
X_test = df[predictor_columns]
PredictionProba = classifier.predict_proba(X_test)

df = pd.concat([df, pd.DataFrame(data=PredictionProba, columns=['Prob0', 'Prob1'])], axis=1)

# Export results to Advanced SQL Engine through standard output in expected format.
for index, row in df.iterrows():
    print(row['cust_id'], delimiter,
          row['Prob0'], delimiter, row['Prob1'], delimiter, row['cc_acct_ind'])
