import sys, os, shutil
import datetime
import subprocess
import re
import dawsonpy
import itertools
import numpy as np

# Function to create final xml using template and  multiple_replace function
def update_xml(template_xml, updated_xml):

    replacements = {
        "%MODELX%"       : str.upper(para),
        "%MODEL%"        : str.upper(prod),
        "%MODELX_LABEL%" : para_label,
        "%MODEL_LABEL%"  : prod_label,
        "%modelx%"       : str.lower(para_label),
        "%model%"        : str.lower(prod_label),
        "%VDAY1%"        : vday1.strftime('%Y-%m-%d'),
        "%DD1%"          : vday1.strftime('%d'),
        "%MMM1%"         : vday1.strftime('%b'),
        "%YYYY1%"        : vday1.strftime('%Y'),
        "%VDAY2%"        : vday2.strftime('%Y-%m-%d'),
        "%DD2%"          : vday2.strftime('%d'),
        "%MMM2%"         : vday2.strftime('%b'),
        "%YYYY2%"        : vday2.strftime('%Y'),
        "%CC%"           : str(cycle), 
        "%F%"            : str(fhr*10000),
        "%FF%"           : str(fhr).zfill(2),
        "%PPP%"          : str(plev),
        "%VIS_THRESH%"   : str(vis_thresh),
        "%GGG%"          : str.upper(vx_mask[0]),
        "%REGION%"       : str.upper(regions[0]),
        "%region%"       : str.lower(regions[0]),
    }

    with open(template_xml) as f:
        new_text = dawsonpy.multiple_replace(replacements, f.read())

    with open(updated_xml, "w") as result:
        result.write(new_text)



# Function to run METviewer command
def run_metviewer(jobtype, xml):
    print('Running mv_'+jobtype+' on '+xml)

    if jobtype == 'scorecard':
        os.system(METVIEWER_DIR+'/mv_'+jobtype+'_on_aws.sh '+str.lower(os.environ['USER'])+' '+PLOT_DIR+' '+xml+' '+threshold_xml+' > '+outfile) 
    else:
        os.system(METVIEWER_DIR+'/mv_'+jobtype+'_on_aws.sh '+str.lower(os.environ['USER'])+' '+PLOT_DIR+' '+xml+' > '+outfile) 




# Set up 
now = datetime.datetime.utcnow()

#vday1 = now + datetime.timedelta(days=-32)    # for doing a past 32 days
#vday1 = datetime.datetime(2019,10,12,00,00)
#valid_end = now + datetime.timedelta(days=-2)
#valid_end_pcp = now + datetime.timedelta(days=-9)


# Get machine
machine, hostname = dawsonpy.get_machine()

# Set up working directories
if machine == 'WCOSS':
    VERIF_DIR = '/gpfs/'+hostname[0]+'d1/emc/meso/save/'+os.environ['USER']+'/CAM_verif'
    OUTPUT_DIR = '/gpfs/'+hostname[0]+'p2/ptmp/'+os.environ['USER']+'/cron.out'
elif machine == 'WCOSS_C':
    pass
elif machine == 'WCOSS_DELL_P3':
    DIR = '/gpfs/dell2/emc/verification/noscrub/'+os.environ['USER']+'/CAM_verif/AWS'
    WORK_DIR = '/gpfs/dell2/ptmp/'+os.environ['USER']+'/CAM_verif/RAPv5_HRRRv4'

METVIEWER_DIR = os.path.join(DIR,'METviewer_scripts')
TEMPLATE_DIR = os.path.join(DIR,'RAPv5_HRRRv4')

# Set up directory for run scripts
SCRIPT_DIR = os.path.join(WORK_DIR,'runscripts')
if os.path.exists(SCRIPT_DIR):
    shutil.rmtree(SCRIPT_DIR)
os.makedirs(SCRIPT_DIR)

# Set up directory for run scripts
OUTPUT_DIR = os.path.join(WORK_DIR,'metviewer.out')
if os.path.exists(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR)
os.makedirs(OUTPUT_DIR)

# Set up directory for saving plots
PLOT_DIR = os.path.join(WORK_DIR,'plots')
if not os.path.exists(PLOT_DIR):
    os.makedirs(PLOT_DIR)


# Define threshold XML file
threshold_xml = DIR+'/greenpurple_95-99.xml'

# dummy vars to fold for now
cycle = [0] 
fhr  = [0]
plev = [0]
ceil_thresh = [0]
vis_thresh = [0]
cape_thresh = [0]

cycles = np.arange(0,22,3)
plevs = [50,100,200,250,300,500,700,850,925,1000]
ceil_thresholds = [152,305,914,1520,3040] 
vis_thresholds = [805,1609,4828,8045,16090] 
cape_thresholds = [500,1000,1500,2000,3000,4000]
apcp_thresh = [.01,.10,.25,.50,.75,1.0,1.5,2.0,3.0,4.0]
apcp_thresh2 = [0.01,0.10,0.25,0.50,0.75,1,1.5,2,3,4]
apcp_thresh3 = ['0p01','0p10','0p25','0p50','0p75','1p0','1p5','2p0','3p0','4p0']
refl_abbrevs = ['refl','refc','refd1','retop']


# Loop through to generate scorecard xmls
prods = ['RAP','HRRR','RAPAK','HRRRAK']
paras = ['RAPX','HRRRX','RAPXAK','HRRRXAK']
prod_labels = ['RAPv4','HRRRv3','RAPv4','HRRRv3-AK']
para_labels = ['RAPv5','HRRRv4','RAPv5','HRRRv4-AK']

for i in xrange(2):
    prod = prods[i]
    para = paras[i]
    prod_label = prod_labels[i]
    para_label = para_labels[i]

    # Define scorecards to run for Alaska and CONUS
    if prod[-2:] == 'AK' and para[-2:] == 'AK':
        scorecards = ['sfc_fcstlead','upper_fcstlead','cv_fcstlead']
        regions = ['Alaska']
        vx_mask = ['']
    else:
        scorecards = ['sfc','upper','24hpcp','6hpcp','cape','refl','cv']
        scorecards = ['sfc_fcstlead','upper_fcstlead','cv_fcstlead','cape_fcstlead']
        scorecards = ['sfc_fcstlead','upper_fcstlead','24hpcp_fcstlead']
        scorecards = ['24hpcp_fcstlead','6hpcp_fcstlead']
        scorecards = ['cv_fcstlead']
        regions = ['CONUS']

    # Set verification start date for RAP and HRRR
    if str.upper(prod[0:3]) == 'RAP':
        vday1 = datetime.datetime(2019,10,15,00,00)
    elif str.upper(prod[0:4]) == 'HRRR':
        vday1 = datetime.datetime(2019,11,19,00,00)
    #   scorecards.extend(['cv_fcstlead','refc_fcstlead','retop_fcstlead'])


    for scorecard in scorecards:

        if scorecard[:6] == '24hpcp' or scorecard[:5] == '6hpcp':
            vx_mask = ['CONUS']
            vday2 = now + datetime.timedelta(days=-2)
        elif scorecard[:2] == 're':
            vx_mask = ['CONUS']
            vday2 = now + datetime.timedelta(days=-1)
        else:
            vx_mask = ['G236']
            vday2 = now + datetime.timedelta(days=-2)

        template_xml = TEMPLATE_DIR+'/scorecard_'+scorecard+'.xml'  
        updated_fname = str.lower(para_label)+'_'+str.lower(prod_label)+'_'+scorecard+'_scorecard'
        updated_xml = SCRIPT_DIR+'/'+updated_fname+'.xml'
        outfile = OUTPUT_DIR+'/'+updated_fname+'.out' 

        update_xml(template_xml, updated_xml)
#       run_metviewer('scorecard', updated_xml)

#exit()

# Loop through
regions = ['CONUS']
#plottypes = ['fcstlead','validhour']
#plottypes2 = ['vis','sfc_z0','sfc_z2','sfc_z10']


for i in xrange(2):
    prod = prods[i]
    para = paras[i]
    prod_label = prod_labels[i]
    para_label = para_labels[i]

    plottypes = []
    plottypes2 = ['24hpcp']

    # Set verification start date for RAP and HRRR
    if str.upper(prod[0:3]) == 'RAP':
        vday1 = datetime.datetime(2019,10,15,00,00)
        plottypes.extend(['rap_fcstthresh3'])
    elif str.upper(prod[0:4]) == 'HRRR':
        vday1 = datetime.datetime(2019,11,19,00,00)
        plottypes.extend(['hrrr_fcstthresh3'])
        plottypes2.extend(['refc'])

    plots = [n for n in itertools.product(plottypes,plottypes2)]

    for region in regions:
        for plot in plots:
            print plot
    
            if str.lower(plot[1]) in refl_abbrevs:
                vday2 = now + datetime.timedelta(days=-1)
            else:
                vday2 = now + datetime.timedelta(days=-2)

            # Loop over cycles for forecast lead plots
            if plot[0] == 'fcst_lead':
                template_xml = TEMPLATE_DIR+'/series_'+plot[0]+'_'+plot[1]+'.xml' 
                updated_xml = SCRIPT_DIR+'/series_'+plot[0]+'_'+plot[1]+'.xml'

                for cycle in cycles:  

                  # Loop through pressure levels              
                  if plot[1][0:5] == 'upper': 
                      for plev in plevs:
                          outfile = OUTPUT_DIR+'/series_'+str(cycle).zfill(2)+'z_'+plot[0]+'_'+plot[1]+'.out'
                          update_xml(template_xml, updated_xml)
                          run_metviewer('batch', updated_xml)

                  # Loop through ceiling thresholds
                  elif plot[1] == 'ceiling': 
                      for vis_thresh in ceiling_thresholds:
                          outfile = OUTPUT_DIR+'/series_'+str(cycle).zfill(2)+'z_'+plot[0]+'_'+plot[1]+'.out'
                          update_xml(template_xml, updated_xml)
                          run_metviewer('batch', updated_xml)

                  # Loop through visibility thresholds
                  elif plot[1] == 'vis': 
                      for vis_thresh in vis_thresholds:
                          outfile = OUTPUT_DIR+'/series_'+str(cycle).zfill(2)+'z_'+plot[0]+'_'+plot[1]+'.out'
                          update_xml(template_xml, updated_xml)
                          run_metviewer('batch', updated_xml)

                  # Loop through CAPE thresholds
                  elif plot[1] == 'cape': 
                      for cape_thresh in cape_thresholds:
                          outfile = OUTPUT_DIR+'/series_'+str(cycle).zfill(2)+'z_'+plot[0]+'_'+plot[1]+'.out'
                          update_xml(template_xml, updated_xml)
                          run_metviewer('batch', updated_xml)

                  # For surface stats              
                  else:
                      outfile = OUTPUT_DIR+'/series_'+str(cycle).zfill(2)+'z_'+plot[0]+'_'+plot[1]+'.out'
                      update_xml(template_xml, updated_xml)
                      run_metviewer('batch', updated_xml)


            # just group everything together for fcst thresh peformance diags
            elif plot[0][-11:] == 'fcstthresh3':
                template_xml = TEMPLATE_DIR+'/perf_'+plot[0]+'_'+plot[1]+'.xml' 
                updated_xml = SCRIPT_DIR+'/perf_'+plot[0]+'_'+plot[1]+'.xml'
  
                if str.upper(prod[0:3]) == 'RAP':
                #   fhrs = [27,33,39]
                    fhrs = [27]
                elif str.upper(prod[0:4]) == 'HRRR':
                #   fhrs = [24,30,36]
                    fhrs = [24]

                for fhr in fhrs:
                    outfile = OUTPUT_DIR+'/perf_f'+str(fhr).zfill(2)+'_'+plot[0]+'_'+plot[1]+'.out'
                    update_xml(template_xml, updated_xml)
                    run_metviewer('batch', updated_xml)
          


exit()


# Loop through to generate performance xmls
domains = ['CONUS','Alaska','East','West']

for region in regions:
    if region == 'Alaska':
        diags = ['ceiling','vis']
    else:
        diags = ['ceiling','vis','cape','24hpcp','refc','retop']

