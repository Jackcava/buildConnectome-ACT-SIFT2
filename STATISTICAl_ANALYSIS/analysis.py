#!/usr/bin/env python

import nibabel as nib # manipulate NIFTI images
import pandas as pd
import numpy as np # manipulate data arrays like in MATLAB
import seaborn as sns
from scipy import stats
import os # interact with the terminal
import shutil #bash utils
import subprocess
import errno #error handling
import datetime
import timeit
import bct
from pathlib import Path
import matplotlib.pyplot as plt # plot images and charts
import xlsxwriter 
from scipy.stats import median_test
#import openpyxl

def prYellow(skk): print(f"\033[93m {skk}\033[00m") 
def prBlue(sk): print(f"\033[94m {sk}\033[00m") 
def prGreen(ss): print(f"\033[92m {ss}\033[00m") 
def prRed(ss): print(f"\033[91m {ss}\033[00m") 

prGreen('________STATISTICAL ANALYSIS________')

gpath =  "/home/giaco/Scrivania/PROJECT_BiomedicalImageProcessing/STATISTICAL_ANALYSIS"

#Read the file excel as a dataframe
dataframe = os.path.join(gpath,  'NetworkMetrics_FINAL.xlsx')
data1 = pd.read_excel(dataframe,sheet_name='ACT_Metrics') #['ACT_Metrics','SIFT_Metrics'])
data2 = pd.read_excel(dataframe,sheet_name='SIFT_Metrics')

###############################################################
## FIG. 1 ##
#Set the palette for the violinplot
sns.set_theme(style="ticks", palette="bright")

#Plot the violinplot using seaborn
prBlue("Close the plot to procede")

plt.figure(num='Density ACT vs SIFT2', figsize=(12, 6))

plt.subplot(121)
sns.violinplot(x="Group", y="Density", palette=["g", "r"], data=data1)
plt.title('ACT',fontsize=20)

plt.subplot(122)
sns.violinplot(x="Group", y="Density", palette=["g", "r"], data=data2)
plt.title('SIFT2',fontsize=20)

#plt.xlabel('1 = HC , 2 = FD',fontsize=10)
plt.show()

#Perform the t-test
t1 = stats.ttest_ind(data1['Density'], data1['Group'])
t2 = stats.ttest_ind(data2['Density'], data2['Group'])
# median = median_test(data1['Density'], data1['Group'])
# print(median)
prYellow(f"ACT -> Density T-Test result: {t1}")
prYellow(f"SIFT2 -> Density T-Test result: {t2}")

###############################################################
## FIG.2 ##
#Set the palette for the violinplot
sns.set_theme(style="ticks", palette="bright")

#Plot the violinplot using seaborn
prBlue("Close the plot to procede")

plt.figure(num='Efficiency ACT vs SIFT2', figsize=(12, 6))

plt.subplot(121)
sns.violinplot(x="Group", y="Efficiency", palette=["g", "r"], data=data1)
plt.title('ACT',fontsize=20)

plt.subplot(122)
sns.violinplot(x="Group", y="Efficiency", palette=["g", "r"], data=data2)
plt.title('SIFT2',fontsize=20)

plt.show()

#Perform the t-test
t1 = stats.ttest_ind(data1['Efficiency'], data1['Group'])
t2 = stats.ttest_ind(data2['Efficiency'], data2['Group'])

prYellow(f"ACT -> Efficiency T-Test result: {t1}")
prYellow(f"SIFT2 -> Efficiency T-Test result: {t2}")

###############################################################
## FIG.3 ##
#Set the palette for the violinplot
sns.set_theme(style="ticks", palette="bright")

#Plot the violinplot using seaborn
prBlue("Close the plot to procede")

plt.figure(num='Modularity ACT vs SIFT2', figsize=(12, 6))

plt.subplot(121)
sns.violinplot(x="Group", y="Modularity", palette=["g", "r"], data=data1)
plt.title('ACT',fontsize=20)

plt.subplot(122)
sns.violinplot(x="Group", y="Modularity", palette=["g", "r"], data=data2)
plt.title('SIFT2',fontsize=20)

plt.show()

#Perform the t-test
t1 = stats.ttest_ind(data1['Modularity'], data1['Group'])
t2 = stats.ttest_ind(data2['Modularity'], data2['Group'])

prYellow(f"ACT -> Modularity T-Test result: {t1}")
prYellow(f"SIFT2 -> Modularity T-Test result: {t2}")

