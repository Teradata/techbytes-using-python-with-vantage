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
# File: stoRFFitMM.py
# ##############################################################################
#
# This TechBytes demo utilizes a use case to predict per state code partition
# the propensity of a financial services customer base to open a credit card
# account.
#
# The present file is the Python model training script to be used with the
# SCRIPT table operator, as described in the use case "Micromodeling: Scaled,
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
df['state_code'] = df['state_code'].apply(lambda x: x.replace('"', ''))
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
### Perform classification model fitting
###

predictor_columns = ["income", "age", "tot_cust_years", "tot_children",
                     "female_ind", "single_ind", "married_ind", "separated_ind",
                     "ck_acct_ind", "sv_acct_ind", "ck_avg_bal", "sv_avg_bal",
                     "ck_avg_tran_amt", "sv_avg_tran_amt", "q1_trans_cnt",
                     "q2_trans_cnt", "q3_trans_cnt", "q4_trans_cnt"]
# For the classifier, specify the equivalent parameter values used in the R example:
# ntree: n_estimators=500, mtry: max_features=5, nodesize: min_samples_leaf=1 (default; skipped)
classifier = RandomForestClassifier(n_estimators=500, max_features=5, random_state=0)
X = df[predictor_columns]
y = df["cc_acct_ind"]
classifier = classifier.fit(X, y)

# Serialize the model for export
modelSer = pickle.dumps(classifier)
modelSerB64 = base64.b64encode(modelSer)

###
### Send the state code and fitted model as output from the present AMP.
###

# Export results to Advanced SQL Engine through std output in expected format.
print(df.iloc[0,9], delimiter, modelSerB64)
