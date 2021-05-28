## Teradata TechBytes series: Using Python with Teradata Vantage

This bundle contains v.2.0 of the Python code for the 4-part demo of the TechBytes series "Using Python with Teradata Vantage".

### The TechBytes series "Using Python with Teradata Vantage"

Teradata TechBytes are offering a 4-part set of videos about Python in Vantage on the Teradata YouTube channel. This series demonstrates the Python capabilities in Teradata Vantage, and ways to use Python for Client and In-database analytics on a target Vantage system through the Teradata Client Package for Python **teradataml**. This TechBytes series utilizes a core use case to predict the propensity of a financial services customer base to open a credit card account, and comprises of the following parts:

* Part 1 has an Introduction, information about connecting to a Vantage Advanced SQL Engine Database with **teradataml**, and exhibits some basic operations.
* Part 2 demonstrates Data Exploration and Transformations, and how to build an Analytic Data Set (ADS).
* Part 3 demonstrates Modeling with Vantage Analytic Functions and the Model Cataloging feature.
* Part 4 In-Database scripting with the SCRIPT Table Operator and the **teradataml** Map functions.

### The Python TechBytes demo

The present bundle is a demo that offers the entire code for all parts of the "Using Python with Teradata Vantage" TechBytes series. The code resides in the Python notebook files, and has been richly annotated with explanatory comments to guide you through each step. In addition, the package contains in a separate folder all the necessary input data that are needed for the demo. To reproduce the analyses with the present bundle, the following are needed:

* A Python interpreter (minimum supported version is 3.5.0) installed on a client machine, and access to a Python repository to install add-on libraries.
* The Teradata Package for Python **teradataml**, which is freely available for installation at the [PyPI](https://pypi.org/project/teradataml) repository.
* Access to a Teradata Vantage system that to the very minimum carries the Advanced SQL Engine Database 16.20.16.01 or later versions.
   + To execute the demo Part 3 in its entirety, the target Vantage system must also feature a Machine Learning Engine component, too.
   + To execute the demo Part 4, the target Advanced SQL Engine must be equipped with the "teradata-python" and "teradata-python-addons" packages.
* A SQL interpreter, such as Teradata Studio that is available through the website https://downloads.teradata.com.
Additional details and any case-specific requirements are provided as needed in the demo files.

### Table of Contents

The present package comprises of the following folders and files.

* README-TBv2_Py.txt
* TBv2_Py-1-Intro-Connect.html
* TBv2_Py-1-Intro-Connect.ipynb
* TBv2_Py-1-Intro-Connect.pptx
* TBv2_Py-2-Explore-Transform-ADS.html
* TBv2_Py-2-Explore-Transform-ADS.ipynb
* TBv2_Py-2-Explore-Transform-ADS.pptx
* TBv2_Py-3-Modeling-Cataloging.html
* TBv2_Py-3-Modeling-Cataloging.ipynb
* TBv2_Py-3-Modeling-Cataloging.pptx
* TBv2_Py-4-In_DB_Scripting.html
* TBv2_Py-4-In_DB_Scripting.ipynb
* TBv2_Py-4-In_DB_Scripting.pptx
* license.txt
* Inputs/
    + Data/
        + Accounts.csv
        + Accounts.fastload
        + Customer.csv
        + Customer.fastload
        + Customer2.fastload
        + Transactions.csv.zip
        + Transactions.fastload
    + Plots/
        + DemoData.png
    + stoRFFitMM.py
    + stoRFScore.py
    + stoRFScoreMM.py
    + stoRFScoreSB.py
    + stoSandboxTestData.csv

### Changelog

<table>
  <tr>
    <th>Version</th>
    <th>Date</th>
    <th>Notes</th>
 </tr>
 <tr>
   <td>2.0</td>
   <td>May 2021</td>
   <td>Overhauled version for Python</td>
  </tr>
  <tr>
    <td>1.1</td>
    <td>April 2020</td>
    <td>Revised code demos with updated libraries features</td>
  </tr>
  <tr>
    <td>1.0</td>
    <td>October 2019</td>
    <td>First release (as "R and Python TechBytes")</td>
  </tr>
</table>
