import sys, os, shutil
import datetime
import subprocess
import re
import dawsonpy
import itertools
import numpy as np

# Function to create final xml using template and  multiple_replace function
def update_xml(jobtype,template_xml, updated_xml):

    replacements = {

        "%VERF_JOB%"     : str.lower(verf_job),
        "%MV_DATABASE%"  : str.lower(mv_database),

        # subs for model names/labels in scorecard scripts
        "%MODELX%"       : str.upper(para),
        "%MODEL%"        : str.upper(prod),
        "%MODELX_LABEL%" : para_label,
        "%MODEL_LABEL%"  : prod_label,
        "%modelx%"       : str.lower(para_label),
        "%model%"        : str.lower(prod_label),

        "%TIME_PERIOD%"  : str.lower(time_period),
        "%VDAY1%"        : vday1.strftime('%Y-%m-%d'),
        "%DD1%"          : vday1.strftime('%d'),
        "%MMM1%"         : vday1.strftime('%b'),
        "%YYYY1%"        : vday1.strftime('%Y'),
        "%VDAY2%"        : vday2.strftime('%Y-%m-%d'),
        "%DD2%"          : vday2.strftime('%d'),
        "%MMM2%"         : vday2.strftime('%b'),
        "%YYYY2%"        : vday2.strftime('%Y'),

        "%CC%"           : str(cycle).zfill(2), 
        "%F%"            : str(fhr*10000),
        "%FF%"           : str(fhr).zfill(2),

        "%PPP%"          : str(plev),
        "%THRESH%"       : str(thresh),
        "%THRESH2%"      : str(imperial_thresh),
        "%GGG%"          : str.upper(vx_mask),
        "%REGION%"       : region,
        "%region%"       : str.lower(region),

        # subs for plot settings in batch scripts with one line per model
        "%CI_LIST%"      : ci_list,
        "%SIGNIF_LIST%"  : signif_list,
        "%DISP_LIST%"    : disp_list,
        "%COLORS_LIST%"  : colors_list,
        "%PCH_LIST%"     : pch_list,
        "%TYPE_LIST%"    : type_list,
        "%LTY_LIST%"     : lty_list,
        "%LWD_LIST%"     : lwd_list,
        "%CON_LIST%"     : con_list,
        "%ORDER_LIST%"   : order_list,
        "%LEGEND_LIST%"  : legend_list,

        # subs for plot settings in batch scripts with two lines per model
        "%CI_LIST2%"     : ci_list2,
        "%SIGNIF_LIST2%" : signif_list2,
        "%DISP_LIST2%"   : disp_list2,
        "%COLORS_LIST2%" : colors_list2,
        "%PCH_LIST2%"    : pch_list2,
        "%TYPE_LIST2%"   : type_list2,
        "%LTY_LIST2%"    : lty_list2,
        "%LWD_LIST2%"    : lwd_list2,
        "%CON_LIST2%"    : con_list2,
        "%ORDER_LIST2%"  : order_list2,
        "%LEGEND_LIST2%" : legend_list2,

        # subs for plot settings in batch scripts with two lines (vector scores) per model
        "%PCH_LIST3%"    : pch_list3,
        "%LEGEND_LIST3%" : legend_list3,
    }

    # Copy template to verf_job directory
    os.system('cp '+template_xml+' '+temp_xml)

    # Open template in verf_job directory and replace using dictionary keys above 
    with open(temp_xml) as f:
        new_text = dawsonpy.multiple_replace(replacements, f.read())
        f.close()

    # Write updated XML
    with open(updated_xml, "w") as result:
        result.write(new_text)
        result.close()

    # Insert list of model values for batch jobs
    if jobtype == 'batch':
        with open(updated_xml,"r") as f:
            data = f.readlines()
            f.close()

        insert_ind = data.index('            <field name=\"model\">\n')
        data.insert(insert_ind+1,model_list)

        f = open(updated_xml,"w")
        data = "".join(data)
        f.write(data)
        f.close() 



# Function to specify METviewer database and most recent verification date
def update_db_vday2(plottype):
    if plottype == '24hpcp' or plottype == '6hpcp':
        mv_database = 'mv_ylin_metplus'
        vday2 = now + datetime.timedelta(days=-2)
    elif plottype[:2] == 're':
         mv_database = 'mv_'
         vday2 = now + datetime.timedelta(days=-1)
    else:
         mv_database = 'mv_emc_g2o_met'
         vday2 = now + datetime.timedelta(days=-2)

    return mv_database, vday2


# Function to specify METviewer database and most recent verification date
def update_vx_mask(jobtype,region):
    if str.upper(region) == 'CONUS':
        if mv_database == 'mv_emc_g2o_met' and jobtype == 'batch':
            vx_mask = 'APL,GMC,GRB,LMV,MDW,NEC,NMT,NPL,NWC,SEC,SMT,SPL,SWC,SWD'
        elif mv_database == 'mv_emc_g2o_met' and jobtype == 'scorecard':
            vx_mask = 'FULL'
        else:
            vx_mask = 'CONUS'
    elif str.upper(region) == 'EAST':
        vx_mask = 'APL,GMC,LMV,MDW,NEC,SEC'
    elif str.upper(region) == 'PLAINS':
        vx_mask = 'NPL,SPL'
    elif str.upper(region) == 'WEST':
        vx_mask = 'GRB,NMT,NWC,SMT,SWC,SWD'

    return vx_mask



# Function to run METviewer command
def run_metviewer(jobtype, xml):
    print('Running mv_'+jobtype+' on '+xml)

    if jobtype == 'scorecard':
#       os.system(METVIEWER_DIR+'/mv_'+jobtype+'_on_aws.sh '+str.lower(os.environ['USER'])+' '+PLOT_DIR+' '+xml+' '+threshold_xml+' > '+outfile) 
        pass
    else:
        os.system(METVIEWER_DIR+'/mv_'+jobtype+'_on_aws.sh '+str.lower(os.environ['USER'])+' '+PLOT_DIR+' '+xml+' > '+outfile) 
#       pass



##################################################
# Begin working 
now = datetime.datetime.utcnow()


#Determine verification job
try:
    verf_job = str(sys.argv[1])
except IndexError:
    raise IndexError, 'need to define verification job (e.g., FV3CAM, MESO, CAM, NAM, RAP_HRRR)'

#Determine verification period
try:
    verf_period = str(sys.argv[2])
except IndexError:
    verf_period = None

# Default to past 30 days if
if verf_period is None:
    verf_period = 'past30days'
    print('Defaulting to generate graphics for past 30 days')

if str.lower(verf_period) == 'past30days':
    vday1 = now + datetime.timedelta(days=-32)    # for doing a past 32 days
    time_period = 'valid'
elif str.lower(verf_period) == 'cur_exp':
    vday1 = datetime.datetime(2019,11,22,00,00)
    time_period = 'init'

# Default with two-day lag. Will adjust later based on verification if needed 
valid_end = now + datetime.timedelta(days=-2)





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
    WORK_DIR = '/gpfs/dell2/ptmp/'+os.environ['USER']+'/CAM_verif/'+verf_job+'/'+verf_period

METVIEWER_DIR = os.path.join(DIR,'METviewer_scripts')
TEMPLATE_DIR = os.path.join(DIR,'templates')

# Set up directory for temporary XML scripts
TEMP_DIR = os.path.join(WORK_DIR,'temp')
if os.path.exists(TEMP_DIR):
    shutil.rmtree(TEMP_DIR)
os.makedirs(TEMP_DIR)

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
if os.path.exists(PLOT_DIR):
    shutil.rmtree(PLOT_DIR)
os.makedirs(PLOT_DIR)


# Define threshold XML file
threshold_xml = TEMPLATE_DIR+'/greenpurple_95-99.xml'


# Define thresholds, levels, etc. for series plots and performance diagrams
plevs = [50,100,200,250,300,500,700,850,925,1000]
ceil_thresholds = [152,305,914,1520,3040] 
us_ceil_thresholds = [500,1000,3000,5000,10000] 
vis_thresholds = [805,1609,4828,8045,16090] 
us_vis_thresholds = [0.5,1,3,5,10] 
cape_thresholds = [500,1000,1500,2000,3000,4000]

# dummy vars to hold for now
cycle = 0 
fhr  = 0
plev = plevs[0] 
thresh = ceil_thresholds[0] 
imperial_thresh = ceil_thresholds[0] 
prod = 'dummy'
para = 'dummy'
prod_label = 'dummy'
para_label = 'dummy'



# Specs for FV3-CAM graphics
if str.upper(verf_job) == 'FV3CAM':
    cycles = np.arange(0,13,12)
    fhrs = np.arange(0,61,6)

    model_list = '                <val>CONUSNEST</val>\n'\
                 '                <val>CONUSNMMB</val>\n'\
                 '                <val>FV3SAR</val>\n'\
                 '                <val>FV3SARX</val>\n'\
                 '                <val>GFS</val>\n'\
                 '                <val>HRRR</val>\n'
    prods = ['FV3SAR','HRRR','CONUSNEST','CONUSNMMB']
    paras = ['FV3SAR','FV3SARX']
    prod_labels = ['FV3SAR','HRRR','NAM-Nest','HiResW-NMMB']
    para_labels = ['FV3SAR','FV3SARX']

    ci_list     = 'c(\"none\",\"none\",\"none\",\"none\",\"none\",\"none\")'
    signif_list = 'c(FALSE,FALSE,FALSE,FALSE,FALSE,FALSE)'
    disp_list   = 'c(TRUE,TRUE,TRUE,TRUE,TRUE,TRUE)'
    colors_list = 'c(\"#0000ffFF\",\"#12C115\",\"#008000\",\"#008000\",\"#000000\",\"#ff0000FF\")'
    pch_list    = 'c(20,20,20,20,20,20)'
  # type_list   = 'c(\"o\",\"o\",\"o\",\"o\",\"o\",\"o\")'
    type_list   = 'c(\"l\",\"l\",\"l\",\"l\",\"l\",\"l\")'
    lty_list    = 'c(1,1,1,2,1,1)'
    lwd_list    = 'c(2.5,2.5,2.5,2.5,2.5,2.5)'
    con_list    = 'c(1,1,1,1,1,1)'
    order_list  = 'c(1,2,3,4,5,6)'
    legend_list = 'c(\"NAM Nest\",\"HiResW NMMB\",\"FV3SAR\",\"FV3SAR-X\",\"GFS\",\"HRRR\")'

    ci_list2     = 'c(\"none\",\"none\",\"none\",\"none\",\"none\",\"none\",\"none\",\"none\",\"none\",\"none\",\"none\",\"none\")'
    signif_list2 = 'c(FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE)'
    disp_list2   = 'c(TRUE,TRUE,TRUE,TRUE,TRUE,TRUE,TRUE,TRUE,TRUE,TRUE,TRUE,TRUE)'
    colors_list2 = 'c(\"#0000ffFF\",\"#12C115\",\"#008000\",\"#008000\",\"#000000\",\"#ff0000FF\",\
                      \"#0000ffFF\",\"#12C115\",\"#008000\",\"#008000\",\"#000000\",\"#ff0000FF\")'
    pch_list2    = 'c(17,17,17,17,17,17,20,20,20,20,20,20)'
    type_list2   = 'c(\"o\",\"o\",\"o\",\"o\",\"o\",\"o\",\"o\",\"o\",\"o\",\"o\",\"o\",\"o\")'
    lty_list2    = 'c(1,1,1,2,1,1,1,1,1,2,1,1)'
    lwd_list2    = 'c(2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5)'
    con_list2    = 'c(1,1,1,1,1,1,1,1,1,1,1,1)'
    order_list2  = 'c(1,2,3,4,5,6,7,8,9,10,11,12)'
    legend_list2 = 'c(\"NAM Nest - BCRMSE\",\"HiResW NMMB - BCRMSE\",\"FV3SAR - BCRMSE\",\"FV3SAR-X - BCRMSE\",\"GFS - BCRMSE\",\"HRRR - BCRMSE\", \
                      \"NAM Nest - Bias\"  ,\"HiResW NMMB - Bias\"  ,\"FV3SAR - Bias\"  ,\"FV3SAR-X - Bias\"  ,\"GFS - Bias\"  ,\"HRRR - Bias\")'

    pch_list3    = 'c(20,20,20,20,20,20,17,17,17,17,17,17)'
    legend_list3 = 'c(\"NAM Nest - Bias\",\"HiResW NMMB - Bias\",\"FV3SAR - Bias\",\"FV3SAR-X - Bias\",\"GFS - Bias\",\"HRRR - Bias\", \
                      \"NAM Nest - RMSVE\"  ,\"HiResW NMMB - RMSVE\"  ,\"FV3SAR - RMSVE\"  ,\"FV3SAR-X - RMSVE\"  ,\"GFS - RMSVE\"  ,\"HRRR - RMSVE\")'


# Specs for meso graphics
elif str.upper(verf_job) == 'MESO':
    cycles = np.arange(0,19,6)
    fhrs = np.arange(0,85,6)

    model_list = '                <val>GFS</val>\n'\
                 '                <val>NAM</val>\n'\
                 '                <val>RAP</val>\n'
    prods = ['NAM']
    paras = ['NAM']
    prod_labels = ['NAM']
    para_labels = ['NAM']

    ci_list     = 'c(\"none\",\"none\",\"none\")'
    signif_list = 'c(FALSE,FALSE,FALSE)'
    disp_list   = 'c(TRUE,TRUE,TRUE)'
    colors_list = 'c(\"#000000\",\"#00aaffFF\",\"#8b0000\")'
    pch_list    = 'c(20,20,20)'
    type_list   = 'c(\"l\",\"l\",\"l\")'
    lty_list    = 'c(1,1,1)'
    lwd_list    = 'c(2.5,2.5,2.5)'
    con_list    = 'c(1,1,1)'
    order_list  = 'c(1,2,3)'
    legend_list = 'c(\"GFS\",\"NAM\",\"RAP\")'

    ci_list2     = 'c(\"none\",\"none\",\"none\",\"none\",\"none\",\"none\")'
    signif_list2 = 'c(FALSE,FALSE,FALSE,FALSE,FALSE,FALSE)'
    disp_list2   = 'c(TRUE,TRUE,TRUE,TRUE,TRUE,TRUE)'
    colors_list2 = 'c(\"#000000\",\"#00aaffFF\",\"#8b0000\",\
                      \"#000000\",\"#00aaffFF\",\"#8b0000\")'
    pch_list2    = 'c(17,17,17,20,20,20)'
    type_list2   = 'c(\"o\",\"o\",\"o\",\"o\",\"o\",\"o\")'
    lty_list2    = 'c(1,1,1,1,1,1)'
    lwd_list2    = 'c(2.5,2.5,2.5,2.5,2.5,2.5)'
    con_list2    = 'c(1,1,1,1,1,1)'
    order_list2  = 'c(1,2,3,4,5,6)'
    legend_list2 = 'c(\"GFS - BCRMSE\",\"NAM - BCRMSE\",\"RAP - BCRMSE\", \
                      \"GFS - Bias\"  ,\"NAM - Bias\"  ,\"RAP - Bias\")'

    pch_list3    = 'c(20,20,20,17,17,17)'
    legend_list3 = 'c(\"GFS - Bias\" ,\"NAM - Bias\" ,\"RAP - Bias\", \
                      \"GFS - RMSVE\",\"NAM - RMSVE\",\"RAP - RMSVE\")'


elif str.upper(verf_job) == 'CAM':
    cycles = np.arange(0,13,12)
    fhrs = np.arange(0,61,6)

    model_list = '                <val>CONUSARW</val>\n'\
                 '                <val>CONUSARW2</val>\n'\
                 '                <val>CONUSNEST</val>\n'\
                 '                <val>CONUSNMMB</val>\n'\
                 '                <val>HRRR</val>\n'
    prods = ['CONUSNEST']
    paras = ['CONUSNEST']
    prod_labels = ['CONUSNEST']
    para_labels = ['CONUSNEST']

    ci_list     = 'c(\"none\",\"none\",\"none\",\"none\",\"none\")'
    signif_list = 'c(FALSE,FALSE,FALSE,FALSE,FALSE)'
    disp_list   = 'c(TRUE,TRUE,TRUE,TRUE,TRUE)'
    colors_list = 'c(\"#ff8c00\",\"#ff00ff\",\"#0000ffFF\",\"#12C115\",\"#ff0000FF\")'
    pch_list    = 'c(20,20,20,20,20)'
    type_list   = 'c(\"l\",\"l\",\"l\",\"l\",\"l\")'
    lty_list    = 'c(1,1,1,1,1)'
    lwd_list    = 'c(2.5,2.5,2.5,2.5,2.5)'
    con_list    = 'c(1,1,1,1,1)'
    order_list  = 'c(1,2,3,4,5)'
    legend_list = 'c(\"HiResW ARW\",\"HiResW ARW2\",\"NAM Nest\",\"HiResW NMMB\",\"HRRR\")'

    ci_list2     = 'c(\"none\",\"none\",\"none\",\"none\",\"none\",\"none\",\"none\",\"none\",\"none\",\"none\")'
    signif_list2 = 'c(FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE)'
    disp_list2   = 'c(TRUE,TRUE,TRUE,TRUE,TRUE,TRUE,TRUE,TRUE,TRUE,TRUE)'
    colors_list2 = 'c(\"#ff8c00\",\"#ff00ff\",\"#0000ffFF\",\"#12C115\",\"#ff0000FF\",\
                      \"#ff8c00\",\"#ff00ff\",\"#0000ffFF\",\"#12C115\",\"#ff0000FF\")'
    pch_list2    = 'c(17,17,17,17,17,20,20,20,20,20)'
    type_list2   = 'c(\"o\",\"o\",\"o\",\"o\",\"o\",\"o\",\"o\",\"o\",\"o\",\"o\")'
    lty_list2    = 'c(1,1,1,1,1,1,1,1,1,1)'
    lwd_list2    = 'c(2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5)'
    con_list2    = 'c(1,1,1,1,1,1,1,1,1,1)'
    order_list2  = 'c(1,2,3,4,5,6,7,8,9,10)'
    legend_list2 = 'c(\"HiResW ARW - BCRMSE\",\"HiResW ARW2 - BCRMSE\",\"NAM Nest - BCRMSE\",\"HiResW NMMB - BCRMSE\",\"HRRR - BCRMSE\", \
                      \"HiResW ARW - Bias\"  ,\"HiResW ARW2 - Bias\"  ,\"NAM Nest - Bias\"  ,\"HiResW NMMB - Bias\"  ,\"HRRR - Bias\")'

    pch_list3    = 'c(20,20,20,20,20,17,17,17,17,17)'
    legend_list3 = 'c(\"HiResW ARW - Bias\" ,\"HiResW ARW2 - Bias\" ,\"NAM Nest - Bias\" ,\"HiResW NMMB - Bias\" ,\"HRRR - Bias\", \
                      \"HiResW ARW - RMSVE\",\"HiResW ARW2 - RMSVE\",\"NAM Nest - RMSVE\",\"HiResW NMMB - RMSVE\",\"HRRR - RMSVE\")'



# Specs for NAM/Nest graphics
elif str.upper(verf_job) == 'NAM':
    cycles = np.arange(0,19,6)
    fhrs = np.arange(0,85,6)

    model_list = '                <val>CONUSNEST</val>\n'\
                 '                <val>NAM</val>\n'
    prods = ['NAM']
    paras = ['NAM']
    prod_labels = ['NAM']
    para_labels = ['NAM']

    ci_list     = 'c(\"none\",\"none\")'
    signif_list = 'c(FALSE,FALSE)'
    disp_list   = 'c(TRUE,TRUE)'
    colors_list = 'c(\"#0000ffFF\",\"#00aaffFF\")'
    pch_list    = 'c(20,20)'
    type_list   = 'c(\"l\",\"l\")'
    lty_list    = 'c(1,1)'
    lwd_list    = 'c(2.5,2.5)'
    con_list    = 'c(1,1)'
    order_list  = 'c(1,2)'
    legend_list = 'c(\"NAM Nest\",\"NAM\")'

    ci_list2     = 'c(\"none\",\"none\",\"none\",\"none\")'
    signif_list2 = 'c(FALSE,FALSE,FALSE,FALSE)'
    disp_list2   = 'c(TRUE,TRUE,TRUE,TRUE)'
    colors_list2 = 'c(\"#0000ffFF\"\"#00aaffFF\",\"#0000ffFF\",\"#00aaffFF\")'
    pch_list2    = 'c(17,17,20,20)'
    type_list2   = 'c(\"o\",\"o\",\"o\",\"o\")'
    lty_list2    = 'c(1,1,1,1)'
    lwd_list2    = 'c(2.5,2.5,2.5,2.5)'
    con_list2    = 'c(1,1,1,1)'
    order_list2  = 'c(1,2,3,4)'
    legend_list2 = 'c(\"NAM Nest - BCRMSE\",\"NAM - BCRMSE\",\"NAM Nest - Bias\",\"NAM - Bias\")'

    pch_list3    = 'c(20,20,17,17)'
    legend_list3 = 'c(\"NAM Nest - Bias\",\"NAM - Bias\",\"NAM Nest - RMSVE\",\"NAM - RMSVE\")'



# Specs for RAP/HRRR graphics
elif str.upper(verf_job) == 'RAP_HRRR':
    cycles = np.arange(0,22,3)
    fhrs = np.arange(0,52,6)

    model_list = '                <val>HRRR</val>\n'\
                 '                <val>RAP</val>\n'
    prods = ['RAP']
    paras = ['RAP']
    prod_labels = ['RAP']
    para_labels = ['RAP']

    ci_list     = 'c(\"none\",\"none\")'
    signif_list = 'c(FALSE,FALSE)'
    disp_list   = 'c(TRUE,TRUE)'
    colors_list = 'c(\"#ff0000FF\",\"#8b0000\")'
    pch_list    = 'c(20,20)'
    type_list   = 'c(\"l\",\"l\")'
    lty_list    = 'c(1,1)'
    lwd_list    = 'c(2.5,2.5)'
    con_list    = 'c(1,1)'
    order_list  = 'c(1,2)'
    legend_list = 'c(\"HRRR\",\"RAP\")'

    ci_list2     = 'c(\"none\",\"none\",\"none\",\"none\")'
    signif_list2 = 'c(FALSE,FALSE,FALSE,FALSE)'
    disp_list2   = 'c(TRUE,TRUE,TRUE,TRUE)'
    colors_list2 = 'c(\"#ff0000FF\"\"#8b0000\",\"#ff0000FF\",\"#8b0000\")'
    pch_list2    = 'c(17,17,20,20)'
    type_list2   = 'c(\"o\",\"o\",\"o\",\"o\")'
    lty_list2    = 'c(1,1,1,1)'
    lwd_list2    = 'c(2.5,2.5,2.5,2.5)'
    con_list2    = 'c(1,1,1,1)'
    order_list2  = 'c(1,2,3,4)'
    legend_list2 = 'c(\"HRRR - BCRMSE\",\"RAP - BCRMSE\",\"HRRR - Bias\",\"RAP - Bias\")'

    pch_list3    = 'c(20,20,17,17)'
    legend_list3 = 'c(\"HRRR - Bias\",\"RAP - Bias\",\"HRRR - RMSVE\",\"RAP - RMSVE\")'


else:
   print("Invalid verification job name used. Plot specs will be undefined. Use appropriate 'verf_job' string or add new definition. Exiting.")
   exit()



# Set up prod/para pairs for scorecards
name_pairs = [n for n in itertools.product(prods,paras)]
label_pairs = [n for n in itertools.product(prod_labels,para_labels)]

# Check for "same model" pairs and remove from list
n = 0
npairs = len(name_pairs)
while n < npairs:
    if name_pairs[n][0] == name_pairs[n][1]:
        del name_pairs[n]
        del label_pairs[n]
        npairs = npairs - 1
    else:
        n += 1


# Loop over model pairs to make scorecards
for i in xrange(npairs):
    prod = name_pairs[i][0]
    para = name_pairs[i][1]
    prod_label = label_pairs[i][0]
    para_label = label_pairs[i][1]

    # Define scorecards to run for Alaska and CONUS
    if prod[-2:] == 'AK' and para[-2:] == 'AK':
        plottypes2 = ['sfc','upper','cv']
        regions = ['Alaska']
    else:
        plottypes2 = ['sfc','upper','cv','cape','24hpcp','6hpcp']
        regions = ['CONUS']


    plottypes = ['fcstlead']
    scorecards = [n for n in itertools.product(plottypes,plottypes2)]

    for scorecard in scorecards:
        for region in regions:

            mv_database, vday2 = update_db_vday2(scorecard[1])
            vx_mask = update_vx_mask('scorecard',region)

            template_xml = TEMPLATE_DIR+'/scorecard_'+scorecard[1]+'_'+scorecard[0]+'.xml'  
            temp_xml = TEMP_DIR+'/scorecard_'+scorecard[1]+'_'+scorecard[0]+'.xml'  
            updated_xml = SCRIPT_DIR+'/'+str.lower(para_label)+'_'+str.lower(prod_label)+'_'+scorecard[1]+'_'+scorecard[0]+'_scorecard.xml'
            outfile = OUTPUT_DIR+'/'+str.lower(para_label)+'_'+str.lower(prod_label)+'_'+scorecard[1]+'_'+scorecard[0]+'_scorecard.out'

            update_xml('scorecard',template_xml, updated_xml)
            if now.strftime('%A') == 'Monday' or now.strftime('%A') == 'Friday':
                run_metviewer('scorecard', updated_xml)

# Set up directory for saving scorecards
SCORECARD_DIR = os.path.join(PLOT_DIR,'scorecards')
if os.path.exists(SCORECARD_DIR):
    shutil.rmtree(SCORECARD_DIR)
os.makedirs(SCORECARD_DIR)

plot_files = os.listdir(PLOT_DIR)
for files in plot_files:
    if files.endswith(".png"):
        source = PLOT_DIR+'/'+files
        dest = SCORECARD_DIR+'/'+files
        shutil.move(source,dest)

        o = open(SCORECARD_DIR+'/done.'+now.strftime('%Y%m%d'),"w")
        o.write('Finished making scorecards')
        o.close()




# Loop through to generate performance diagrams
regions = ['CONUS','East','West','Plains']
plottypes = ['fcstthresh3']
plottypes2 = ['ceiling','vis','cape','24hpcp']

plots = [n for n in itertools.product(plottypes,plottypes2)]

for region in regions:
    for cycle in cycles:
        for plot in plots:

            mv_database, vday2 = update_db_vday2(plot[1])
            vx_mask = update_vx_mask('batch',region)


            if plot[0][-11:] == 'fcstthresh3':
                template_xml = TEMPLATE_DIR+'/perf_'+plot[0]+'_'+plot[1]+'.xml' 
                temp_xml = TEMP_DIR+'/perf_'+plot[0]+'_'+plot[1]+'.xml' 
                updated_xml = SCRIPT_DIR+'/perf_'+plot[0]+'_'+plot[1]+'.xml'
                outfile = OUTPUT_DIR+'/perf_'+plot[0]+'_'+plot[1]+'_'+str(cycle).zfill(2)+'z_'+region+'.out'

                update_xml('batch',template_xml, updated_xml)
                run_metviewer('batch', updated_xml)


# Set up directory for saving performance diagrams
PERFORMANCE_DIR = os.path.join(PLOT_DIR,'performance')
if os.path.exists(PERFORMANCE_DIR):
    shutil.rmtree(PERFORMANCE_DIR)
os.makedirs(PERFORMANCE_DIR)

plot_files = os.listdir(PLOT_DIR)
for files in plot_files:
    if files.endswith("perf-diag.png"):
        source = PLOT_DIR+'/'+files
        dest = PERFORMANCE_DIR+'/'+files
        shutil.move(source,dest)

        o = open(PERFORMANCE_DIR+'/done.'+now.strftime('%Y%m%d'),"w")
        o.write('Finished making performance diagrams')





# Loop through to generate valid hour series plots
regions = ['CONUS','East','West','Plains']
plottypes = ['validhour']
plottypes2 = ['sfc_z0','sfc_z2','sfc_z10','upper','upperwind','cape','ceiling','vis']

plots = [n for n in itertools.product(plottypes,plottypes2)]

for region in regions:
    for plot in plots:

        mv_database, vday2 = update_db_vday2(plot[1])
        vx_mask = update_vx_mask('batch',region)

        template_xml = TEMPLATE_DIR+'/'+plot[0]+'_'+plot[1]+'.xml' 
        updated_xml = SCRIPT_DIR+'/series_'+plot[0]+'_'+plot[1]+'.xml'

        # Loop through ceiling thresholds
        if plot[1] == 'ceiling': 
            for j in xrange(len(ceil_thresholds)):
                thresh = ceil_thresholds[j]
                imperial_thresh = us_ceil_thresholds[j]

                outfile = OUTPUT_DIR+'/series_'+plot[0]+'_'+plot[1]+'_'+str(thresh)+'_'+region+'.out'
                update_xml('batch',template_xml, updated_xml)
                run_metviewer('batch', updated_xml)

        # Loop through visibility thresholds
        elif plot[1] == 'vis':
            for j in xrange(len(vis_thresholds)):
                thresh = vis_thresholds[j]
                imperial_thresh = us_vis_thresholds[j]

                outfile = OUTPUT_DIR+'/series_'+plot[0]+'_'+plot[1]+'_'+str(thresh)+'_'+region+'.out'
                update_xml('batch',template_xml, updated_xml)
                run_metviewer('batch', updated_xml)

        # Loop through CAPE thresholds
        elif plot[1] == 'cape':
            for thresh in cape_thresholds:

                outfile = OUTPUT_DIR+'/series_'+plot[0]+'_'+plot[1]+'_'+str(thresh)+'_'+region+'.out'
                update_xml('batch',template_xml, updated_xml)
                run_metviewer('batch', updated_xml)

        # Upper air plots
        elif plot[1] == 'upper' or plot[1] == 'upperwind':
            for cycle in cycles:

                if region == 'CONUS':
                    outfile = OUTPUT_DIR+'/series_'+plot[0]+'_'+plot[1]+'_'+str(cycle).zfill(2)+'z_'+region+'.out'
                    update_xml('batch',template_xml, updated_xml)
                    run_metviewer('batch', updated_xml)

        # Sfc plots
        else:
            outfile = OUTPUT_DIR+'/series_'+plot[0]+'_'+plot[1]+'_'+region+'.out'
            update_xml('batch',template_xml, updated_xml)
            run_metviewer('batch', updated_xml)


# Set up directory for saving valid hour series plots
VALIDHOUR_DIR = os.path.join(PLOT_DIR,'series_validhour')
if os.path.exists(VALIDHOUR_DIR):
    shutil.rmtree(VALIDHOUR_DIR)
os.makedirs(VALIDHOUR_DIR)

plot_files = os.listdir(PLOT_DIR)
for files in plot_files:
    if files.endswith(".png"):
        source = PLOT_DIR+'/'+files
        dest = VALIDHOUR_DIR+'/'+files
        shutil.move(source,dest)

        o = open(VALIDHOUR_DIR+'/done.'+now.strftime('%Y%m%d'),"w")
        o.write('Finished making valid hour series plots')
        o.close()




# Loop through to generate fcst lead series plots
regions = ['CONUS','East','West','Plains']
plottypes = ['fcstlead']
plottypes2 = ['sfc_z0','sfc_z2','sfc_z10','upper','upperwind','cape','ceiling','vis']

plots = [n for n in itertools.product(plottypes,plottypes2)]

for region in regions:
    for cycle in cycles:
        for plot in plots:

            mv_database, vday2 = update_db_vday2(plot[1])
            vx_mask = update_vx_mask('batch',region)

            template_xml = TEMPLATE_DIR+'/'+plot[0]+'_'+plot[1]+'.xml' 
            updated_xml = SCRIPT_DIR+'/series_'+plot[0]+'_'+plot[1]+'.xml'

            # Loop through ceiling thresholds
            if plot[1] == 'ceiling': 
                for j in xrange(len(ceil_thresholds)):
                    thresh = ceil_thresholds[j]
                    imperial_thresh = us_ceil_thresholds[j]

                    outfile = OUTPUT_DIR+'/series_'+plot[0]+'_'+plot[1]+'_'+str(cycle).zfill(2)+'z_'+str(thresh)+'_'+region+'.out'
                    update_xml('batch',template_xml, updated_xml)
                    run_metviewer('batch', updated_xml)

            # Loop through visibility thresholds
            elif plot[1] == 'vis':
                for j in xrange(len(vis_thresholds)):
                    thresh = vis_thresholds[j]
                    imperial_thresh = us_vis_thresholds[j]

                    outfile = OUTPUT_DIR+'/series_'+plot[0]+'_'+plot[1]+'_'+str(cycle).zfill(2)+'z_'+str(thresh)+'_'+region+'.out'
                    update_xml('batch',template_xml, updated_xml)
                    run_metviewer('batch', updated_xml)

            # Loop through CAPE thresholds
            elif plot[1] == 'cape':
                for thresh in cape_thresholds:

                    outfile = OUTPUT_DIR+'/series_'+plot[0]+'_'+plot[1]+'_'+str(cycle).zfill(2)+'z_'+str(thresh)+'_'+region+'.out'
                    update_xml('batch',template_xml, updated_xml)
                    run_metviewer('batch', updated_xml)

            # Loop through pressure levels
            elif plot[1] == 'upper' or plot[1] == 'upperwind':
                for plev in plevs:

                    if region == 'CONUS':
                        outfile = OUTPUT_DIR+'/series_'+plot[0]+'_'+plot[1]+'_'+str(cycle).zfill(2)+'z_'+str(plev)+'mb_'+region+'.out'
                        update_xml('batch',template_xml, updated_xml)
                        run_metviewer('batch', updated_xml)

            # Sfc plots
            else:
                outfile = OUTPUT_DIR+'/series_'+plot[0]+'_'+plot[1]+'_'+str(cycle).zfill(2)+'z_'+region+'.out'
                update_xml('batch',template_xml, updated_xml)
                run_metviewer('batch', updated_xml)


# Set up directory for saving forecast lead series plots
FCSTLEAD_DIR = os.path.join(PLOT_DIR,'series_fcstlead')
if os.path.exists(FCSTLEAD_DIR):
    shutil.rmtree(FCSTLEAD_DIR)
os.makedirs(FCSTLEAD_DIR)

plot_files = os.listdir(PLOT_DIR)
for files in plot_files:
    if files.endswith(".png"):
        source = PLOT_DIR+'/'+files
        dest = FCSTLEAD_DIR+'/'+files
        shutil.move(source,dest)

        o = open(FCSTLEAD_DIR+'/done.'+now.strftime('%Y%m%d'),"w")
        o.write('Finished making forecast lead series plots')
        o.close()




# Loop through to generate verification date series plots
regions = ['CONUS']
plottypes = ['initdate']
plottypes2 = ['sfc_z0','sfc_z2','sfc_z10','cape','ceiling','vis']

plots = [n for n in itertools.product(plottypes,plottypes2)]

for region in regions:
    for plot in plots:

        mv_database, vday2 = update_db_vday2(plot[1])
        vx_mask = update_vx_mask('batch',region)

        template_xml = TEMPLATE_DIR+'/'+plot[0]+'_'+plot[1]+'.xml' 
        updated_xml = SCRIPT_DIR+'/series_'+plot[0]+'_'+plot[1]+'.xml'

        # Loop through ceiling thresholds
        if plot[1] == 'ceiling': 
            for fhr in fhrs:
                for j in xrange(len(ceil_thresholds)):
                    thresh = ceil_thresholds[j]
                    imperial_thresh = us_ceil_thresholds[j]

                    outfile = OUTPUT_DIR+'/series_'+plot[0]+'_'+plot[1]+'_f'+str(fhr).zfill(2)+'_'+str(thresh)+'_'+region+'.out'
                    update_xml('batch',template_xml, updated_xml)
                    run_metviewer('batch', updated_xml)

        # Loop through visibility thresholds
        elif plot[1] == 'vis':
            for fhr in fhrs:
                for j in xrange(len(vis_thresholds)):
                    thresh = vis_thresholds[j]
                    imperial_thresh = us_vis_thresholds[j]

                    outfile = OUTPUT_DIR+'/series_'+plot[0]+'_'+plot[1]+'_f'+str(fhr).zfill(2)+'_'+str(thresh)+'_'+region+'.out'
                    update_xml('batch',template_xml, updated_xml)
                    run_metviewer('batch', updated_xml)

        # Loop through CAPE thresholds
        elif plot[1] == 'cape':
            for fhr in fhrs:
                for thresh in cape_thresholds:

                    outfile = OUTPUT_DIR+'/series_'+plot[0]+'_'+plot[1]+'_f'+str(fhr).zfill(2)+'_'+str(thresh)+'_'+region+'.out'
                    update_xml('batch',template_xml, updated_xml)
                    run_metviewer('batch', updated_xml)

        # Sfc plots
        else:
            for fhr in fhrs:
                outfile = OUTPUT_DIR+'/series_'+plot[0]+'_'+plot[1]+'_f'+str(fhr).zfill(2)+'_'+region+'.out'
                update_xml('batch',template_xml, updated_xml)
                run_metviewer('batch', updated_xml)


# Set up directory for saving initialization date series plots
INITDATE_DIR = os.path.join(PLOT_DIR,'series_initdate')
if os.path.exists(INITDATE_DIR):
    shutil.rmtree(INITDATE_DIR)
os.makedirs(INITDATE_DIR)

plot_files = os.listdir(PLOT_DIR)
for files in plot_files:
    if files.endswith(".png"):
        source = PLOT_DIR+'/'+files
        dest = INITDATE_DIR+'/'+files
        shutil.move(source,dest)

        o = open(INITDATE_DIR+'/done.'+now.strftime('%Y%m%d'),"w")
        o.write('Finished making initialization date series plots')
        o.close()






exit()










cycles = np.arange(0,22,3)
apcp_thresh = [.01,.10,.25,.50,.75,1.0,1.5,2.0,3.0,4.0]
apcp_thresh2 = [0.01,0.10,0.25,0.50,0.75,1,1.5,2,3,4]
apcp_thresh3 = ['0p01','0p10','0p25','0p50','0p75','1p0','1p5','2p0','3p0','4p0']
refl_abbrevs = ['refl','refc','refd1','retop']

#plottypes = ['fcstlead','validhour']
#plottypes2 = ['vis','sfc_z0','sfc_z2','sfc_z10']


for i in xrange(2):

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
    
            if str.lower(plot[1]) in refl_abbrevs:
                vday2 = now + datetime.timedelta(days=-1)
            else:
                vday2 = now + datetime.timedelta(days=-2)

            # Loop over cycles for forecast lead plots
            if plot[0] == 'fcst_lead':
                template_xml = TEMPLATE_DIR++'/series_'+plot[0]+'_'+plot[1]+'.xml' 
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
          




# Loop through to generate performance xmls
domains = ['CONUS','Alaska','East','West']

for region in regions:
    if region == 'Alaska':
        diags = ['ceiling','vis']
    else:
        diags = ['ceiling','vis','cape','24hpcp','refc','retop']

