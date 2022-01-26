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

def prYellow(skk): print(f"\033[93m {skk}\033[00m") 
def prBlue(sk): print(f"\033[94m {sk}\033[00m") 
def prGreen(ss): print(f"\033[92m {ss}\033[00m") 
def prRed(ss): print(f"\033[91m {ss}\033[00m") 

path_script = '/home/giaco/Scrivania/PROJECT_BiomedicalImageProcessing'
path_subjects = '/home/giaco/Scrivania/PROJECT_BiomedicalImageProcessing/FD'

if not os.path.exists('/home/giaco/Scrivania/PROJECT_BiomedicalImageProcessing/Analysis'):
    os.makedirs('/home/giaco/Scrivania/PROJECT_BiomedicalImageProcessing/Analysis')

path_g = '/home/giaco/Scrivania/PROJECT_BiomedicalImageProcessing/Analysis'

subj_list1 = [f for f in os.listdir(path_subjects) if not f.startswith('.')]  #list of the folder in path_subjects

subj_list1.sort()
prGreen(subj_list1)

workbook_metrics = xlsxwriter.Workbook(os.path.join(path_g, 'NetworkMetrics_FINAL.xlsx')) #Initialize the excel file
worksheet_metrics = workbook_metrics.add_worksheet("ACT_Metrics")  #Initialize the excel worksheet

worksheet_metrics_sift = workbook_metrics.add_worksheet("SIFT_Metrics")  #Initialize the excel worksheet
row = 1

for subj in subj_list1:

    if not os.path.exists(os.path.join(path_g, subj)):
        os.makedirs(os.path.join(path_g, subj))

    path_Analysis = os.path.join(path_g, subj)

    path_s = os.path.join(path_subjects, subj)


    # PART 1: DWI PROCESSING
    #DENOISING
    prRed("PART 1: DWI PROCESSING")
    prBlue("DENOISING")
    if not os.path.exists(path_Analysis + '/DWI'):
        os.makedirs(path_Analysis + '/DWI')
        
    path_DWI = path_Analysis + '/DWI'

    now = datetime.datetime.now()
    
    cmd = 'dwidenoise -mask ' + path_s + '/DTI/' + subj + '_data_mask.nii.gz ' + path_s + '/DTI/' + subj + '_data.nii.gz ' + path_DWI + '/' + subj + '_data_denoise.nii.gz -force'
    os.system(cmd)

    ######################################################
    # PART 2: CSD reconstruction
    prRed("PART 2: CSD reconstruction")
    ###### Create the folder that will contain the output of the CSD reconstructions:
    if not os.path.exists(path_Analysis + '/CSD'):
        os.makedirs(path_Analysis + '/CSD')

    path_CSD = path_Analysis + '/CSD'

    cmd = 'dwi2mask ' + path_DWI + '/' + subj + '_data_denoise.nii.gz ' + path_DWI + '/mask_brain.nii.gz -fslgrad ' + path_s + '/DTI/' + subj + '_bvecs.txt ' + path_s + '/DTI/' + subj + '_bvals.txt -force'
    os.system(cmd)
        
    # define the desired Spherical Harmonics order
    lmax = 6

    # estimate the response function (i.e., PSF)
    cmd = 'dwi2response tournier -lmax 6 ' + path_DWI + '/' + subj + '_data_denoise.nii.gz ' + path_CSD + '/response.txt -fslgrad ' + path_s + '/DTI/' + subj + '_bvecs.txt ' + path_s + '/DTI/' + subj + '_bvals.txt -mask ' + path_DWI + '/mask_brain.nii.gz -force'
    os.system(cmd)

    #Perform the actual deconvolution
    cmd = 'dwi2fod csd -lmax 6 ' + path_DWI + '/' + subj + '_data_denoise.nii.gz ' + path_CSD + '/response.txt ' + path_CSD + '/FODsh.mif -fslgrad ' + path_s + '/DTI/' + subj + '_bvecs.txt ' + path_s + '/DTI/' + subj + '_bvals.txt -mask ' + path_DWI + '/mask_brain.nii.gz -force'
    os.system(cmd)

    ######################################################
    # PART 3: 5TT
    prRed("PART 3: 5TT")

    if not os.path.exists(path_Analysis + '/5TT'):
        os.makedirs(path_Analysis + '/5TT')

    path_5TT = path_Analysis + '/5TT'

    print(path_5TT)
    os.chdir(path_5TT)
    cmd = 'pwd'
    os.system(cmd)

    cmd = '5ttgen fsl ' + path_s + '/T1/T1_brain.nii.gz ' + path_5TT + '/5TT.mif -premasked -nocleanup -force'
    os.system(cmd)

    cmd = 'mrconvert ' + path_5TT + '/5ttgen-tmp*/wm.mif ' + path_5TT + '/WM.nii.gz'
    os.system(cmd) 

    cmd = '5tt2gmwmi ' + path_5TT + '/5TT.mif ' + path_5TT + '/5TT_mask.mif -force'
    os.system(cmd)

    cmd = 'mrconvert ' + path_5TT + '/5TT.mif ' + path_5TT + '/5TT.nii.gz -force'
    os.system(cmd)

    cmd = 'mrconvert ' + path_5TT + '/5TT_mask.mif ' + path_5TT + '/5TT_mask.nii.gz -force'
    os.system(cmd)

    os.chdir(path_script)
    cmd = 'pwd'
    os.system(cmd)

    ######################################################
    # PART 4: REGISTRATION
    prRed("PART 4: REGISTRATION")
    if not os.path.exists(path_Analysis + '/T1_to_b0_registration'):
        os.makedirs(path_Analysis + '/T1_to_b0_registration')

    path_REG = path_Analysis + '/T1_to_b0_registration'

    cmd = 'dwiextract -bzero ' + path_DWI + '/' + subj + '_data_denoise.nii.gz ' + path_DWI + '/' + subj + '_denoise_b0.nii.gz -fslgrad ' + path_s + '/DTI/' + subj + '_bvecs.txt ' + path_s + '/DTI/' + subj + '_bvals.txt -force'
    os.system(cmd)

    cmd = 'fslmaths ' + path_DWI + '/' + subj + '_denoise_b0.nii.gz -Tmean ' + path_DWI + '/' + subj + '_denoise_b0.nii.gz'
    os.system(cmd)


    cmd = 'flirt -in ' + path_DWI + '/' + subj + '_denoise_b0.nii.gz -ref ' + path_s + '/T1/T1_brain.nii.gz -dof 6 -omat ' + path_REG + '/tmp_dwi-t1.mat'
    os.system(cmd)

    schedule = '/usr/local/fsl/etc/flirtsch'
    cmd = 'flirt -in ' + path_DWI + '/' + subj + '_denoise_b0.nii.gz -ref ' + path_s + '/T1/T1_brain.nii.gz -dof 6 -cost bbr -wmseg ' + path_5TT + '/WM.nii.gz -init ' + path_REG + '/tmp_dwi-t1.mat -omat ' + path_REG + '/tmp_prereg_dwi-t1.mat -out ' + path_REG + '/Reg1.nii.gz -schedule ' + schedule + '/bbr.sch'
    os.system(cmd)

    cmd = 'convert_xfm -omat ' + path_REG + '/tmp_inverse.mat -inverse ' + path_REG + '/tmp_prereg_dwi-t1.mat'
    os.system(cmd)

    cmd = 'flirt -applyxfm -init ' + path_REG + '/tmp_inverse.mat -in ' + path_s + '/T1/T1_brain.nii.gz -ref ' + path_DWI + '/' + subj + '_denoise_b0.nii.gz -out ' + path_REG + '/Reg_Final.nii.gz'
    os.system(cmd)

    cmd = 'transformconvert ' + path_REG + '/tmp_prereg_dwi-t1.mat ' + path_DWI + '/' + subj + '_denoise_b0.nii.gz ' + path_s + '/T1/T1_brain.nii.gz flirt_import ' + path_REG + '/mrtrix_final_matrix.txt -force'
    os.system(cmd)

    cmd = 'mrtransform ' + path_5TT + '/5TT.nii.gz ' + path_5TT + '/5tt_reg.nii.gz -linear ' + path_REG + '/mrtrix_final_matrix.txt -inverse -force'
    os.system(cmd)

    cmd = 'mrtransform ' + path_5TT + '/5TT_mask.nii.gz ' + path_5TT + '/5tt_mask_reg.nii.gz -linear ' + path_REG + '/mrtrix_final_matrix.txt -inverse -force'
    os.system(cmd)
    
    ######################################################
    # PART 5: TRACTOGRAPHY
    prRed("PART 5: TRACTOGRAPHY")

    if not os.path.exists(path_Analysis + '/Tractography'):
        os.makedirs(path_Analysis + '/Tractography')

    path_Tractography = path_Analysis + '/Tractography'

    prBlue("ACT")
    cmd = 'tckgen ' + path_CSD + '/FODsh.mif ' + path_Tractography + '/fibers_prob_wholebrain.tck -act ' + path_5TT + '/5tt_reg.nii.gz -algorithm iFOD2 -select 1000000 -step 0.5 -angle 45 -crop_at_gmwmi -seed_gmwmi ' + path_5TT + '/5tt_mask_reg.nii.gz -force'
    os.system(cmd)

    prBlue("SIFT2")
    cmd = 'tcksift2 ' + path_Tractography + '/fibers_prob_wholebrain.tck ' + path_CSD + '/FODsh.mif ' + path_Tractography + '/fibers_prob_wholebrain_sift2.txt' #-act {path_5TT}/5TT.nii.gz
    os.system(cmd)

    ######################################################
    # PART 6: CONNECTOME
    prRed("PART 6: CONNECTOME")
    if not os.path.exists(path_Analysis + '/Connectome'):
        os.makedirs(path_Analysis + '/Connectome')

    path_Connectome = path_Analysis + '/Connectome'

    cmd = 'labelconvert ' + path_s + '/T1/aparc+aseg.nii.gz /usr/local/freesurfer/FreeSurferColorLUT.txt /home/giaco/mrtrix3/share/mrtrix3/labelconvert/fs_default.txt ' + path_Connectome + '/nodes.nii.gz -force'
    os.system(cmd)

    cmd = 'labelsgmfix ' + path_Connectome + '/nodes.nii.gz ' + path_s + '/T1/T1_brain.nii.gz /home/giaco/mrtrix3/share/mrtrix3/labelconvert/fs_default.txt ' + path_Connectome + '/nodes_fixSGM.nii.gz -sgm_amyg_hipp -premasked -force'
    os.system(cmd)

    cmd = 'flirt -interp nearestneighbour -applyxfm -init ' + path_REG + '/tmp_inverse.mat -in ' + path_Connectome + '/nodes_fixSGM.nii.gz -ref ' + path_DWI + '/' + subj + '_denoise_b0.nii.gz -out ' + path_REG + '/aparc+aseg_to_b0.nii.gz'
    os.system(cmd)

    #ACT
    cmd = 'tck2connectome -symmetric ' + path_Tractography + '/fibers_prob_wholebrain.tck ' + path_REG + '/aparc+aseg_to_b0.nii.gz ' + path_Connectome + '/my_connectome.csv -assignment_radial_search 2 -out_assignments ' + path_Connectome + '/my_streamlines_assignment.txt -force'
    os.system(cmd)

    #SIFT2
    cmd = 'tck2connectome -symmetric ' + path_Tractography + '/fibers_prob_wholebrain.tck ' + path_REG + '/aparc+aseg_to_b0.nii.gz ' + path_Connectome + '/my_connectome_sift2.csv -assignment_radial_search 2 -out_assignments ' + path_Connectome + '/my_streamlines_assignment_sift2.txt -tck_weights_in  ' + path_Tractography + '/fibers_prob_wholebrain_sift2.txt -force'
    os.system(cmd)

    ######################################################
    # PART 7: METRICS
    prRed("PART 7: METRICS")
    subj_connectome_csv = path_Connectome + '/my_connectome.csv'
    subj_connectome = np.loadtxt(subj_connectome_csv, delimiter = ',')

    subj_connectome_sift_csv = path_Connectome + '/my_connectome_sift2.csv'
    subj_connectome_sift = np.loadtxt(subj_connectome_sift_csv, delimiter = ',')
    
    #ACT
    np.fill_diagonal(subj_connectome, 0)

    D = bct.density_und(subj_connectome)
    E = bct.efficiency_wei(subj_connectome, local=False)
    M = bct.modularity_und(subj_connectome,gamma=1,kci=None)
    C = np.mean(bct.clustering_coef_wu(subj_connectome))

    #SIFT2
    np.fill_diagonal(subj_connectome_sift, 0)

    Ds = bct.density_und(subj_connectome_sift)
    Es = bct.efficiency_wei(subj_connectome_sift, local=False)
    Ms = bct.modularity_und(subj_connectome_sift,gamma=1,kci=None)
    Cs = np.mean(bct.clustering_coef_wu(subj_connectome_sift))

    if 'HC_' in subj:
        l = 1
    if 'FD_' in subj:
        l = 2

    # WRITE FILE EXCEL
    # write operation perform 
    worksheet_metrics.write(0, 0, 'Subj') #row, col
    worksheet_metrics.write(0, 1, 'Density') 
    worksheet_metrics.write(0, 2, 'Efficiency') 
    worksheet_metrics.write(0, 3, 'Modularity')
    worksheet_metrics.write(0, 4, 'Average Clustering')
    worksheet_metrics.write(0, 5, 'Group') 
    worksheet_metrics.write(row, 0, subj) 
    worksheet_metrics.write(row, 1, D[0]) 
    worksheet_metrics.write(row, 2, E)
    worksheet_metrics.write(row, 3, M[1])
    worksheet_metrics.write(row, 4, C)
    worksheet_metrics.write(row, 5, l)

    worksheet_metrics_sift.write(0, 0, 'Subj') #row, col
    worksheet_metrics_sift.write(0, 1, 'Density') 
    worksheet_metrics_sift.write(0, 2, 'Efficiency') 
    worksheet_metrics_sift.write(0, 3, 'Modularity')
    worksheet_metrics_sift.write(0, 4, 'Average Clustering')
    worksheet_metrics_sift.write(0, 5, 'Group') 
    worksheet_metrics_sift.write(row, 0, subj) 
    worksheet_metrics_sift.write(row, 1, Ds[0]) 
    worksheet_metrics_sift.write(row, 2, Es)
    worksheet_metrics_sift.write(row, 3, Ms[1])
    worksheet_metrics_sift.write(row, 4, Cs)
    worksheet_metrics_sift.write(row, 5, l)

    row += 1

#end for
workbook_metrics.close()
