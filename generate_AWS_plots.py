import sys, os, shutil
import datetime, time, calendar
import numpy as np
import subprocess
import re, csv, glob 
import itertools
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import dawsonpy


# Function to create final xml using template and  multiple_replace function
def update_xml(jobtype,plottype,template_xml,updated_xml):

    # Copy template to verf_job directory
    os.system('cp '+template_xml+' '+temp_xml)

    #############################################################################################
                       # Insert list of model values for batch jobs #
    #############################################################################################

    # Set list of model names
    if str.upper(verf_job) == 'FV3CAM' and str.lower(verf_exp) == 'para_exp':
        nam3_val  = '                <val>'+nam3[domain_key]+'</val>\n'
        lam_val   = '                <val>'+lam[domain_key]+'</val>\n'
        lamda_val = '                <val>'+lamda[domain_key]+'</val>\n'
        lamx_val  = '                <val>'+lamx[domain_key]+'</val>\n'
        gfs_val   = '                <val>'+gfs[domain_key]+'</val>\n'
        hrrr_val  = '                <val>'+hrrr[domain_key]+'</val>\n'

        model_list = nam3_val + lam_val + lamda_val + lamx_val + gfs_val + hrrr_val

    elif str.upper(verf_job) == 'FV3CAM' and str.lower(verf_exp) == 'da_exp':
        lam_val    = '                <val>'+lam[domain_key]+'</val>\n'
        lamda_val  = '                <val>'+lamda[domain_key]+'</val>\n'
        lamdax_val = '                <val>'+lamdax[domain_key]+'</val>\n'

        model_list = lam_val + lamda_val + lamdax_val

    elif str.upper(verf_job) == 'FV3CAM' and str.lower(verf_exp) == 'lam_exp':
        lam_val   = '                <val>'+lam[domain_key]+'</val>\n'
        lamx_val  = '                <val>'+lamx[domain_key]+'</val>\n'

        model_list = lam_val + lamx_val

    elif (str.upper(verf_job) == 'FV3CAM' and 
         (str.lower(verf_exp) == 'sarda_exp' or str.lower(verf_exp) == 'sar_exp')):
        sar_val   = '                <val>'+sar[domain_key]+'</val>\n'
        sarda_val = '                <val>'+sarda[domain_key]+'</val>\n'
        sarx_val  = '                <val>'+sarx[domain_key]+'</val>\n'
 
        if str.lower(verf_exp) == 'sar_exp':
            model_list = sar_val + sarx_val
        elif str.lower(verf_exp) == 'sarda_exp':
            model_list = sar_val + sarda_val

    elif str.upper(verf_job) == 'HREF_MEM':
        fv3_val   = '                <val>'+hrwfv3[domain_key]+'</val>\n'
        nmmb_val  = '                <val>'+hrwnmmb[domain_key]+'</val>\n'

        model_list = fv3_val + nmmb_val

    elif str.upper(verf_job) == 'HREFV3':

        # Precip plots comparing HREF PMMN, HREFX PMMN, and HREFX LPMM
        if plottype[-4:] == 'lpmm': 
            href_pmmn_val  = '                <val>'+href['pcp']+href['pmmn']+'</val>\n'
            hrefx_lpmm_val = '                <val>'+hrefx['pcp']+hrefx['lpmm']+'</val>\n'
            hrefx_pmmn_val = '                <val>'+hrefx['pcp']+hrefx['pmmn']+'</val>\n'

            model_list = href_pmmn_val + hrefx_lpmm_val + hrefx_pmmn_val

        # Precip plots comparing HREF AVRG, HREFX AVRG, and HREFX LAVG
        elif plottype[-4:] == 'avrg': 
            href_avrg_val  = '                <val>'+href['pcp']+href['avrg']+'</val>\n'
            hrefx_avrg_val = '                <val>'+hrefx['pcp']+hrefx['avrg']+'</val>\n'
            hrefx_lavg_val = '                <val>'+hrefx['pcp']+hrefx['lavg']+'</val>\n'

            model_list = href_avrg_val + hrefx_avrg_val + hrefx_lavg_val

        # Precip plots comparing HREFX AVRG, LAVG, LPMM, MEAN, PMMN
        elif plottype[-7:] == 'v3prods': 
            hrefx_avrg_val = '                <val>'+hrefx['pcp']+hrefx['avrg']+'</val>\n'
            hrefx_lavg_val = '                <val>'+hrefx['pcp']+hrefx['lavg']+'</val>\n'
            hrefx_lpmm_val = '                <val>'+hrefx['pcp']+hrefx['lpmm']+'</val>\n'
            hrefx_mean_val = '                <val>'+hrefx['pcp']+hrefx['mean']+'</val>\n'
            hrefx_pmmn_val = '                <val>'+hrefx['pcp']+hrefx['pmmn']+'</val>\n'

            model_list = hrefx_avrg_val + hrefx_lavg_val + hrefx_lpmm_val + hrefx_mean_val + hrefx_pmmn_val

        # works for all other 24-h and 3-h precip plots
        elif plottype[0:6] == '24hpcp' or plottype[0:5] == '3hpcp': 
            href_val  = '                <val>'+href['pcp']+href[ensprod_key]+'</val>\n'
            hrefx_val = '                <val>'+hrefx['pcp']+hrefx[ensprod_key]+'</val>\n'

            model_list = href_val + hrefx_val

        # All other HREFv3 stats from Binbin
        elif plottype[0:3] == 'sfc' or plottype == 'cape' or plottype == 'ceiling' or plottype == 'vis': 
            hrefx_mean_val = '                <val>'+hrefx[domain_key]+'_'+hrefx['mean']+'</val>\n'
            href_mean_val  = '                <val>'+href[domain_key]+'_'+href['mean']+'</val>\n'
            href_mean_val  = '                <val>HREFMEAN</val>\n'
            hrefx_mean_val = '                <val>HREFV3MEAN</val>\n'

            model_list = href_mean_val + hrefx_mean_val

        # Radar and surrogate severe stats
        elif ensprod_key == 'nbmax':
            hrefx_val = '                <val>'+hrefx[domain_key]+'_'+hrefx['prob']+'</val>\n'
            href_val  = '                <val>'+href[domain_key]+'_'+href['prob']+'</val>\n'

            model_list = hrefx_val + href_val
        else:
            hrefx_val = '                <val>'+hrefx[domain_key]+'_'+hrefx[ensprod_key]+'</val>\n'
            href_val  = '                <val>'+href[domain_key]+'_'+href[ensprod_key]+'</val>\n'

            model_list = hrefx_val + href_val



    elif str.upper(verf_job) == 'CAM':
        arw_val  = '                <val>'+hrwarw[domain_key]+'</val>\n'
        arw2_val = '                <val>'+hrwarw2[domain_key]+'</val>\n'
        nam3_val = '                <val>'+nam3[domain_key]+'</val>\n'
        nmmb_val = '                <val>'+hrwnmmb[domain_key]+'</val>\n'
        hrrr_val = '                <val>'+hrrr[domain_key]+'</val>\n'

        model_list = arw_val + arw2_val + nam3_val + nmmb_val + hrrr_val

    elif str.upper(verf_job) == 'MESO':
        gfs_val  = '                <val>'+gfs[domain_key]+'</val>\n'
        nam_val  = '                <val>'+nam[domain_key]+'</val>\n'
        rap_val  = '                <val>'+rap[domain_key]+'</val>\n'

        model_list = gfs_val + nam_val + rap_val



    # Read lines of temp XML
    with open(temp_xml,"r") as f:
        data = f.readlines()
        f.close()

    # Find correct number and insert model list
    insert_ind = data.index('            <field name=\"model\">\n')
    data.insert(insert_ind+1,model_list)

    # Write updated XML
    f = open(temp_xml,"w")
    data = "".join(data)
    f.write(data)
    f.close() 


    #############################################################################################
                   # Insert list of forecast hours for forecast lead jobs #
    #############################################################################################

    # Define x-axis for forecast lead plots
    if str.lower(plot[0]) == 'fcstlead':
        if plottype[0:5] == 'upper': 
            if cycle%12 == 0:
                leads = np.arange(0,runlength+1,12) 
            elif cycle%12 == 6:
                leads = np.arange(6,runlength+1,12) 

        elif plottype[0:4] == 'cape': 
            leads = np.arange(0,runlength+1,6) 

        elif plottype[0:5] == 'radar':
            ones   = np.arange(0,12,1) 
            threes = np.arange(12,runlength+1,3) 
            leads  = np.concatenate((ones,threes),axis=None)

        else:
            leads = np.arange(0,runlength+1,3) 

        # Loop over leads to build list to be inserted
        lead_list = '            <val label=\"0\" plot_val=\"\">0</val>\n'
        for lead in leads[1:]:
            lead_list = lead_list + '            <val label=\"'+str(lead)\
                                  +'\" plot_val=\"\">'+str(lead*10000)+'</val>\n'
        
        # Read lines of temp XML
        with open(temp_xml,"r") as f:
            data = f.readlines()
            f.close()

        # Find correct number and insert lead list
        insert_ind = data.index('        <indep equalize=\"true\" name=\"fcst_lead\">\n')
        data.insert(insert_ind+1,lead_list)

        # Write updated XML
        f = open(temp_xml,"w")
        data = "".join(data)
        f.write(data)
        f.close()
       

    #############################################################################################
                       # Replacements #
    #############################################################################################

    replacements = {

        "%VERF_JOB%"     : str.lower(verf_job),
        "%SUB_DIR%"      : str.lower(sub_dir),
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

        "%ENSPROD%"      : str.upper(ensprod_key),
        "%FCST_VAR%"     : str.upper(fcst_var),
        "%PPP%"          : str(plev),
        "%THRESH%"       : str(thresh),
        "%THRESH2%"      : str(imperial_thresh),
        "%HREF_THRESH%"  : '%.3f' % thresh,
        "%INT_PTS%"      : str(interp_pnts),
        "%NBR%"          : nbrhd,

        "%GGG%"          : vx_mask,
        "%REGION%"       : region_strings[str.lower(region)],
        "%region%"       : str.lower(region),

        "%BOOT_REPL%"    : str(boot_repl),
        "%EVENT_EQ%"     : event_eq,

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

        # subs for plot settings in batch scripts with two lines per model
        "%CI_LIST4%"     : ci_list4,
        "%SIGNIF_LIST4%" : signif_list4,
        "%DISP_LIST4%"   : disp_list4,
        "%COLORS_LIST4%" : colors_list4,
        "%PCH_LIST4%"    : pch_list4,
        "%LTY_LIST4%"    : lty_list4,
        "%LWD_LIST4%"    : lwd_list4,
        "%CON_LIST4%"    : con_list4,
        "%ORDER_LIST4%"  : order_list4,
        "%TYPE_LIST4%"   : type_list4,
        "%LEGEND_LIST4%" : legend_list4,

        # subs for plot settings in batch scripts with two lines per model
        "%CI_LIST5%"     : ci_list5,
        "%SIGNIF_LIST5%" : signif_list5,
        "%DISP_LIST5%"   : disp_list5,
        "%COLORS_LIST5%" : colors_list5,
        "%PCH_LIST5%"    : pch_list5,
        "%TYPE_LIST5%"   : type_list5,
        "%LTY_LIST5%"    : lty_list5,
        "%LWD_LIST5%"    : lwd_list5,
        "%CON_LIST5%"    : con_list5,
        "%ORDER_LIST5%"  : order_list5,
        "%LEGEND_LIST5%" : legend_list5,

        # subs for plot settings in batch scripts with three lines total
        "%CI_LIST6%"      : ci_list6,
        "%SIGNIF_LIST6%"  : signif_list6,
        "%DISP_LIST6%"    : disp_list6,
        "%COLORS_LIST6%"  : colors_list6,
        "%PCH_LIST6%"     : pch_list6,
        "%TYPE_LIST6%"    : type_list6,
        "%LTY_LIST6%"     : lty_list6,
        "%LWD_LIST6%"     : lwd_list6,
        "%CON_LIST6%"     : con_list6,
        "%ORDER_LIST6%"   : order_list6,
        "%LEGEND_LIST6%"  : legend_list6,

        # subs for plot settings in batch scripts with 5 lines total (HREFv3 five means)
        "%CI_LIST7%"      : ci_list7,
        "%SIGNIF_LIST7%"  : signif_list7,
        "%DISP_LIST7%"    : disp_list7,
        "%COLORS_LIST7%"  : colors_list7,
        "%PCH_LIST7%"     : pch_list7,
        "%TYPE_LIST7%"    : type_list7,
        "%LTY_LIST7%"     : lty_list7,
        "%LWD_LIST7%"     : lwd_list7,
        "%CON_LIST7%"     : con_list7,
        "%ORDER_LIST7%"   : order_list7,
        "%LEGEND_LIST7%"  : legend_list7,

        # subs for plot settings in batch scripts with 10 lines total (HREFv3 five means with diurnal obs)
        "%CI_LIST8%"      : ci_list8,
        "%SIGNIF_LIST8%"  : signif_list8,
        "%DISP_LIST8%"    : disp_list8,
        "%COLORS_LIST8%"  : colors_list8,
        "%PCH_LIST8%"     : pch_list8,
        "%TYPE_LIST8%"    : type_list8,
        "%LTY_LIST8%"     : lty_list8,
        "%LWD_LIST8%"     : lwd_list8,
        "%CON_LIST8%"     : con_list8,
        "%ORDER_LIST8%"   : order_list8,
        "%LEGEND_LIST8%"  : legend_list8,

    }


    # Open template in verf_job directory and replace using dictionary keys above 
    with open(temp_xml) as f:
        new_text = dawsonpy.multiple_replace(replacements, f.read())
        f.close()

    # Write updated XML
    with open(updated_xml, "w") as result:
        result.write(new_text)
        result.close()



# Function to create final xml using template and  multiple_replace function
def update_scorecard_xml(plottype,template_xml,updated_xml):

    # Copy template to verf_job directory
    os.system('cp '+template_xml+' '+temp_xml)

    #############################################################################################
                       # Replacements #
    #############################################################################################

    replacements = {

        "%VERF_JOB%"     : str.lower(verf_job),
        "%SUB_DIR%"      : str.lower(sub_dir),
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

        "%ENSPROD%"      : str.upper(ensprod_key),
        "%FCST_VAR%"     : str.upper(fcst_var),
        "%PPP%"          : str(plev),
        "%THRESH%"       : str(thresh),
        "%THRESH2%"      : str(imperial_thresh),
        "%HREF_THRESH%"  : '%.3f' % thresh,
        "%INT_PTS%"      : str(interp_pnts),
        "%NBR%"          : nbrhd,

        "%GGG%"          : vx_mask,
    #   "%REGION%"       : region,
        "%REGION%"       : region_strings[str.lower(region)],
        "%region%"       : str.lower(region),

        "%BOOT_REPL%"    : str(boot_repl),
        "%EVENT_EQ%"     : event_eq,

    }

    # Open template in verf_job directory and replace using dictionary keys above 
    with open(temp_xml) as f:
        new_text = dawsonpy.multiple_replace(replacements, f.read())
        f.close()

    # Write updated XML
    with open(updated_xml, "w") as result:
        result.write(new_text)
        result.close()



# Function to specify METviewer database and most recent verification date
def update_db_vday2(verf_job,plottype):

    # Precip databases
    if plottype[0:6] == '24hpcp' or plottype[0:5] == '6hpcp' or plottype[0:5] == '3hpcp':

        if str.upper(verf_job) == 'FV3CAM':
            if str.lower(verf_exp) == 'da_exp' or str.lower(verf_exp) == 'lam_exp':
                mv_database = 'mv_lam_pcp_2021_metplus'
            else:
                mv_database = 'mv_cam_pcp_2021_metplus,mv_lam_pcp_2021_metplus,mv_meso_pcp_2021_metplus'

        elif str.upper(verf_job) == 'CAM':
            mv_database = 'mv_cam_pcp_2021_metplus'

        elif str.upper(verf_job) == 'MESO':
            mv_database = 'mv_meso_pcp_2021_metplus'

        elif str.upper(verf_job) == 'HREFV3':
            mv_database = 'mv_met_hrefv2_v3_apcp'

        else:
            print("ERROR. Database not defined correctly.")

        vday2 = now + datetime.timedelta(days=-2)

    # Radar databases
    elif plottype[:2] == 're' or plottype[0:5] == 'radar':

        if str.upper(verf_job) == 'FV3CAM':
            if str.lower(verf_exp) == 'da_exp' or str.lower(verf_exp) == 'lam_exp':
                mv_database = 'mv_lam_radar_2021_metplus'
            else:
                mv_database = 'mv_cam_radar_2021_metplus,mv_lam_radar_2021_metplus'

        elif str.upper(verf_job) == 'CAM':
            mv_database = 'mv_cam_radar_2021_metplus,mv_href_radar_2021_metplus'

        elif str.upper(verf_job) == 'HREFV3':
            mv_database = 'mv_hrefv3_eval_radar_metplus'

        else:
            print("ERROR. Database not defined correctly.")

        vday2 = now + datetime.timedelta(days=-2)

    # Surrogate Severe databases
    elif plottype[0:7] == 'surrsvr':

        if str.upper(verf_job) == 'HREFV3':
            mv_database = 'mv_hrefv3_eval_surrogatesvr_metplus'

        elif str.upper(verf_job) == 'CAM':
            mv_database = 'mv_cam_svr_20201_metplus'

        if str.upper(verf_job) == 'FV3CAM':
            if str.lower(verf_exp) == 'da_exp' or str.lower(verf_exp) == 'lam_exp':
                mv_database = 'mv_lam_svr_20201_metplus'
            else:
                mv_database = 'mv_cam_svr_20201_metplus,mv_lam_svr_20201_metplus'
        else:
            print("ERROR. Database not defined correctly.")

        vday2 = now + datetime.timedelta(days=-8)

    # Grid2obs database(s)
    else:
        if str.upper(verf_job) == 'FV3CAM':
            if str.lower(verf_exp) == 'da_exp' or str.lower(verf_exp) == 'lam_exp':
                mv_database = 'mv_lam_grid2obs_2020_metplus,mv_lam_grid2obs_2021_metplus'
            else:
                mv_database = 'mv_cam_grid2obs_2021_metplus,mv_lam_grid2obs_2021_metplus,mv_meso_grid2obs_2021_metplus'

        elif str.upper(verf_job) == 'CAM':
            mv_database = 'mv_cam_grid2obs_2021_metplus,mv_href_grid2obs_2021_metplus'

        elif str.upper(verf_job) == 'MESO':
            mv_database = 'mv_meso_grid2obs_2021_metplus'

        # HREFv3 upper air database from Logan 
        elif str.upper(verf_job) == 'HREFV3' and plottype[0:5] == 'upper':
            mv_database = 'mv_hrefv3_eval_upperair_metplus'

        # HREFv3 databases from Binbin
        elif str.upper(verf_job) == 'HREFV3' and (plottype[0:3] == 'sfc' or plottype == 'cape' or plottype == 'ceiling' or plottype == 'vis'):
            mv_database = 'mv_met_hrefv2_v3_sfc'

        else:
            print("ERROR. Database not defined correctly.")

        vday2 = now + datetime.timedelta(days=-2)


    # If working on a period with a predefined end date, use that
    # Handles FV3CAM experiments, HREFV3/HREF_MEM experiments/eval periods
    # Handles monthly periods 
    if 'exp_vday2' in globals():
        vday2 = exp_vday2
    elif 'month_vday2' in globals():
        vday2 = month_vday2

    return mv_database, vday2



# Function to specify METviewer database and most recent verification date
def update_vx_mask(jobtype,region):

    # CONUS settings
    if str.upper(region) == 'CONUS':
        vx_mask = 'CONUS'
    #   if mv_database == 'mv_emc_g2o_met' and jobtype == 'batch':
    #       vx_mask = 'APL,GMC,GRB,LMV,MDW,NEC,NMT,NPL,NWC,SEC,SMT,SPL,SWC,SWD'
    #   elif mv_database == 'mv_emc_g2o_met' and jobtype == 'scorecard':
    #       vx_mask = 'FULL'
    #   else:
    #       vx_mask = 'CONUS'

    # Eastern CONUS settings
    elif str.upper(region) == 'EAST':
        if str.upper(verf_job) == 'HREFV3' and mv_database[0:14] != 'mv_hrefv3_eval':
            vx_mask = 'EAST'
        else:
            vx_mask = 'APL,GMC,LMV,MDW,NEC,SEC'

    # Western CONUS settings
    elif str.upper(region) == 'WEST':
        if str.upper(verf_job) == 'HREFV3' and mv_database[0:14] != 'mv_hrefv3_eval':
            # includes NPL and SPL
            vx_mask = 'WEST'
        else:
            # excludes NPL and SPL
            vx_mask = 'GRB,NMT,NWC,SMT,SWC,SWD'

    # Plains settings
    elif str.upper(region) == 'PLAINS':
        vx_mask = 'NPL,SPL'


    # Alaska settings
    elif str.upper(region) == 'ALASKA':
        if str.upper(verf_job) == 'HREFV3' and mv_database[0:14] != 'mv_hrefv3_eval':
            vx_mask = 'Alaska'
        else:
            vx_mask = 'NAK,SAK'


    # SPC settings
    elif str.upper(region) == 'SPC':
        vx_mask = 'DAY1_1200_MRGL,DAY2_1730_MRGL,DAY3_MRGL'

    elif str.upper(region) == 'DAY 1':
        vx_mask = 'DAY1_1200_MRGL'
    elif str.upper(region) == 'DAY 2':
        vx_mask = 'DAY2_1730_MRGL'
    elif str.upper(region) == 'DAY 3':
        vx_mask = 'DAY3_MRGL'

    elif str.upper(region) == 'TSTM':
        vx_mask = 'DAY1_1200_TSTM,DAY2_1730_TSTM,DAY3_TSTM'
    elif str.upper(region) == 'MRGL':
        vx_mask = 'DAY1_1200_MRGL,DAY2_1730_MRGL,DAY3_MRGL'
    elif str.upper(region) == 'SLGT':
        vx_mask = 'DAY1_1200_SLGT,DAY2_1730_SLGT,DAY3_SLGT'
    elif str.upper(region) == 'ENH':
        vx_mask = 'DAY1_1200_ENH,DAY2_1730_ENH,DAY3_ENH'
    elif str.upper(region) == 'MOD':
        vx_mask = 'DAY1_1200_MOD,DAY2_1730_MOD,DAY3_MOD'
    elif str.upper(region) == 'HIGH':
        vx_mask = 'DAY1_1200_HIGH,DAY2_1730_HIGH'


    # Otherwise, use region that is previously defined
    else:
        vx_mask = str.upper(region)

    return vx_mask



# Function to read METviewer data and replace performance diagram
def performance_diag(filename,plottype):

    print('Remaking performance diagram with python')

    # Read METviewer data file
    with open(filename+'.data','r') as f:
        reader = csv.reader(f)

        data_list = []
        thresh_list = []
        model_list = []
        far_list = []
        pod_list = []   

        for row in reader:
            row_list = row[0].split('\t')

            # Build list of models to plot
            if row_list[1] not in model_list and row_list[1] != 'model':
                model_list.append(row_list[1])

            # Build list of thresholds to plot
            if row_list[1] not in thresh_list:
                thresh_list.append(row_list[2])

            # Build list for easier iteration later
            if row_list[0] != 'fcst_var':
                data_list.append(row_list)

        # Get fcst_var to use for title keys
        fcst_var = row_list[0]

      # Build list of POD and FAR stats
        for model in model_list:
            model_far = []
            model_pod = []

            for row in data_list:
                if row[1] == model and row[3][-3:] == 'FAR':
                    if row[4] == 'NA':
                        model_far.append(np.nan)
                    else:
                        model_far.append(float(row[4]))
                elif row[1] == model and row[3][-4:] == 'PODY':
                    if row[4] == 'NA':
                        model_pod.append(np.nan)
                    else:
                        model_pod.append(float(row[4]))

            far_list.append(model_far)
            pod_list.append(model_pod)


    # Begin plotting
    fig = plt.figure(figsize=[8.5,8])
    ax = plt.subplot(111)

    # Define limits for diagram axes
    ax.set_xlim([0,1])
    ax.set_ylim([0,1])
    x=y = np.arange(0.01,1.01,0.01)
    X,Y = np.meshgrid(x,y)


    # Define and add CSI lines to the diagram
    bounds = np.arange(0,1.10,0.10)
    norm = matplotlib.colors.BoundaryNorm(bounds, len(bounds))
    colors=['#ffffff','#f0f0f0','#e3e3e3','#d6d6d6','#c9c9c9','#bdbdbd','#b0b0b0','#a3a3a3','#969696','#8a8a8a']
    cm = LinearSegmentedColormap.from_list('percentdiff_cbar', colors, N=len(bounds))

    CSI = ((1/X)+(1/Y)-1)**-1
    CSI_lines = ax.contourf(X,Y,CSI,np.arange(0.0,1.1,0.1),cmap=cm)


    # Define and add bias lines to the diagram
    biases=[0.1,0.25,0.5,0.75,1.0,1.5,2.0,4.0,10.0]
    bias_loc_x = [0.94,0.935,0.94,0.935,0.9,0.58,0.42,0.18,0.03]
    bias_loc_y = [0.12,0.2625,0.5,0.74,0.95,0.95,0.95,0.95,0.95]

    FBIAS = Y/X
    FBIAS_lines = ax.contour(X,Y,FBIAS,biases,colors='black',linestyles='--')

    for i,j in enumerate(biases):
        ax.annotate(j,(bias_loc_x[i],bias_loc_y[i]),fontsize=12)


    # Settings for CAM performance diagrams
    if str.upper(verf_job) == 'CAM':
        perf_legend = [hrwarw['name'],hrwarw2['name'],nam3['name'],hrwnmmb['name'],hrrr['name']]
        perf_colors = [hrwarw['pycolor'],hrwarw2['pycolor'],nam3['pycolor'],hrwnmmb['pycolor'],hrrr['pycolor']]
        perf_lines  = ['solid','solid','solid','solid','solid']
        perf_marks  = ['o','o','o','o','o']

    # Settings for MESO performance diagrams
    elif str.upper(verf_job) == 'MESO':
        perf_legend = [gfs['name'],nam['name'],rap['name']]
        perf_colors = [gfs['pycolor'],nam['pycolor'],rap['pycolor']]
        perf_lines  = ['solid','solid','solid']
        perf_marks  = ['o','o','o']

    # Settings for HREFv3 performance diagrams
    elif str.upper(verf_job) == 'HREFV3':

        # Precip plots comparing HREF PMMN, HREFX PMMN, and HREFX LPMM
        if plottype == '24hpcp_lpmm': 
            perf_legend = [href['name']+' '+href['pmmn'],hrefx['name']+' '+hrefx['lpmm'],hrefx['name']+' '+hrefx['pmmn']]
            perf_colors = [href['pycolor'],'blue',hrefx['pycolor']]
            perf_lines  = ['solid','solid','solid']
            perf_marks  = ['o','o','o']

        # Precip plots comparing HREF AVRG, HREFX AVRG, and HREFX LAVG
        elif plottype == '24hpcp_avrg': 
            perf_legend = [href['name']+' '+href['avrg'],hrefx['name']+' '+hrefx['avrg'],hrefx['name']+' '+hrefx['lavg']]
            perf_colors = [href['pycolor'],hrefx['pycolor'],'blue']
            perf_lines  = ['solid','solid','solid']
            perf_marks  = ['o','o','o']

        # Precip plots comparing HREFX AVRG, LAVG, LPMM, MEAN, PMMN
        elif plottype == '24hpcp_v3prods': 
            perf_legend = [hrefx['name']+' '+hrefx['avrg'],hrefx['name']+' '+hrefx['lavg'],hrefx['name']+' '+hrefx['lpmm'],hrefx['name']+' '+hrefx['mean'],hrefx['name']+' '+hrefx['pmmn']]
            perf_colors = [hrefx['pycolor'],'blue','blue',href['pycolor'],hrefx['pycolor']]
            perf_lines  = ['dashed','dashed','solid','solid','solid']
            perf_marks  = ['D','D','o','o','o']

        # All other HREFv3 stats from Binbin
        elif plottype == '24hpcp_mean' or plottype == 'cape' or plottype == 'ceiling' or plottype == 'vis': 
            perf_legend = [href['name']+' '+href[ensprod_key],hrefx['name']+' '+hrefx[ensprod_key]]
            perf_colors = [href['pycolor'],hrefx['pycolor']]
            perf_lines  = ['solid','solid','solid']
            perf_marks  = ['o','o']

        # Radar and surrogate severe stats
        elif plottype[0:2] == 're' or plottype == 'surrsvr':
            perf_legend = [hrefx['name']+' '+hrefx[ensprod_key],href['name']+' '+href[ensprod_key]]
            perf_colors = [hrefx['pycolor'],href['pycolor']]
            perf_lines  = ['solid','solid']
            perf_marks  = ['o','o']

    # Settings for HREF_MEM performance diagrams
    elif str.upper(verf_job) == 'HREF_MEM':
        perf_legend = [hrwfv3['name'],hrwnmmb['name']]
        perf_colors = [hrwfv3['pycolor'],hrwnmmb['pycolor']]
        perf_lines  = ['solid','solid']
        perf_marks  = ['o','o']

    # Settings for FV3-CAM performance diagrams
    elif str.upper(verf_job) == 'FV3CAM' and str.lower(verf_exp) == 'para_exp':
        perf_legend = [nam3['name'],lam['name'],lamda['name'],lamx['name'],gfs['name'],hrrr['name']]
        perf_colors = [nam3['pycolor'],lam['pycolor'],lamda['pycolor'],lamx['pycolor'],gfs['pycolor'],hrrr['pycolor']]
        perf_lines  = ['solid','solid','solid','solid','solid','solid']
        perf_marks  = ['o','o','D','^','o','o']

    # Settings for FV3-CAM LAM-X vs. LAM performance diagrams
    elif str.upper(verf_job) == 'FV3CAM' and str.lower(verf_exp) == 'lam_exp':
        perf_legend = [lam['name'],lamx['name']]
        perf_colors = [lam['pycolor'],lamx['pycolor']]
        perf_lines  = ['solid','solid']
        perf_marks  = ['o','^']

    # Settings for FV3-CAM LAM-DA vs. LAM performance diagrams
    elif str.upper(verf_job) == 'FV3CAM' and str.lower(verf_exp) == 'da_exp':
        perf_legend = [lam['name'],lamda['name']]
        perf_colors = [lam['pycolor'],lamda['pycolor']]
        perf_lines  = ['solid','solid']
        perf_marks  = ['o','D']


    # Add data lines
    for model in model_list:

        ind = model_list.index(model)
        pod = pod_list[ind]
        far = far_list[ind]
        sr  = [1 - x for x in far]

        line, = ax.plot(sr,pod,color=perf_colors[ind],linestyle=perf_lines[ind],label=perf_legend[ind],linewidth=3)
        pts = ax.plot(sr,pod,color=perf_colors[ind],marker=perf_marks[ind],markersize=7)


    # Add title and axis labels
    titlestr = var_strings[str.upper(fcst_var)]+' Performance Diagram \n'+ \
               region_strings[str.lower(region)]+' - Valid from '+vday1.strftime('%d %B %Y')+' to '+vday2.strftime('%d %B %Y')
    ax.set_xlabel('Success Ratio (1-FAR)')
    ax.set_ylabel('Probability of Detection (POD)')
    plt.title(titlestr, fontweight='bold')
    ax.tick_params(axis='both',length=5,width=1,which='major')

    # Add CSI colorbar
    cax = fig.add_axes([0.917, 0.2, 0.015, 0.65])
    fig.colorbar(CSI_lines,cax=cax,norm=norm,ticks=bounds,spacing='proportional',orientation='vertical',label='CSI')

    # Shrink current axis height by 10% on the bottom
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])

    # Put a legend below current axis
    ax.legend(loc='upper center', numpoints=2, bbox_to_anchor=(0.5, -0.1), fancybox=True, shadow=True, ncol=2)

    plt.savefig(filename+'.png',bbox_inches='tight')
    plt.close()



# Function to read METviewer data and replace reliability diagram
def reliability_diag(filename,plottype):

    print('Remaking reliability diagram with python')

    # Read METviewer data file
    with open(filename+'.data','r') as f:
        reader = csv.reader(f)

        data_list = []
        model_list = []
        baser_list = []   
        calib_list = []
        efreq_list = []   

        for row in reader:
            row_list = row[0].split('\t')

            # Build list of models to plot
            if row_list[1] not in model_list and row_list[1] != 'model':
                model_list.append(row_list[1])

            # Build list of sample climatologies to plot
            if row_list[4] == 'PSTD_BASER' and row_list[5] not in baser_list:
                if len(baser_list) >= 1 and row_list[5] == 'NA':
                  # pass
                  # baser_list.append(np.nan)
                    baser_list.append(baser_list[-1])
                else:
                    baser_list.append(row_list[5])

            # Build list for easier iteration later
            if row_list[0] != 'fcst_var':
                data_list.append(row_list)

        # Get fcst_var to use for title keys
        fcst_var_entry = row_list[0]
        for var_string in var_strings:
            if var_string in fcst_var_entry:
                fcst_var = var_string

        # Get threshold to use for title keys 
        for x in thresholds:
            if str(x) in fcst_var_entry:
                thresh = str(x)


      # Build list of stats
        for model in model_list:
            model_calib = []
            model_baser = []
            model_efreq = []

            for row in data_list:
                if row[1] == model and row[4] == 'PSTD_CALIBRATION':

                    if row[5] == 'NA':
                        model_calib.append(np.nan)
                    else:
                        model_calib.append(float(row[5]))
                elif row[1] == model and row[4] == 'PSTD_NI':
                    if row[5] == 'NA':
                        model_efreq.append(0)   # setting to zero instead of nan to avoid error with yscale('log')
                    else:
                        model_efreq.append(int(row[5]))

            calib_list.append(model_calib)
            efreq_list.append(model_efreq)



    # Define points for reliability lines
    if plottype == 'surrsvr':
        xcoord = [0.0,0.02,0.05,0.1,0.15,0.3,0.45,0.6]
     #  xcoord = [0.01,0.35,0.75,0.125,0.225,0.375,0.525]
    else:
        xcoord = [0.05,0.15,0.25,0.35,0.45,0.55,0.65,0.75,0.85,0.95]


    # Begin plotting
    fig = plt.figure(figsize=[8.5,8])
    ax = plt.subplot(111)

    # Add perfect reliability line
    relx = [0,1]
    rely = [0,1]
    rel_line, = ax.plot(relx,rely,"k-",linewidth=2)


    # Settings for HREFv3 reliability diagrams
    if str.upper(verf_job) == 'HREFV3':

        # Diagrams comparing HREF and HREFX for radar and surrogate svr
        if plottype[0:2] == 're' or plottype == 'surrsvr': 
            rel_legend = [hrefx['name']+' '+hrefx['nbmax']+' Prob',href['name']+' '+href['nbmax']+' Prob']
            rel_colors = [hrefx['pycolor'],href['pycolor']]
            rel_lty    = ['solid','solid']

        # Diagrams comparing HREF and HREFX for precip probabilities
        elif plottype[1:] == 'hpcp_prob': 
            rel_legend = [hrefx['name']+' '+hrefx['prob'],href['name']+' '+href['prob']]
            rel_colors = [hrefx['pycolor'],href['pycolor']]
            rel_lty    = ['solid','solid']


    # Add reliability data lines
    for ind in range(len(model_list)):

        rel_pts = calib_list[ind]
        clim = float(baser_list[ind])

        # Add no resolution line
        resx = [0,1]
        resy = [clim,clim]
        res_line, = ax.plot(resx,resy,color=rel_colors[ind],linestyle="--",linewidth=2)

        # Add no skill line
        skillx = [0,clim,1]
        skilly = [clim*0.5,clim,clim+((1-clim)*0.5)]
        skill_line, = ax.plot(skillx,skilly,color=rel_colors[ind],linestyle="--",linewidth=2)

        # Add reliability line
        rel_line, = ax.plot(xcoord,rel_pts,color=rel_colors[ind],linestyle=rel_lty[ind],label=rel_legend[ind],linewidth=3)
        rel_pts = ax.plot(xcoord,rel_pts,color=rel_colors[ind],marker="o",markersize=7)


    # Add main title and axis labels
    if plottype == 'surrsvr':
        titlestr = 'Surrogate Severe Reliability Diagram \n'+ \
                   region_strings[str.lower(region)]+' - Valid from '+vday1.strftime('%d %B %Y')+' to '+vday2.strftime('%d %B %Y')
    else:
        titlestr = 'Probability of '+str.upper(fcst_var)+' > '+thresh+' '+units[str.upper(fcst_var)]+' Reliability Diagram \n'+ \
                   region_strings[str.lower(region)]+' - Valid from '+vday1.strftime('%d %B %Y')+' to '+vday2.strftime('%d %B %Y')
    plt.axis([0,1,0,1])
    plt.xticks([0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0])
    plt.yticks([0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0])
    plt.xlabel("Forecast Probability")
    plt.ylabel("Observed Relative Frequency")
    plt.title(titlestr, fontweight='bold')


    # Define points for positive BSS shaded area
    shadex = [clim,1]
    shadey = [clim,clim+((1-clim)*0.5)]

    # Define points for no resolution positive BSS shaded area
    shadex2 = [0,clim]
    shadey2 = [0,clim]

    # Shade positive BSS areas
    plt.fill_between(shadex,shadey,1,facecolor='gray',alpha=0.25)
    plt.fill_between(shadex2,0,shadey2,facecolor='gray',alpha=0.25)


    # Add event histogram on inset
    axins = inset_axes(ax, width="100%", height="100%", bbox_to_anchor=(.085, .69, .45, .3), bbox_transform=ax.transAxes, loc=2)
    axins.set_zorder(10)
    axins.set_yscale('log')
  # axins.axis([0,1,10,10000000])
    axins.set_xticks([0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0])
    axins.set_xticklabels(["0","","0.2","","0.4","","0.6","","0.8","","1.0"])
  # axins.set_yticks([10,100,1000,10000,100000,1000000,10000000])

    # Add event histogram data lines
    for ind in range(len(model_list)):

        if ind == 0:
            xpts = [x - 0.005 for x in xcoord]
        elif ind == 1:
            xpts = [x + 0.005 for x in xcoord]
        else:
            xpts = xcoord

        efreq = efreq_list[ind]
        line, = axins.plot(xpts,efreq,color=rel_colors[ind],linestyle=rel_lty[ind],linewidth=3)
        pts = axins.plot(xpts,efreq,color=rel_colors[ind],marker="o",markersize=7)

    # Add inset axis labels
    axins.set_xlabel("Forecast Probability")
    axins.set_ylabel("# Forecasts")
    axins.grid(color="k")


    # Shrink current axis height by 10% on the bottom
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])

    # Put a legend below current axis
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), fancybox=True, shadow=True, ncol=2)

    plt.grid(color="k")

    plt.savefig(filename+'.png',bbox_inches='tight')
    plt.close()




# Function to run METviewer command
def run_metviewer(jobtype, xml):

    # Scorecard run command (only running on pre-specified days)
    if jobtype == 'scorecard':
        if scorecard_day:
            if run_mv:
                print('Running mv_'+jobtype+' on '+xml)
                os.system(METVIEWER_DIR+'/mv_'+jobtype+'_on_aws.sh '+aws_username+' '+PLOT_DIR+' '+xml+' '+threshold_xml+' > '+outfile) 
            else:
                print('Only writing '+xml)

    # Batch run command for performance and reliability diagrams
    # Needed to retrieve R data file for python plotting
    elif jobtype == 'performance' or jobtype == 'reliability':
        if run_mv:
            print('Running mv_batch on '+xml)
            os.system(METVIEWER_DIR+'/mv_batch_on_aws.sh '+aws_username+' '+PLOT_DIR+' '+xml+' -data > '+outfile) 
        else:
            print('Only writing '+xml)

    # Batch run command for all other plot types
    else:
        if run_mv:
            print('Running mv_'+jobtype+' on '+xml)
            os.system(METVIEWER_DIR+'/mv_'+jobtype+'_on_aws.sh '+aws_username+' '+PLOT_DIR+' '+xml+' > '+outfile) 
        else:
            print('Only writing '+xml)



# Function to move plots to appropriate directory
def organize_plots():

    # Set up directory for saving radar verification graphics 
    RADAR_DIR = os.path.join(PLOT_DIR,'radar')
    radar_list = ['REFC','REFD','RETOP']

    # Set up directory for saving surrogate severe verification graphics 
    SURRSVR_DIR = os.path.join(PLOT_DIR,'surrogate_severe')
    surrsvr_list = ['UH_SSPF']

    # Set up directory for saving precip verification graphics 
    PRECIP_DIR = os.path.join(PLOT_DIR,'precip')
    precip_list = ['APCP']

    # Set up directory for saving cape verification graphics 
    CAPE_DIR = os.path.join(PLOT_DIR,'cape')
    cape_list = ['CAPE']

    # Set up directory for saving ceiling & visibility verification graphics 
    CV_DIR = os.path.join(PLOT_DIR,'ceil_vis')
    cv_list = ['VIS','HGT']

    # Set up directory for saving surface and upper air verification graphics 
    SFC_DIR = os.path.join(PLOT_DIR,'sfc_upper')
    sfc_list = ['_sfc_','_upper_','mb_']


    directories = [SFC_DIR, RADAR_DIR, SURRSVR_DIR, PRECIP_DIR, CAPE_DIR, CV_DIR]
    string_lists = [sfc_list, radar_list, surrsvr_list, precip_list, cape_list, cv_list]


    for DEST_DIR in directories:

        # List all plots in directory
        plot_files = os.listdir(PLOT_DIR)

        i = directories.index(DEST_DIR)
        string_list = string_lists[i]

        for fil in plot_files:
            if any(x in fil for x in string_list):

                # Make sure destination directory exists
                if not os.path.exists(DEST_DIR):
                    os.makedirs(DEST_DIR)

                source = PLOT_DIR+'/'+fil
                dest = DEST_DIR+'/'+fil
                shutil.move(source,dest)

                with open(DEST_DIR+'/done.'+now.strftime('%Y%m%d'),"w") as f:
                    f.write('New verification graphics available')








############################### Get verification job and time period from command line  #################################################

# Begin working 
now = datetime.datetime.utcnow()


# Set AWS username
if os.environ['USER'] == 'Christopher.Macintosh':
   aws_username = cwmac
else:
   aws_username = str.lower(os.environ['USER'])


# Option to control whether to actually run METviewer scripts  
# Setting to False will write updated XMLs, but won't run METviewer
# (Allows you to see if substitutions are happening as expected)
run_mv = True
#run_mv = False

# List of months to help with checking for a monthly period
months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']


# Determine verification job
try:
    verf_job = str(sys.argv[1])
except IndexError:
    raise IndexError('need to define verification job (e.g., CAM, MESO, FV3CAM, HREFV3, HREF_MEM)')


# Determine verification period
try:
    verf_period = str(sys.argv[2])
except IndexError:
    raise IndexError('need to define verification period (e.g., past30days, exp_period, MMMYYYY)')


# Determine experiment name (needed for specified verification jobs)
try:
    verf_exp = str(sys.argv[3])
except IndexError:
    if str.upper(verf_job) == 'FV3CAM':
        raise IndexError('need to define FV3CAM experiment name (e.g., para_exp, lam_exp, da_exp)')
    else:
        verf_exp = None


# Handle special dates for specific verf_jobs
# Dates for FV3-CAM development
if str.upper(verf_job) == 'FV3CAM':

    # Initial date for current LAM-X experiment
    if str.lower(verf_exp) == 'lam_exp' and str.lower(verf_period) == 'exp_period':
        vday1 = datetime.datetime(2021,1,1,0,0)
        time_period = 'init'

    # Start/end dates for fall 2020 LAM-DA (only) experiment
    elif str.lower(verf_exp) == 'lam_exp' and str.lower(verf_period) == 'exp_period2020':
        vday1 = datetime.datetime(2020,10,15,12,0)
        exp_vday2 = datetime.datetime(2020,12,31,12,0)
        time_period = 'init'

    # Initial date for current LAM-DA experiment
    elif str.lower(verf_exp) == 'da_exp' and str.lower(verf_period) == 'exp_period':
        vday1 = datetime.datetime(2020,12,19,0,0)
        time_period = 'init'

    # Start/end dates for fall 2020 LAM-DA (only) experiment
    elif str.lower(verf_exp) == 'da_exp' and str.lower(verf_period) == 'da_only_exp':
        vday1 = datetime.datetime(2020,9,2,12,0)
        exp_vday2 = datetime.datetime(2020,12,18,12,0)
        time_period = 'init'

    # Start/end dates for spring/summer 2020 SAR-DA experiment
    elif str.lower(verf_exp) == 'sarda_exp' and str.lower(verf_period) == 'exp_period':
        vday1 = datetime.datetime(2020,5,8,12,00)         # updated to exclude forecasts before GSI bug fix
        exp_vday2 = datetime.datetime(2020,9,2,0,0)
        time_period = 'init'

    # Start/end dates for spring/summer 2020 SAR-X experiment
    elif str.lower(verf_exp) == 'sar_exp' and str.lower(verf_period) == 'exp_period':
        vday1 = datetime.datetime(2020,4,9,12,00)         # updated to exclude bad stats in early April
        exp_vday2 = datetime.datetime(2020,9,2,0,0)
        time_period = 'init'

    # Start/end dates for 2019-2020 SAR-X experiment
    elif str.lower(verf_exp) == 'sar_exp' and str.lower(verf_period) == 'exp_period':
        vday1 = datetime.datetime(2019,11,22,00,00)
        exp_vday2 = datetime.datetime(2020,4,1,00,00)
        time_period = 'init'


# Dates for HREFv3 evaluation
if str.upper(verf_job) == 'HREFV3':

    # Start/end dates for evaluation period HREFv2/v3 comparison
    if str.lower(verf_period) == 'eval_period':
        vday1 = datetime.datetime(2020,4,10,18,00)
        exp_vday2 = datetime.datetime(2020,7,21,21,00)
        time_period = 'valid'

    # Start/end dates for HREFv2/v3 comparison prior to eval period
    elif str.lower(verf_period) == 'prev_exp':
        vday1 = datetime.datetime(2020,1,22,00,00)
        exp_vday2 = datetime.datetime(2020,4,7,18,00)   # need to check this
        time_period = 'valid'


# Dates for NMMB/FV3 comparsion during HREFv3 evaluation
if str.upper(verf_job) == 'HREF_MEM':

    # Start/end dates for evaluation period NMMB/FV3 comparison
    if str.lower(verf_period) == 'eval_period':
        vday1 = datetime.datetime(2020,4,10,00,00)
        exp_vday2 = datetime.datetime(2020,7,21,21,00)
        time_period = 'valid'

    # Start/end dates for NMMB/FV3 comparison prior to eval period
    elif str.lower(verf_period) == 'prev_exp':
        vday1 = datetime.datetime(2020,1,22,00,00)
        exp_vday2 = datetime.datetime(2020,4,7,18,00)
        time_period = 'valid'



# Initial date for recent stats pages 
if str.lower(verf_period) == 'past30days': 
    vday1 = now + datetime.timedelta(days=-32)    # for doing a past 32 days
    time_period = 'valid'


# Dates for monthly plots
elif verf_period[0:3].capitalize() in months:
    time_period = 'valid'

    # Set first valid day as first day of month
    vday1 = datetime.datetime.strptime(verf_period,'%b%Y')
    # Determine number of days in the month
    ndays = calendar.monthrange(vday1.year,vday1.month)[1]
    # Set second vald day as final day of month 
    month_vday2 = vday1 + datetime.timedelta(days=ndays-1)


# Run a quick check to make sure start date has been set  
if 'vday1' not in globals():
    print('Initial verification date not initialized properly. Check logic for setting dates above. Exiting')
    exit()


# Define AWS subdirectory for data, scripts, plots
sub_dir = str.lower(verf_job)+'_'+str.lower(verf_period)


#################################### Set up directories for machine  #####################################################


# Get machine
machine, hostname = dawsonpy.get_machine()

# Set up working directories
if machine == 'WCOSS':
    VERIF_DIR = '/gpfs/'+hostname[0]+'d1/emc/meso/save/'+os.environ['USER']+'/CAM_verif'
    OUTPUT_DIR = '/gpfs/'+hostname[0]+'p2/ptmp/'+os.environ['USER']+'/cron.out'
elif machine == 'WCOSS_C':
    pass
elif machine == 'WCOSS_DELL_P3':
    TEMPLATE_HEAD = '/gpfs/dell2/emc/verification/save/Logan.Dawson/mv_emc_regional'
    METVIEWER_DIR = '/gpfs/dell2/emc/verification/noscrub/emc.metplus/METviewer_AWS'
    if verf_exp is None:
        WORK_DIR = '/gpfs/dell2/ptmp/'+os.environ['USER']+'/CAM_verif/'+verf_job+'/'+verf_period
    else:
        WORK_DIR = '/gpfs/dell2/ptmp/'+os.environ['USER']+'/CAM_verif/'+verf_job+'/'+verf_exp+'/'+verf_period


# Define path to template XML files
if str.upper(verf_job) == 'HREFV3':
    TEMPLATE_DIR = os.path.join(TEMPLATE_HEAD,'templates','href')
else:
    TEMPLATE_DIR = os.path.join(TEMPLATE_HEAD,'templates')

# Define threshold XML file for scorecards
threshold_xml = TEMPLATE_DIR+'/greenpurple_95-99.xml'


# Set up directory for temporary XML scripts
TEMP_DIR = os.path.join(WORK_DIR,'temp')
if os.path.exists(TEMP_DIR):
    shutil.rmtree(TEMP_DIR)
os.makedirs(TEMP_DIR)
temp_xml = TEMP_DIR+'/temp.xml'  

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




#################################### Dictonaries for Plot Settings  #####################################################


nam     = { 'name':'NAM'      , 'lty':'1' , 'color':'#0000ffFF' , 'pycolor':'blue'        , 'conus':'NAM'       , 'alaska':'NAM'    , 'hawaii':'NAM'    , 'puertorico':'NAM'    }
nam3    = { 'name':'NAM Nest' , 'lty':'1' , 'color':'#0000ffFF' , 'pycolor':'blue'        , 'conus':'CONUSNEST' , 'alaska':'AKNEST' , 'hawaii':'HINEST' , 'puertorico':'PRNEST' }
hrwnmmb = { 'name':'HRW NMMB' , 'lty':'1' , 'color':'#008cff'   , 'pycolor':'deepskyblue' , 'conus':'CONUSNMMB' , 'alaska':'AKNMMB' , 'hawaii':'HINMMB' , 'puertorico':'PRNMMB' }

rap     = { 'name':'RAP'      , 'lty':'1' , 'color':'#ff0000FF' , 'pycolor':'red'         , 'conus':'RAP'       , 'alaska':'RAPAK'  }
hrrr    = { 'name':'HRRR'     , 'lty':'1' , 'color':'#ff0000FF' , 'pycolor':'red'         , 'conus':'HRRR'      , 'alaska':'HRRRAK' }
hrwarw  = { 'name':'HRW ARW'  , 'lty':'1' , 'color':'#ff8c00'   , 'pycolor':'purple'      , 'conus':'CONUSARW'  , 'alaska':'AKARW'  , 'hawaii':'HIARW'  , 'puertorico':'PRARW'  }
hrwarw2 = { 'name':'HRW ARW2' , 'lty':'1' , 'color':'#8000ff'   , 'pycolor':'darkorange'  , 'conus':'CONUSARW2' , 'alaska':'AKARW2' , 'hawaii':'HIARW2' , 'puertorico':'PRARW2' }

gfs     = { 'name':'GFS'      , 'lty':'1' , 'color':'#000000'   , 'pycolor':'black'       , 'conus':'GFS'       , 'alaska':'GFS'    , 'hawaii':'GFS'    , 'puertorico':'GFS'    }
hrwfv3  = { 'name':'HRW FV3'  , 'lty':'1' , 'color':'#006400'   , 'pycolor':'darkgreen'   , 'conus':'CONUSFV3'  , 'alaska':'AKFV3'  , 'hawaii':'HIFV3'  , 'puertorico':'PRFV3'  }
sar     = { 'name':'FV3SAR'   , 'lty':'1' , 'color':'#000000'   , 'pycolor':'black'       , 'conus':'FV3SAR'    }
sarx    = { 'name':'FV3SARX'  , 'lty':'1' , 'color':'#b59b18'   , 'pycolor':'gold'        , 'conus':'FV3SARX'   }
sarda   = { 'name':'FV3SARDA' , 'lty':'2' , 'color':'#b59b18'   , 'pycolor':'gold'        , 'conus':'FV3SARDA'  }

lam     = { 'name':'FV3LAM'   , 'lty':'1' , 'color':'#000000'   , 'pycolor':'black'       , 'conus':'FV3LAM'    }
lamx    = { 'name':'FV3LAMX'  , 'lty':'1' , 'color':'#b59b18'   , 'pycolor':'gold'        , 'conus':'FV3LAMX'   }
lamda   = { 'name':'FV3LAMDA' , 'lty':'2' , 'color':'#b59b18'   , 'pycolor':'gold'        , 'conus':'FV3LAMDA'  }
lamdax  = { 'name':'FV3LAMDAX' , 'lty':'1' , 'color':'#006400'   , 'pycolor':'darkgreen'   , 'conus':'FV3LAMDAX'  }

href    = { 'name':'HREFv2'      , 'lty':'1'          , 'color':'#000000'   , 'pycolor':'black' ,
            'conus':'CONUSHREF'  , 'alaska':'AKHREF'  , 'hawaii':'HIHREF'   , 'puertorico':'PRHREF'  , 'pcp':'HREF'   , 'pcpnbmax':'APCPNBMAX' ,
            'avrg':'AVRG'        , 'mean':'MEAN'      , 'nbmax':'NBMAX' , 'pmmn':'PMMN' , 'prob':'PROB' }
hrefx   = { 'name':'HREFv3'      , 'lty':'1'          , 'color':'#ff0000FF' , 'pycolor':'red' ,
            'conus':'CONUSHREFX' , 'alaska':'AKHREFX' , 'hawaii':'HIHREFX'  , 'puertorico':'PRHREFX' , 'pcp':'HREFV3' , 'pcpnbmax':'APCPNBMAXV3' , 'pcpeas':'APCPEASV3' ,
            'avrg':'AVRG'        , 'mean':'MEAN'      , 'nbmax':'NBMAX' , 'pmmn':'PMMN' , 'prob':'PROB' , 'eas':'EAS' , 'lavg':'LAVG' , 'lpmm':'LPMM' }


# Define keys for variable long names in plot titles 
var_strings = {
    'APCP_01':'1-h Precipitation',
    'APCP_03':'3-h Precipitation',
    'APCP_06':'6-h Precipitation',
    'APCP_24':'24-h Precipitation',
    'CAPE':'CAPE',
    'HGT':'Ceiling',
    'REFC':'Composite Reflectivity',
    'REFD':'1-km AGL Reflectivity',
    'RETOP':'Echo Top Height',
    'UH_SSPF':'Surrogate Severe',
    'VIS':'Visibility'
}

# Define keys for variable units in reliability diagram titles 
units = {
    'APCP_01':'mm',
    'APCP_03':'mm',
    'APCP_06':'mm',
    'APCP_24':'mm',
    'CAPE':'J/kg',
    'HGT':'m',
    'REFC':'dBZ',
    'REFD':'dBZ',
    'RETOP':'m',
    'UH_SSPF':'%',
    'VIS':'m'
}

# Define keys for verification regions in plot titles
region_strings = { 
    'conus':'CONUS',
    'alaska':'Alaska',
    'east':'Eastern CONUS',
    'plains':'Great Plains',
    'west':'Western CONUS',
    'apl':'Appalachians',
    'gmc':'Gulf Coast',
    'grb':'Great Basin',
    'lmv':'Lower MS Valley',
    'mdw':'Midwest',
    'nec':'Northeast Coast',
    'nmt':'Northern Rocky Mts',
    'nak':'Northern Alaska',
    'npl':'Northern Plains',
    'nwc':'Northwest Coast',
    'sak':'Southern Alaska',
    'sec':'Southeast Coast',
    'smt':'Southern Rocky Mts',
    'spl':'Southern Plains',
    'swc':'Southwest Coast',
    'swd':'Southwest Desert',
    'spc':'SPC Outlook Areas',
    'day 1':'SPC 1200Z Day 1 Outlooks',
    'day 2':'SPC 1730Z Day 2 Outlooks',
    'day 3':'SPC 0800Z Day 3 Outlooks',
    'tstm':'SPC TSTM Outlook Areas',
    'mrgl':'SPC MRGL Outlook Areas',
    'slgt':'SPC SLGT Outlook Areas',
    'enh':'SPC ENH Outlook Areas',
    'mod':'SPC MOD Outlook Areas',
    'high':'SPC HIGH Outlook Areas',
}



#################################### Specs for Verification Jobs  #####################################################

# Run without event equalization by default
event_eq = 'false'
boot_repl = 1


# Specs for CAM graphics
if str.upper(verf_job) == 'CAM':

    doScorecard   = False
    doPerformance = True
    doReliability = False
    doFcstThresh  = True
    doValidHour   = True
    doFcstLead    = True
    doTimeSeries  = False

    event_eq = 'false'
    boot_repl = 1

    cycles = np.arange(0,19,6)
    fhrs = np.arange(0,61,6)
    runlength = 60

    # Single line per model settings
    ci_list     = 'c(\"none\",\"none\",\"none\",\"none\",\"none\")'
    signif_list = 'c(FALSE,FALSE,FALSE,FALSE,FALSE)'
    disp_list   = 'c(TRUE,TRUE,TRUE,TRUE,TRUE)'
    colors_list = 'c(\"'+hrwarw['color']+'\",\"'+hrwarw2['color']+'\",\"'+nam3['color']+'\",\"'+hrwnmmb['color']+'\",\"'+hrrr['color']+'\")'
    pch_list    = 'c(20,20,20,20,20)'
    type_list   = 'c(\"l\",\"l\",\"l\",\"l\",\"l\")'
    lty_list    = 'c('+hrwarw['lty']+','+hrwarw2['lty']+','+nam3['lty']+','+hrwnmmb['lty']+','+hrrr['lty']+')'
    lwd_list    = 'c(2.5,2.5,2.5,2.5,2.5)'
    con_list    = 'c(1,1,1,1,1)'
    order_list  = 'c(1,2,3,4,5)'
    legend_list = 'c(\"'+hrwarw['name']+'\",\"'+hrwarw2['name']+'\",\"'+nam3['name']+'\",\"'+hrwnmmb['name']+'\",\"'+hrrr['name']+'\")'

    # BCRMSE and Bias settings
    ci_list2     = 'c(\"none\",\"none\",\"none\",\"none\",\"none\",\"none\",\"none\",\"none\",\"none\",\"none\")'
    signif_list2 = 'c(FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE)'
    disp_list2   = 'c(TRUE,TRUE,TRUE,TRUE,TRUE,TRUE,TRUE,TRUE,TRUE,TRUE)'
    colors_list2 = 'c(\"'+hrwarw['color']+'\",\"'+hrwarw2['color']+'\",\"'+nam3['color']+'\",\"'+hrwnmmb['color']+'\",\"'+hrrr['color']+'\",\
                      \"'+hrwarw['color']+'\",\"'+hrwarw2['color']+'\",\"'+nam3['color']+'\",\"'+hrwnmmb['color']+'\",\"'+hrrr['color']+'\")'
    pch_list2    = 'c(17,17,17,17,17,20,20,20,20,20)'
    type_list2   = 'c(\"o\",\"o\",\"o\",\"o\",\"o\",\"o\",\"o\",\"o\",\"o\",\"o\")'
    lty_list2    = 'c('+hrwarw['lty']+','+hrwarw2['lty']+','+nam3['lty']+','+hrwnmmb['lty']+','+hrrr['lty']+','\
                       +hrwarw['lty']+','+hrwarw2['lty']+','+nam3['lty']+','+hrwnmmb['lty']+','+hrrr['lty']+')'
    lwd_list2    = 'c(2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5)'
    con_list2    = 'c(1,1,1,1,1,1,1,1,1,1)'
    order_list2  = 'c(1,2,3,4,5,6,7,8,9,10)'
    legend_list2 = 'c(\"'+hrwarw['name']+' - BCRMSE\",\"'+hrwarw2['name']+' - BCRMSE\",\"'+nam3['name']+' - BCRMSE\",\"'+hrwnmmb['name']+' - BCRMSE\",\"'+hrrr['name']+' - BCRMSE\",\
                      \"'+hrwarw['name']+' - Bias\"  ,\"'+hrwarw2['name']+' - Bias\"  ,\"'+nam3['name']+' - Bias\"  ,\"'+hrwnmmb['name']+' - Bias\"  ,\"'+hrrr['name']+' - Bias\")'

    # Vector wind settings
    pch_list3    = 'c(20,20,20,20,20,17,17,17,17,17)'
    legend_list3 = 'c(\"'+hrwarw['name']+' - Bias\" ,\"'+hrwarw2['name']+' - Bias\" ,\"'+nam3['name']+' - Bias\" ,\"'+hrwnmmb['name']+' - Bias\" ,\"'+hrrr['name']+' - Bias\", \
                      \"'+hrwarw['name']+' - RMSVE\",\"'+hrwarw2['name']+' - RMSVE\",\"'+nam3['name']+' - RMSVE\",\"'+hrwnmmb['name']+' - RMSVE\",\"'+hrrr['name']+' - RMSVE\")'

    # Diurnal cycle settings
    ci_list4     = 'c(\"none\",\"none\",\"none\",\"none\",\"none\",\"none\",\"none\",\"none\",\"none\",\"none\")'
    signif_list4 = 'c(FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE)'
    disp_list4   = 'c(TRUE,TRUE,TRUE,TRUE,TRUE,FALSE,FALSE,TRUE,FALSE,FALSE)'
    colors_list4 = 'c(\"'+hrwarw['color']+'\",\"'+hrwarw2['color']+'\",\"'+nam3['color']+'\",\"'+hrwnmmb['color']+'\",\"'+hrrr['color']+'\",\
                      \"'+gfs['color']+'\",\"'   +gfs['color']+'\",\"'    +gfs['color']+'\",\"' +gfs['color']+'\",\"'    +gfs['color']+'\")'
    pch_list4    = 'c(20,20,20,20,20,20,20,20,20,20)'
    type_list4   = 'c(\"l\",\"l\",\"l\",\"l\",\"l\",\"o\",\"o\",\"o\",\"o\",\"o\")'
    lty_list4    = 'c('+hrwarw['lty']+','+hrwarw2['lty']+','+nam3['lty']+','+hrwnmmb['lty']+','+hrrr['lty']+','\
                       +lamda['lty']+','+lamda['lty']+','+lamda['lty']+','+lamda['lty']+','+lamda['lty']+')'
    lwd_list4    = 'c(2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5)'
    con_list4    = 'c(1,1,1,1,1,1,1,1,1,1)'
    order_list4  = 'c(1,2,3,4,5,6,7,8,9,10)'
    legend_list4 = 'c(\"'+hrwarw['name']+'\",\"'+hrwarw2['name']+'\",\"'+nam3['name']+'\",\"'+hrwnmmb['name']+'\",\"'+hrrr['name']+'\", \
                      \"Obs\",\"Obs\",\"Obs\",\"Obs\",\"Obs\",\"Obs\")'



# Specs for Meso graphics
elif str.upper(verf_job) == 'MESO':

    doScorecard   = False
    doPerformance = True
    doReliability = False
    doFcstThresh  = True
    doValidHour   = True
    doFcstLead    = True
    doTimeSeries  = False

    event_eq = 'false'
    boot_repl = 1

    cycles = np.arange(0,19,6)
    fhrs = np.arange(0,85,6)
    runlength = 84

    # Single line per model settings
    ci_list     = 'c(\"none\",\"none\",\"none\")'
    signif_list = 'c(FALSE,FALSE,FALSE)'
    disp_list   = 'c(TRUE,TRUE,TRUE)'
    colors_list = 'c(\"'+gfs['color']+'\",\"'+nam['color']+'\",\"'+rap['color']+'\")'
    pch_list    = 'c(20,20,20)'
    type_list   = 'c(\"l\",\"l\",\"l\")'
    lty_list    = 'c('+gfs['lty']+','+nam['lty']+','+rap['lty']+')'
    lwd_list    = 'c(2.5,2.5,2.5)'
    con_list    = 'c(1,1,1)'
    order_list  = 'c(1,2,3)'
    legend_list = 'c(\"'+gfs['name']+'\",\"'+nam['name']+'\",\"'+rap['name']+'\")'

    # BCRMSE and Bias settings
    ci_list2     = 'c(\"none\",\"none\",\"none\",\"none\",\"none\",\"none\")'
    signif_list2 = 'c(FALSE,FALSE,FALSE,FALSE,FALSE,FALSE)'
    disp_list2   = 'c(TRUE,TRUE,TRUE,TRUE,TRUE,TRUE)'
    colors_list2 = 'c(\"'+gfs['color']+'\",\"'+nam['color']+'\",\"'+rap['color']+'\",\"'\
                         +gfs['color']+'\",\"'+nam['color']+'\",\"'+rap['color']+'\")'
    pch_list2    = 'c(17,17,17,20,20,20)'
    type_list2   = 'c(\"o\",\"o\",\"o\",\"o\",\"o\",\"o\")'
    lty_list2    = 'c('+gfs['lty']+','+nam['lty']+','+rap['lty']+','\
                       +gfs['lty']+','+nam['lty']+','+rap['lty']+')'
    lwd_list2    = 'c(2.5,2.5,2.5,2.5,2.5,2.5)'
    con_list2    = 'c(1,1,1,1,1,1)'
    order_list2  = 'c(1,2,3,4,5,6)'
    legend_list2 = 'c(\"'+gfs['name']+' - BCRMSE\",\"'+nam['name']+' - BCRMSE\","'+rap['name']+' - BCRMSE\","'\
                         +gfs['name']+' - Bias\",\"'  +nam['name']+' - Bias\","'  +rap['name']+' - Bias\")'

    # Vector wind settings
    pch_list3    = 'c(20,20,20,17,17,17)'
    legend_list3 = 'c(\"'+gfs['name']+' - Bias\",\"' +nam['name']+' - Bias\","' +rap['name']+' - Bias\","'\
                         +gfs['name']+' - RMSVE\",\"'+nam['name']+' - RMSVE\","'+rap['name']+' - RMSVE\")'

    # Diurnal cycle settings
    legend_list4 = 'c(\"'+gfs['name']+'\",\"'+nam['name']+'\",\"'+rap['name']+'\",\"Obs\",\"Obs\",\"Obs\")'
    ci_list4     = 'c(\"none\",\"none\",\"none\",\"none\",\"none\",\"none\")'
    signif_list4 = 'c(FALSE,FALSE,FALSE,FALSE,FALSE,FALSE)'
    disp_list4   = 'c(TRUE,TRUE,TRUE,FALSE,TRUE,FALSE)'
    colors_list4 = 'c(\"'+gfs['color']+'\",\"'+nam['color']+'\",\"'+rap['color']+'\",\"'\
                         +gfs['color']+'\",\"'+gfs['color']+'\",\"'  +gfs['color']+'\")'
    pch_list4    = 'c(20,20,20,20,20,20)'
    type_list4   = 'c(\"l\",\"l\",\"l\",\"o\",\"o\",\"o\")'
    lty_list4    = 'c('+gfs['lty']+','  +nam['lty']+','+rap['lty']+','\
                       +lamda['lty']+','+lamda['lty']+','+lamda['lty']+')'
    lwd_list4    = 'c(2.5,2.5,2.5,2.5,2.5,2.5)'
    con_list4    = 'c(1,1,1,1,1,1)'
    order_list4  = 'c(1,2,3,4,5,6)'



# Specs for FV3-CAM recent stats graphics
elif str.upper(verf_job) == 'FV3CAM' and str.lower(verf_exp) == 'para_exp':

    doScorecard   = True
    doPerformance = True
    doReliability = False
    doFcstThresh  = True
    doValidHour   = True
    doFcstLead    = True
    doTimeSeries  = False

    event_eq = 'false'
    boot_repl = 1000

    cycles = np.arange(0,13,12)
    fhrs = np.arange(0,61,12)
    if event_eq == 'false':
        runlength = 60
    elif event_eq == 'true':
        runlength = 48

    prods = ['FV3SAR','HRRR','CONUSNEST']
    paras = ['FV3SAR','FV3SARX','FV3SARDA']
    prod_labels = ['FV3SAR','HRRR','NAM-Nest']
    para_labels = ['FV3SAR','FV3SAR-X','FV3SAR-DA']

    prods = ['HRRR','CONUSNEST']
    paras = ['FV3LAM','FV3LAMDA','FV3LAMX']
    paras = ['FV3LAM','FV3LAMDA']
    prod_labels = ['HRRR','NAM-Nest']
    para_labels = ['FV3LAM','FV3LAM-DA','FV3LAM-X']
    para_labels = ['FV3LAM','FV3LAM-DA']

    # Single line per model settings
    ci_list     = 'c(\"none\",\"none\",\"none\",\"none\",\"none\",\"none\")'
    signif_list = 'c(FALSE,FALSE,FALSE,FALSE,FALSE,FALSE)'
    disp_list   = 'c(TRUE,TRUE,TRUE,TRUE,TRUE,TRUE)'
    colors_list = 'c(\"'+nam3['color']+'\",\"'+lam['color']+'\",\"'+lamda['color']+'\",\"'+lamx['color']+'\",\"'+gfs['color']+'\",\"'+hrrr['color']+'\")'
    pch_list    = 'c(20,20,20,20,20,20)'
    type_list   = 'c(\"l\",\"l\",\"l\",\"l\",\"l\",\"l\")'
    lty_list    = 'c('+nam3['lty']+','+lam['lty']+','+lamda['lty']+','+lamx['lty']+','+gfs['lty']+','+hrrr['lty']+')'
    lwd_list    = 'c(2.5,2.5,2.5,2.5,2.5,2.5)'
    con_list    = 'c(1,1,1,1,1,1)'
    order_list  = 'c(1,2,3,4,5,6)'
    legend_list = 'c(\"'+nam3['name']+'\",\"'+lam['name']+'\",\"'+lamda['name']+'\",\"'+lamx['name']+'\",\"'+gfs['name']+'\",\"'+hrrr['name']+'\")'

    # BCRMSE and Bias settings
    ci_list2     = 'c(\"none\",\"none\",\"none\",\"none\",\"none\",\"none\",\"none\",\"none\",\"none\",\"none\",\"none\",\"none\")'
    signif_list2 = 'c(FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE)'
    disp_list2   = 'c(TRUE,TRUE,TRUE,TRUE,TRUE,TRUE,TRUE,TRUE,TRUE,TRUE,TRUE,TRUE)'
    colors_list2 = 'c(\"'+nam3['color']+'\",\"'+lam['color']+'\",\"'+lamda['color']+'\",\"'+lamx['color']+'\",\"'+gfs['color']+'\",\"'+hrrr['color']+'\",\
                      \"'+nam3['color']+'\",\"'+lam['color']+'\",\"'+lamda['color']+'\",\"'+lamx['color']+'\",\"'+gfs['color']+'\",\"'+hrrr['color']+'\")'
    pch_list2    = 'c(17,17,17,17,17,17,20,20,20,20,20,20)'
    type_list2   = 'c(\"o\",\"o\",\"o\",\"o\",\"o\",\"o\",\"o\",\"o\",\"o\",\"o\",\"o\",\"o\")'
    lty_list2    = 'c('+nam3['lty']+','+lam['lty']+','+lamda['lty']+','+lamx['lty']+','+gfs['lty']+','+hrrr['lty']+','\
                       +nam3['lty']+','+lam['lty']+','+lamda['lty']+','+lamx['lty']+','+gfs['lty']+','+hrrr['lty']+')'
    lwd_list2    = 'c(2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5)'
    con_list2    = 'c(1,1,1,1,1,1,1,1,1,1,1,1)'
    order_list2  = 'c(1,2,3,4,5,6,7,8,9,10,11,12)'
    legend_list2 = 'c(\"'+nam3['name']+' - BCRMSE\",\"'+lam['name']+' - BCRMSE\",\"'+lamda['name']+' - BCRMSE\",\"'+lamx['name']+' - BCRMSE\",\"'+gfs['name']+' - BCRMSE\",\"'+hrrr['name']+' - BCRMSE\", \
                      \"'+nam3['name']+' - Bias\",\"'  +lam['name']+' - Bias\",\"'  +lamda['name']+' - Bias\",\"'  +lamx['name']+' - Bias\",\"'  +gfs['name']+' - Bias\",\"'  +hrrr['name']+' - Bias\")'

    # Vector wind settings
    pch_list3    = 'c(20,20,20,20,20,20,17,17,17,17,17,17)'
    legend_list3 = 'c(\"'+nam3['name']+' - Bias\",\"' +lam['name']+' - Bias\",\"' +lamda['name']+' - Bias\",\"' +lamx['name']+' - Bias\",\"' +gfs['name']+' - Bias\",\"' +hrrr['name']+' - Bias\", \
                      \"'+nam3['name']+' - RMSVE\",\"'+lam['name']+' - RMSVE\",\"'+lamda['name']+' - RMSVE\",\"'+lamx['name']+' - RMSVE\",\"'+gfs['name']+' - RMSVE\",\"'+hrrr['name']+' - RMSVE\")'

    # Diurnal cycle settings
    ci_list4     = 'c(\"none\",\"none\",\"none\",\"none\",\"none\",\"none\",\"none\",\"none\",\"none\",\"none\",\"none\",\"none\")'
    signif_list4 = 'c(FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE)'
    disp_list4   = 'c(TRUE,TRUE,TRUE,TRUE,TRUE,TRUE,FALSE,TRUE,FALSE,FALSE,FALSE,FALSE)'
    colors_list4 = 'c(\"'+nam3['color']+'\",\"'+lam['color']+'\",\"'+lamda['color']+'\",\"'+lamx['color']+'\",\"'+gfs['color']+'\",\"'+hrrr['color']+'\",\
                      \"'+gfs['color']+'\",\"' +gfs['color']+'\",\"'+gfs['color']+'\",\"'  +gfs['color']+'\",\"' +gfs['color']+'\",\"'+gfs['color']+'\")'
    pch_list4    = 'c(20,20,20,20,20,20,20,20,20,20,20,20)'
    type_list4   = 'c(\"l\",\"l\",\"l\",\"l\",\"l\",\"l\",\"o\",\"o\",\"o\",\"o\",\"o\",\"o\")'
    lty_list4    = 'c('+nam3['lty']+','+lam['lty']+','+lamda['lty']+','+lamx['lty']+','+gfs['lty']+','+hrrr['lty']+','\
                       +lamda['lty']+','+lamda['lty']+','+lamda['lty']+','+lamda['lty']+','+lamda['lty']+','+lamda['lty']+')'
    lwd_list4    = 'c(2.5,2.5,2.5,2.5)'
    con_list4    = 'c(1,1,1,1)'
    order_list4  = 'c(1,2,3,4)'
    legend_list4 = 'c(\"'+nam3['name']+'\",\"'+lam['name']+'\",\"'+lamda['name']+'\",\"'+lamx['name']+'\",\"'+gfs['name']+'\",\"'+hrrr['name']+'\", \
                      \"Obs\",\"Obs\",\"Obs\",\"Obs\",\"Obs\",\"Obs\")'



# Specs for FV3-CAM LAM-DA experiment (3 models) graphics
elif (str.upper(verf_job) == 'FV3CAM' and str.lower(verf_exp) == 'da_exp'):

    doScorecard   = True
    doPerformance = True
    doReliability = False
    doFcstThresh  = True
    doValidHour   = True
    doFcstLead    = True
    doTimeSeries  = True

    event_eq    = 'true'
    boot_repl   = 1000

    cycles = np.arange(0,13,12)
    fhrs = np.arange(0,61,12)
    runlength = 60

    prods = ['FV3LAM','FV3LAMDA']
    paras = ['FV3LAMDA','FV3LAMDAX']
    prod_labels = ['FV3LAM','FV3LAM-DA']
    para_labels = ['FV3LAM-DA','FV3LAM-DA-X']

    # Single line per model settings
    legend_list = 'c(\"'+lam['name']+'\",\"'+lamda['name']+'\",\"'+lamdax['name']+'\")'
    ci_list     = 'c(\"none\",\"none\",\"none\")'
    signif_list = 'c(FALSE,FALSE,FALSE)'
    disp_list   = 'c(TRUE,TRUE,TRUE)'
    colors_list = 'c(\"'+lam['color']+'\",\"'+lamda['color']+'\",\"'+lamdax['color']+'\")'
    pch_list    = 'c(20,20,20)'
    type_list   = 'c(\"l\",\"l\",\"l\")'
    lty_list    = 'c('+lam['lty']+','+lamda['lty']+','+lamdax['lty']+')'
    lwd_list    = 'c(2.5,2.5,2.5)'
    con_list    = 'c(1,1,1)'
    order_list  = 'c(1,2,3)'

    # BCRMSE and Bias settings
    legend_list2 = 'c(\"'+lam['name']+' - BCRMSE\",\"'+lamda['name']+' - BCRMSE\","'+lamdax['name']+' - BCRMSE\","'\
                         +lam['name']+' - Bias\",\"'  +lamda['name']+' - Bias\","'  +lamdax['name']+' - Bias\")'
    ci_list2     = 'c(\"none\",\"none\",\"none\",\"none\",\"none\",\"none\")'
    signif_list2 = 'c(FALSE,FALSE,FALSE,FALSE,FALSE,FALSE)'
    disp_list2   = 'c(TRUE,TRUE,TRUE,TRUE,TRUE,TRUE)'
    colors_list2 = 'c(\"'+lam['color']+'\",\"'+lamda['color']+'\",\"'+lamdax['color']+'\",\"'\
                         +lam['color']+'\",\"'+lamda['color']+'\",\"'+lamdax['color']+'\")'
    pch_list2    = 'c(17,17,17,20,20,20)'
    type_list2   = 'c(\"o\",\"o\",\"o\",\"o\",\"o\",\"o\")'
    lty_list2    = 'c('+lam['lty']+','+lamda['lty']+','+lamdax['lty']+','\
                       +lam['lty']+','+lamda['lty']+','+lamdax['lty']+')'
    lwd_list2    = 'c(2.5,2.5,2.5,2.5,2.5,2.5)'
    con_list2    = 'c(1,1,1,1,1,1)'
    order_list2  = 'c(1,2,3,4,5,6)'

    # Vector wind settings
    legend_list3 = 'c(\"'+lam['name']+' - Bias\",\"' +lamda['name']+' - Bias\","' +lamdax['name']+' - Bias\","'\
                         +lam['name']+' - RMSVE\",\"'+lamda['name']+' - RMSVE\","'+lamdax['name']+' - RMSVE\")'
    pch_list3    = 'c(20,20,20,17,17,17)'

    # Diurnal cycle settings
    legend_list4 = 'c(\"'+lam['name']+'\",\"'+lamda['name']+'\",\"'+lamdax['name']+'\",\"Obs\",\"Obs\",\"Obs\")'
    ci_list4     = 'c(\"none\",\"none\",\"none\",\"none\",\"none\",\"none\")'
    signif_list4 = 'c(FALSE,FALSE,FALSE,FALSE,FALSE,FALSE)'
    disp_list4   = 'c(TRUE,TRUE,TRUE,FALSE,TRUE,FALSE)'
    colors_list4 = 'c(\"'+lam['color']+'\",\"'+lamda['color']+'\",\"'+lamdax['color']+'\",\"'\
                         +gfs['color']+'\",\"'+gfs['color']+'\",\"'  +gfs['color']+'\")'
    pch_list4    = 'c(20,20,20,20,20,20)'
    type_list4   = 'c(\"l\",\"l\",\"l\",\"o\",\"o\",\"o\")'
    lty_list4    = 'c('+lam['lty']+','  +lamda['lty']+','+lamdax['lty']+','\
                       +lamda['lty']+','+lamda['lty']+','+lamda['lty']+')'
    lwd_list4    = 'c(2.5,2.5,2.5,2.5,2.5,2.5)'
    con_list4    = 'c(1,1,1,1,1,1)'
    order_list4  = 'c(1,2,3,4,5,6)'



# Specs for FV3-CAM LAM-X experiment (2 models) graphics
elif (str.upper(verf_job) == 'FV3CAM' and 
      str.lower(verf_exp) != 'para_exp' and 
      str.lower(verf_exp) != 'da_exp'):

    doScorecard   = True
    doPerformance = True
    doReliability = False
    doFcstThresh  = True
    doValidHour   = True
    doFcstLead    = True
    doTimeSeries  = True

    doScorecard   = False
    doPerformance = False
    doReliability = False
    doFcstThresh  = False
    doValidHour   = False
    doFcstLead    = True
    doTimeSeries  = False
    event_eq    = 'true'
    boot_repl   = 1000

    cycles = np.arange(0,13,12)
    fhrs = np.arange(0,61,12)
    runlength = 60

    # Settings specific to SAR-X experiment
    if str.lower(verf_exp) == 'sar_exp':
        prods = ['FV3SAR']
        paras = ['FV3SARX']
        prod_labels = ['FV3SAR']
        para_labels = ['FV3SAR-X']

        legend_list = 'c(\"'+sar['name']+'\",\"'+sarx['name']+'\")'

        legend_list2 = 'c(\"'+sar['name']+' - BCRMSE\",\"'+sarx['name']+' - BCRMSE\","'+sar['name']+' - Bias\",\"'+sarx['name']+' - Bias\")'

        legend_list3 = 'c(\"'+sar['name']+' - Bias\",\"'+sarx['name']+' - Bias\","'+sar['name']+' - RMSVE\",\"'+sarx['name']+' - RMSVE\")'

        legend_list4 = 'c(\"'+sar['name']+'\",\"'+sarx['name']+'\",\"Obs\",\"Obs\")'

    # Settings specific to LAM-X experiment
    elif str.lower(verf_exp) == 'lam_exp':
        prods = ['FV3LAM']
        paras = ['FV3LAMX']
        prod_labels = ['FV3LAM']
        para_labels = ['FV3LAM-X']

        legend_list = 'c(\"'+lam['name']+'\",\"'+lamx['name']+'\")'

        legend_list2 = 'c(\"'+lam['name']+' - BCRMSE\",\"'+lamx['name']+' - BCRMSE\","'+lam['name']+' - Bias\",\"'+lamx['name']+' - Bias\")'

        legend_list3 = 'c(\"'+lam['name']+' - Bias\",\"'+lamx['name']+' - Bias\","'+lam['name']+' - RMSVE\",\"'+lamx['name']+' - RMSVE\")'

        legend_list4 = 'c(\"'+lam['name']+'\",\"'+lamx['name']+'\",\"Obs\",\"Obs\")'

    # Settings specific to SAR-DA experiment
    elif str.lower(verf_exp) == 'sarda_exp':
        prods = ['FV3SARX']
        paras = ['FV3SARDA']
        prod_labels = ['FV3SAR-X']
        para_labels = ['FV3SAR-DA']

        legend_list = 'c(\"'+sar['name']+'\",\"'+sarda['name']+'\")'

        legend_list2 = 'c(\"'+sar['name']+' - BCRMSE\",\"'+sarda['name']+' - BCRMSE\","'+sar['name']+' - Bias\",\"'+sarda['name']+' - Bias\")'

        legend_list3 = 'c(\"'+sar['name']+' - Bias\",\"'+sarda['name']+' - Bias\","'+sar['name']+' - RMSVE\",\"'+sarda['name']+' - RMSVE\")'

        legend_list4 = 'c(\"'+sar['name']+'\",\"'+sarda['name']+'\",\"Obs\",\"Obs\")'


    # Single line per model settings
    ci_list     = 'c(\"none\",\"none\")'
    signif_list = 'c(FALSE,FALSE)'
    disp_list   = 'c(TRUE,TRUE)'
    colors_list = 'c(\"'+lam['color']+'\",\"'+lamx['color']+'\")'
    pch_list    = 'c(20,20)'
    type_list   = 'c(\"l\",\"l\")'
    lty_list    = 'c('+lam['lty']+','+lamx['lty']+')'
    lwd_list    = 'c(2.5,2.5)'
    con_list    = 'c(1,1)'
    order_list  = 'c(1,2)'

    # BCRMSE and Bias settings
    ci_list2     = 'c(\"none\",\"none\",\"none\",\"none\")'
    signif_list2 = 'c(FALSE,FALSE,FALSE,FALSE)'
    disp_list2   = 'c(TRUE,TRUE,TRUE,TRUE)'
    colors_list2 = 'c(\"'+lam['color']+'\",\"'+lamx['color']+'\",\"'+lam['color']+'\",\"'+lamx['color']+'\")'
    pch_list2    = 'c(17,17,20,20)'
    type_list2   = 'c(\"o\",\"o\",\"o\",\"o\")'
    lty_list2    = 'c('+lam['lty']+','+lamx['lty']+','+lam['lty']+','+lamx['lty']+')'
    lwd_list2    = 'c(2.5,2.5,2.5,2.5)'
    con_list2    = 'c(1,1,1,1)'
    order_list2  = 'c(1,2,3,4)'

    # Vector wind settings
    pch_list3    = 'c(20,20,17,17)'

    # Diurnal cycle settings
    ci_list4     = 'c(\"none\",\"none\",\"none\",\"none\")'
    signif_list4 = 'c(FALSE,FALSE,FALSE,FALSE)'
    disp_list4   = 'c(TRUE,TRUE,FALSE,TRUE)'
    colors_list4 = 'c(\"'+lam['color']+'\",\"'+lamx['color']+'\",\"'+gfs['color']+'\",\"'+gfs['color']+'\")'
    pch_list4    = 'c(20,20,20,20)'
    type_list4   = 'c(\"l\",\"l\",\"o\",\"o\")'
    lty_list4    = 'c('+lam['lty']+','+lamx['lty']+','+lamda['lty']+','+lamda['lty']+')'
    lwd_list4    = 'c(2.5,2.5,2.5,2.5)'
    con_list4    = 'c(1,1,1,1)'
    order_list4  = 'c(1,2,3,4)'



# Specs for FV3/NMMB graphics
elif str.upper(verf_job) == 'HREF_MEM':

    doScorecard   = True
    doPerformance = True
    doReliability = False
    doFcstThresh  = True
    doValidHour   = True
    doFcstLead    = True
    doTimeSeries  = False

    event_eq    = 'false'
    boot_repl   = 1000

    cycles = np.arange(0,13,12)
    fhrs = np.arange(0,49,6)
    if event_eq == 'false':
        runlength = 60
    elif event_eq == 'true':
        runlength = 48

    prods = ['CONUSNMMB','AKNMMB']
    paras = ['CONUSFV3','AKFV3']
    prod_labels = ['HiResW-NMMB']*len(prods)
    para_labels = ['HiResW-FV3']*len(paras)

    # Single line per model settings
    ci_list     = 'c(\"boot\",\"boot\")'
    signif_list = 'c(FALSE,FALSE)'
    disp_list   = 'c(TRUE,TRUE)'
    colors_list = 'c(\"'+hrwfv3['color']+'\",\"'+hrwnmmb['color']+'\")'
    pch_list    = 'c(20,20)'
    type_list   = 'c(\"l\",\"l\")'
    lty_list    = 'c('+hrwfv3['lty']+','+hrwnmmb['lty']+')'
    lwd_list    = 'c(2.5,2.5)'
    con_list    = 'c(1,1)'
    order_list  = 'c(1,2)'
    legend_list = 'c(\"'+hrwfv3['name']+'\",\"'+hrwnmmb['name']+'\")'

    # BCRMSE and Bias settings
    ci_list2     = 'c(\"boot\",\"boot\",\"boot\",\"boot\")'
    signif_list2 = 'c(FALSE,FALSE,FALSE,FALSE)'
    disp_list2   = 'c(TRUE,TRUE,TRUE,TRUE)'
    colors_list2 = 'c(\"'+hrwfv3['color']+'\",\"'+hrwnmmb['color']+'\",\"'+hrwfv3['color']+'\",\"'+hrwnmmb['color']+'\")'
    pch_list2    = 'c(17,17,20,20)'
    type_list2   = 'c(\"o\",\"o\",\"o\",\"o\")'
  # lty_list2    = 'c('+hrwfv3['lty']+','+hrwnmmb['lty']+','+hrwfv3['lty']+','+hrwnmmb['lty']+')'
    lty_list2    = 'c(2,2,1,1)'
    lwd_list2    = 'c(2.5,2.5,2.5,2.5)'
    con_list2    = 'c(1,1,1,1)'
    order_list2  = 'c(1,2,3,4)'
    legend_list2 = 'c(\"'+hrwfv3['name']+' - BCRMSE\",\"'+hrwnmmb['name']+' - BCRMSE\",\"'+hrwfv3['name']+' - Bias\",\"'+hrwnmmb['name']+' - Bias\")'

    # Vector wind settings
    pch_list3    = 'c(20,20,17,17)'
    legend_list3 = 'c(\"'+hrwfv3['name']+' - Bias\",\"'+hrwnmmb['name']+' - Bias\",\"'+hrwfv3['name']+' - RMSVE\",\"'+hrwnmmb['name']+' - RMSVE\")'

    # Diurnal cycle settings
    ci_list4     = 'c(\"none\",\"none\",\"none\",\"none\")'
    signif_list4 = 'c(FALSE,FALSE,FALSE,FALSE)'
    disp_list4   = 'c(TRUE,TRUE,FALSE,TRUE)'
    colors_list4 = 'c(\"'+hrwfv3['color']+'\",\"'+hrwnmmb['color']+'\",\"'+gfs['color']+'\",\"'+gfs['color']+'\")'
    pch_list4    = 'c(20,20,20,20)'
    type_list4   = 'c(\"l\",\"l\",\"o\",\"o\")'
    lty_list4    = 'c(1,1,2,2)'
    lwd_list4    = 'c(2.5,2.5,2.5,2.5)'
    con_list4    = 'c(1,1,1,1)'
    order_list4  = 'c(1,2,3,4)'
    legend_list4 = 'c(\"'+hrwfv3['name']+'\",\"'+hrwnmmb['name']+'\",\"Obs\",\"Obs\")'



# Specs for HREFv3 evaluation graphics
elif str.upper(verf_job) == 'HREFV3':

    doScorecard   = True
    doPerformance = True
    doReliability = True
    doFcstThresh  = True
    doValidHour   = True
    doFcstLead    = True
    doTimeSeries  = False

    event_eq    = 'true'
    boot_repl   = 1000

    cycles = np.arange(0,13,12)
    fhrs = np.arange(0,49,6)
    if event_eq == 'false':
        runlength = 48
    elif event_eq == 'true':
        runlength = 36

    prods = ['CONUSHREF_PMMN']
    paras = ['CONUSHREFX_PMMN']
    prod_labels = ['HREFv2-PMMN']
    para_labels = ['HREFv3-PMMN']

    # Single line per model settings
    ci_list     = 'c(\"boot\",\"boot\")'
    signif_list = 'c(FALSE,FALSE)'
    disp_list   = 'c(TRUE,TRUE)'
    colors_list = 'c(\"'+hrefx['color']+'\",\"'+href['color']+'\")'
    pch_list    = 'c(20,20)'
    type_list   = 'c(\"l\",\"l\")'
    lty_list    = 'c('+hrefx['lty']+','+href['lty']+')'
    lwd_list    = 'c(2.5,2.5)'
    con_list    = 'c(1,1)'
    order_list  = 'c(1,2)'
    legend_list = 'c(\"'+hrefx['name']+' '+hrefx['pmmn']+'\",\"'+href['name']+' '+href['pmmn']+'\")'

    # BCRMSE and Bias settings
    ci_list2     = 'c(\"boot\",\"boot\",\"boot\",\"boot\")'
    signif_list2 = 'c(FALSE,FALSE,FALSE,FALSE)'
    disp_list2   = 'c(TRUE,TRUE,TRUE,TRUE)'
    colors_list2 = 'c(\"'+href['color']+'\",\"'+hrefx['color']+'\",\"'+href['color']+'\",\"'+hrefx['color']+'\")'
    pch_list2    = 'c(17,17,20,20)'
    type_list2   = 'c(\"o\",\"o\",\"o\",\"o\")'
    lty_list2    = 'c(2,2,1,1)'
    lwd_list2    = 'c(2.5,2.5,2.5,2.5)'
    con_list2    = 'c(1,1,1,1)'
    order_list2  = 'c(1,2,3,4)'
    legend_list2 = 'c(\"'+href['name']+' '+href['mean']+' - BCRMSE\",\"'+hrefx['name']+' '+hrefx['mean']+' - BCRMSE\",\"'+href['name']+' '+href['mean']+' - Bias\",\"'+hrefx['name']+' '+hrefx['mean']+' - Bias\")'

    # Vector wind settings
    pch_list3    = 'c(20,20,17,17)'
    legend_list3 = 'c(\"'+hrefx['name']+' - Bias\",\"'+href['name']+' - Bias\",\"'+hrefx['name']+' - RMSVE\",\"'+href['name']+' - RMSVE\")'

    # Diurnal cycle (2 forecast products) settings
    ci_list4     = 'c(\"none\",\"none\",\"none\",\"none\")'
    signif_list4 = 'c(FALSE,FALSE,FALSE,FALSE)'
    disp_list4   = 'c(TRUE,TRUE,FALSE,TRUE)'
    colors_list4 = 'c(\"'+href['color']+'\",\"'+hrefx['color']+'\",\"'+gfs['color']+'\",\"'+gfs['color']+'\")'
    pch_list4    = 'c(20,20,20,20)'
    type_list4   = 'c(\"l\",\"l\",\"o\",\"o\")'
    lty_list4    = 'c('+href['lty']+','+hrefx['lty']+',2,2)'
    lwd_list4    = 'c(2.5,2.5,2.5,2.5)'
    con_list4    = 'c(1,1,1,1)'
    order_list4  = 'c(1,2,3,4)'
    legend_list4 = 'c(\"'+href['name']+' '+href['mean']+'\",\"'+hrefx['name']+' '+hrefx['mean']+'\",\"Obs\",\"Obs\")'

    # Diurnal cycle (3 forecast products) settings
    ci_list5     = 'c(\"none\",\"none\",\"none\",\"none\",\"none\",\"none\")'
    signif_list5 = 'c(FALSE,FALSE,FALSE,FALSE,FALSE,FALSE)'
    disp_list5   = 'c(TRUE,TRUE,TRUE,FALSE,TRUE,FALSE)'
    colors_list5 = 'c(\"dummy\")'
    pch_list5    = 'c(20,20,20,20,20,20)'
    type_list5   = 'c(\"l\",\"l\",\"l\",\"o\",\"o\",\"o\")'
    lty_list5    = 'c('+href['lty']+','+hrefx['lty']+','+href['lty']+',2,2,2)'
    lwd_list5    = 'c(2.5,2.5,2.5,2.5,2.5,2.5)'
    con_list5    = 'c(1,1,1,1,1,1)'
    order_list5  = 'c(1,2,3,4,5,6)'
    legend_list5 = 'c(\"dummy\")'

    # Precip plots (3 forecast product) settings
    ci_list6     = 'c(\"boot\",\"boot\",\"boot\")'
    signif_list6 = 'c(FALSE,FALSE,FALSE)'
    disp_list6   = 'c(TRUE,TRUE,TRUE)'
    colors_list6 = 'c(\"'+href['color']+'\",\"'+hrefx['color']+'\",\"'+href['color']+'\")'
    pch_list6    = 'c(20,20,20)'
    type_list6   = 'c(\"l\",\"l\",\"l\")'
    lty_list6    = 'c('+href['lty']+','+hrefx['lty']+','+href['lty']+')'
    lwd_list6    = 'c(2.5,2.5,2.5)'
    con_list6    = 'c(1,1,1)'
    order_list6  = 'c(1,2,3)'
    legend_list6 = 'c(\"dummy\")'

    # Diurnal cycle (5 forecast products) settings
    ci_list7     = 'c(\"none\",\"none\",\"none\",\"none\",\"none\",\"none\",\"none\",\"none\",\"none\",\"none\")'
    signif_list7 = 'c(FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE)'
    disp_list7   = 'c(TRUE,TRUE,TRUE,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,TRUE)'
    colors_list7 = 'c(\"'+hrefx['color']+'\",\"'+nam3['color']+'\",\"'+nam3['color']+'\",\"'+href['color']+'\",\"'+hrefx['color']+'\",\"'+gfs['color']+'\",\"'+gfs['color']+'\",\"'+gfs['color']+'\",\"'+gfs['color']+'\",\"'+gfs['color']+'\")'
    pch_list7    = 'c(20,20,20,20,20,20,20,20,20,20)'
    type_list7   = 'c(\"l\",\"l\",\"l\",\"o\",\"o\",\"o\")'
    lty_list7    = 'c(2,2,1,1,1,2,2,2,2,2)'
    lwd_list7    = 'c(2.5,2.5,2.5,2.5,2.5,2.5)'
    con_list7    = 'c(1,1,1,1,1,1,1,1,1,1)'
    order_list7  = 'c(1,2,3,4,5,6,7,8,9,10)'
    legend_list7 = 'c(\"dummy\")'
    legend_list7 = 'c(\"'+hrefx['name']+' '+hrefx['avrg']+'\",\"'+hrefx['name']+' '+hrefx['lavg']+'\",\"'+hrefx['name']+' '+hrefx['lpmm']+'\",\"'+hrefx['name']+' '+hrefx['mean']+'\",\"'+hrefx['name']+' '+hrefx['pmmn']+'\",\"Obs\",\"Obs\",\"Obs\",\"Obs",\"Obs\")'

    # Precip plots (5 forecast product) settings
    # avrg, lavg, lpmm, mean, pmmn
                        # red, blue, blue, black, red
    ci_list8     = 'c(\"boot\",\"boot\",\"boot\",\"boot\",\"boot\")'
    signif_list8 = 'c(FALSE,FALSE,FALSE,FALSE,FALSE)'
    disp_list8   = 'c(TRUE,TRUE,TRUE,TRUE,TRUE)'
    colors_list8 = 'c(\"'+hrefx['color']+'\",\"'+nam3['color']+'\",\"'+nam3['color']+'\",\"'+href['color']+'\",\"'+hrefx['color']+'\")'
    pch_list8    = 'c(20,20,20,20,20)'
    type_list8   = 'c(\"l\",\"l\",\"l\",\"l\",\"l\")'
    lty_list8    = 'c(2,2,1,1,1)'
    lwd_list8    = 'c(2.5,2.5,2.5,2.5,2.5)'
    con_list8    = 'c(1,1,1,1,1)'
    order_list8  = 'c(1,2,3,4,5)'
    legend_list8 = 'c(\"dummy\")'
    legend_list8 = 'c(\"'+hrefx['name']+' '+hrefx['avrg']+'\",\"'+hrefx['name']+' '+hrefx['lavg']+'\",\"'+hrefx['name']+' '+hrefx['lpmm']+'\",\"'+hrefx['name']+' '+hrefx['mean']+'\",\"'+hrefx['name']+' '+hrefx['pmmn']+'\")'


else:
   print("Invalid verification job name used. Plot specs will be undefined. Use appropriate 'verf_job' string or add new definition. Exiting.")
   exit()



try:
    ci_list5     
except:
    ci_list5     = 'dummy'
    signif_list5 = 'dummy'
    disp_list5   = 'dummy'
    colors_list5 = 'dummy'
    pch_list5    = 'dummy'
    type_list5   = 'dummy'
    lty_list5    = 'dummy'
    lwd_list5    = 'dummy'
    con_list5    = 'dummy'
    order_list5  = 'dummy'
    legend_list5 = 'dummy'

try:
    ci_list6
except:
    ci_list6     = 'dummy'
    signif_list6 = 'dummy'
    disp_list6   = 'dummy'
    colors_list6 = 'dummy'
    pch_list6    = 'dummy'
    type_list6   = 'dummy'
    lty_list6    = 'dummy'
    lwd_list6    = 'dummy'
    con_list6    = 'dummy'
    order_list6  = 'dummy'
    legend_list6 = 'dummy'

try:
    ci_list7
except:
    ci_list7     = 'dummy'
    signif_list7 = 'dummy'
    disp_list7   = 'dummy'
    colors_list7 = 'dummy'
    pch_list7    = 'dummy'
    type_list7   = 'dummy'
    lty_list7    = 'dummy'
    lwd_list7    = 'dummy'
    con_list7    = 'dummy'
    order_list7  = 'dummy'
    legend_list7 = 'dummy'

try:
    ci_list8
except:
    ci_list8     = 'dummy'
    signif_list8 = 'dummy'
    disp_list8   = 'dummy'
    colors_list8 = 'dummy'
    pch_list8    = 'dummy'
    type_list8   = 'dummy'
    lty_list8    = 'dummy'
    lwd_list8    = 'dummy'
    con_list8    = 'dummy'
    order_list8  = 'dummy'
    legend_list8 = 'dummy'




# Define thresholds, levels, etc. for series plots and performance diagrams
plevs = [250,500,850]
#plevs = [250,500,700,850,925]
#if str.upper(verf_job) != 'HREFV3':
#    plevs.extend([50,100,200,300,1000])

ceil_thresholds = [152,305,914,1520,3040]                    # ceiling thresholds in m
us_ceil_thresholds = [500,1000,3000,5000,10000]              # ceiling thresholds in ft
href_ceil_thresholds = [305,1000,2000,3000]                  # Binbin ceiling thresholds in m

vis_thresholds = [805,1609,4828,8045,16090]                  # vis thresholds in m
us_vis_thresholds = [0.5,1,3,5,10]                           # vis thresholds in mi
href_vis_thresholds = [500,1000,4000,8000,10000]             # Binbin vis thresholds in me

cape_thresholds = [500,1000,1500,2000,3000,4000]             # cape thresholds
href_cape_thresholds = [500,1000,3000]                       # Binbin cape thresholds

radar_thresholds = [20,30,40,50]                             # thresholds for REFC, REFD, RETOP
refd_thresholds = [30,40,50]                                 # thresholds for HREF REFD probs
retop_thresholds = [6096,9144,12192]                         # thresholds for HREF RETOP probs
radar_nbrhd = "43 km"
radar_interp_pnts = 289

surrsvr_thresholds = [0.02,0.05,0.10,0.15,0.30,0.45,0.60]    # thresholds for REFC, REFD, RETOP
surrsvr_rel_thresholds = [1]                                 # dummy threshold for UH_SSPF reliability diagram
surrsvr_nbrhd = "81 km"
surrsvr_interp_pnts = 1

pcp3h_thresholds = [6.35,12.75,25.4]                         # Binbin thresholds for APCP_03 in mm
us_pcp3h_thresholds = [0.25,0.5,1]                           # Binbin thresholds for APCP_03 in in
pcp3h_interp_pnts = 121
pcp3h_nbrhd = "26 km"

upper_air_obs = np.arange(0,13,12)

# dummy vars to hold for now
cycle = 0 
fhr  = 0
plev = plevs[0] 
thresh = ceil_thresholds[0] 
imperial_thresh = ceil_thresholds[0] 
interp_pnts = 'dummy'
nbrhd = 'dummy'
fcst_var = 'dummy'
ensprod_key = 'dummy'
prod = 'dummy'
para = 'dummy'
prod_label = 'dummy'
para_label = 'dummy'


# Define groups of regions to use for list of model names 
conus_regions = ['conus','east','plains','west','apl','gmc','grb','lmv','mdw','nec','nmt','npl','nwc','sec','smt','spl','swc','swd']
alaska_regions = ['alaska','ak','nak','sak']
spc_regions = ['spc outlook areas','spc','spc day 1','spc day 2','spc day 3','spc tstm','spc mrgl','spc slgt','spc enh','spc mod','spc high']

# Define grouups of regions to help specify regions for different fields
upper_air_regions = ['conus','alaska']
cape_regions = ['conus','east','plains','west','alaska']
precip_regions = conus_regions
radar_regions = conus_regions + spc_regions

#################################### Scorecard Section  #####################################################


if doScorecard:

    t1a = time.time()

    # Check for argument to run scorecards
    try:
        scorecard_command = str(sys.argv[4])
        scorecard_day = True
    except IndexError:
        scorecard_day = False

    # Skip other plot types on scorecard day
    if scorecard_day:
        doPerformance = False
        doReliability = False
        doFcstThresh  = False
        doValidHour   = False
        doFcstLead    = False
        doTimeSeries  = False


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

    # Check for "different domain" pairs and remove from list
    if str.upper(verf_job) == 'HREF_MEM':
        n = 0
        npairs = len(name_pairs)
        while n < npairs:
            if name_pairs[n][0][0:2] != name_pairs[n][1][0:2]:
                del name_pairs[n]
                del label_pairs[n]
                npairs = npairs - 1
            else:
                n += 1


    # Loop over model pairs to make scorecards
    for i in range(npairs):
        prod = name_pairs[i][0]
        para = name_pairs[i][1]
        prod_label = label_pairs[i][0]
        para_label = label_pairs[i][1]

        # Define scorecards to run
        plottypes = ['fcstlead']
        if (prod[-2:] == 'AK' and para[-2:] == 'AK') or (prod[0:2] == 'AK' and para[0:2] == 'AK'):
            plottypes2 = ['sfc','upper','cv']
            regions = ['Alaska']
        elif prod == 'CONUSHREF_PMMN':
            plottypes2 = ['refc','retop']
            regions = ['CONUS']
        else:
            plottypes2 = ['sfc','upper','cv','cape','24hpcp','6hpcp','refc','retop']
            plottypes2 = ['sfc','upper','cv','cape','refc']
            regions = ['CONUS']

        # Generate list of scorecard jobs to run
        scorecards = [n for n in itertools.product(plottypes,plottypes2)]


        # Loop over regions and generate scorecards
        for region in regions:
            for scorecard in scorecards:

                # Define neighborhood settings for radar stats
                if scorecard[1][0:2] == 're':
                    nbrhd = radar_nbrhd   
                    interp_pnts = radar_interp_pnts 

                # Update final valid date and masking region
                mv_database, vday2 = update_db_vday2(verf_job,scorecard[1])
                vx_mask = update_vx_mask('scorecard',region)

                # Update XML file and run METviewer job
                template_xml = TEMPLATE_DIR+'/scorecard_'+scorecard[1]+'_'+scorecard[0]+'.xml'  
                updated_xml = SCRIPT_DIR+'/'+str.lower(para_label)+'_'+str.lower(prod_label)+'_'+scorecard[1]+'_'+scorecard[0]+'_scorecard.xml'
                outfile = OUTPUT_DIR+'/'+str.lower(para_label)+'_'+str.lower(prod_label)+'_'+scorecard[1]+'_'+scorecard[0]+'_scorecard.out'

                update_scorecard_xml(scorecard[1],template_xml, updated_xml)
                run_metviewer('scorecard', updated_xml)


    # Set up directory for saving scorecards
    SCORECARD_DIR = os.path.join(PLOT_DIR,'scorecards')

    plot_files = os.listdir(PLOT_DIR)
    for files in plot_files:
        if files.endswith("scorecard.png"):

            # Make sure destination directory exists
            if not os.path.exists(SCORECARD_DIR):
                os.makedirs(SCORECARD_DIR)

            source = PLOT_DIR+'/'+files
            dest = SCORECARD_DIR+'/'+files
            shutil.move(source,dest)

            o = open(SCORECARD_DIR+'/done.'+now.strftime('%Y%m%d'),"w")
            o.write('Finished making scorecards')
            o.close()



    t2a = time.time()
    t3a = round(t2a-t1a, 3)
    print(("%.3f seconds to generate all scorecards") % t3a)



#################################### Performance Diagram Section  #####################################################


if doPerformance:

    t1a = time.time()

    plottypes = ['perf_fcstthresh3']

    # Loop through regions to generate performance diagrams
    regions = ['CONUS','East','Plains','West']

    if str.upper(verf_job) != 'FV3CAM':
        regions.extend(['Alaska','NAK','SAK'])
    if str.upper(verf_job) != 'MESO':
        regions.extend(['SPC'])

    for region in regions:

        print('\n Working on '+region+' performance diagrams \n')

        # Set domain_key so appropriate model name can be used
        # Define list of plots to make for each region 
        if str.lower(region) in conus_regions:
            domain_key = 'conus'

            # Plots for HREFv3 over CONUS/East/West
            if str.upper(verf_job) == 'HREFV3':
                plottypes2 = ['24hpcp_lpmm','24hpcp_avrg','24hpcp_mean','24hpcp_v3prods','ceiling','vis']
                if str.lower(region) in cape_regions:
                    plottypes2.extend(['cape'])
                if str.lower(region) in radar_regions:
                  # plottypes2.extend(['refc','refd','retop','surrsvr'])
                    plottypes2.extend(['refc','refd','retop'])

            # Plots for deterministics over CONUS/East/West
            else:
                plottypes2 = ['24hpcp','ceiling','vis']
                if str.lower(region) in cape_regions:
                    plottypes2.extend(['cape'])
                if str.lower(region) in radar_regions and str.upper(verf_job) != 'MESO':
                    plottypes2.extend(['refc','refd','retop'])

        # Plots for Alaska
        elif str.lower(region) in alaska_regions:
            domain_key = 'alaska' 
            plottypes2 = ['ceiling','vis']
            if str.lower(region) in cape_regions:
                plottypes2.extend(['cape'])

        # Plots for SPC outlook areas
        elif str.lower(region) in spc_regions:
            domain_key = 'conus'
           #plottypes2 = ['refc','refd','retop','surrsvr']
            plottypes2 = ['refc','refd','retop']

        # Generate list of plotting jobs to run
        plots = [n for n in itertools.product(plottypes,plottypes2)]

        # Loop over cycles and generate plots
     #  for cycle in cycles:
        for plot in plots:

                # Update final valid date and masking region
                mv_database, vday2 = update_db_vday2(verf_job,plot[1])
                vx_mask = update_vx_mask('batch',region)

                if plot[1][0:2] == 're':
                    nbrhd = radar_nbrhd    
                    interp_pnts = radar_interp_pnts 
                    ensprod_key = 'pmmn'
                elif plot[1] == 'surrsvr':
                    interp_pnts = surrsvr_interp_pnts
                    ensprod_key = 'prob'


                if str.upper(verf_job) == 'HREFV3':

                    # Plots comparing HREF and HREFX MEAN from Binbin
                    if plot[1] == 'cape' or plot[1] == 'ceiling' or plot[1] == 'vis': 
                        template_xml = TEMPLATE_DIR+'/'+plot[0]+'_'+plot[1]+'_href.xml' 
                        ensprod_key = 'mean'

                        colors_list = 'c(\"'+href['color']+'\",\"'+hrefx['color']+'\")'
                        legend_list = 'c(\"'+href['name']+' '+href[ensprod_key]+'\",\"'+hrefx['name']+' '+hrefx[ensprod_key]+'\")'

                    # Precip plots comparing HREF and HREFX MEAN
                    elif plot[1][0:6] == '24hpcp' and plot[1][-4:] != 'lpmm' and plot[1][-4:] != 'avrg' and plot[1][-7:] != 'v3prods':
                        template_xml = TEMPLATE_DIR+'/'+plot[0]+'_'+plot[1][0:6]+'_href.xml' 
                        ensprod_key = plot[1][-4:]

                        colors_list = 'c(\"'+href['color']+'\",\"'+hrefx['color']+'\")'
                        legend_list = 'c(\"'+href['name']+' '+href[ensprod_key]+'\",\"'+hrefx['name']+' '+hrefx[ensprod_key]+'\")'

                    # Precip plots comparing three HREF products
                    elif plot[1][0:6] == '24hpcp' and (plot[1][-4:] == 'lpmm' or plot[1][-4:] == 'avrg'):
                        template_xml = TEMPLATE_DIR+'/'+plot[0]+'_'+plot[1][0:6]+'_href3.xml' 
                        ensprod_key = plot[1][-4:]

                        # Precip plots comparing PMMN, PMMN, and LPMM
                        if plot[1][-4:] == 'lpmm':
                            colors_list5 = 'c(\"'+href['color']+'\",\"'+nam3['color']+'\",\"'+hrefx['color']+'\",\"'+gfs['color']+'\",\"'+gfs['color']+'\",\"'+gfs['color']+'\")'
                            legend_list5 = 'c(\"'+href['name']+' '+href['pmmn']+'\",\"'+hrefx['name']+' '+hrefx['lpmm']+'\",\"'+hrefx['name']+' '+hrefx['pmmn']+'\",\"Obs\",\"Obs\",\"Obs\")'
                            colors_list6 = 'c(\"'+href['color']+'\",\"'+nam3['color']+'\",\"'+hrefx['color']+'\")'
                            legend_list6 = 'c(\"'+href['name']+' '+href['pmmn']+'\",\"'+hrefx['name']+' '+hrefx['lpmm']+'\",\"'+hrefx['name']+' '+hrefx['pmmn']+'\")'

                        # Precip plots comparing HREF AVRG, HREFX AVRG, and HREFX LAVG
                        elif plot[1][-4:] == 'avrg':
                            colors_list5 = 'c(\"'+href['color']+'\",\"'+hrefx['color']+'\",\"'+nam3['color']+'\",\"'+gfs['color']+'\",\"'+gfs['color']+'\",\"'+gfs['color']+'\")'
                            legend_list5 = 'c(\"'+href['name']+' '+href['avrg']+'\",\"'+hrefx['name']+' '+hrefx['avrg']+'\",\"'+hrefx['name']+' '+hrefx['lavg']+'\",\"Obs\",\"Obs\",\"Obs\")'
                            colors_list6 = 'c(\"'+href['color']+'\",\"'+hrefx['color']+'\",\"'+nam3['color']+'\")'
                            legend_list6 = 'c(\"'+href['name']+' '+href['avrg']+'\",\"'+hrefx['name']+' '+hrefx['avrg']+'\",\"'+hrefx['name']+' '+hrefx['lavg']+'\")'

                    # Precip plots comparing five HREF products
                    elif plot[1][0:6] == '24hpcp' and plot[1][-7:] == 'v3prods':
                        template_xml = TEMPLATE_DIR+'/'+plot[0]+'_'+plot[1][0:6]+'_href5.xml' 
                        ensprod_key = 'v3prods'

                    # Plots comparing HREF and HREFX PMMN for radar and surrogate severe
                    else:   
                        template_xml = TEMPLATE_DIR+'/'+plot[0]+'_'+plot[1]+'.xml' 

                        colors_list = 'c(\"'+hrefx['color']+'\",\"'+href['color']+'\")'
                        legend_list = 'c(\"'+hrefx['name']+' '+hrefx[ensprod_key]+'\",\"'+href['name']+' '+href[ensprod_key]+'\")'


                else:   
                    template_xml = TEMPLATE_DIR+'/'+plot[0]+'_'+plot[1]+'.xml' 


                updated_xml = SCRIPT_DIR+'/'+plot[0]+'_'+plot[1]+'.xml'
                outfile = OUTPUT_DIR+'/'+plot[0]+'_'+plot[1]+'_'+str(cycle).zfill(2)+'z_'+str.lower(region)+'.out'

#               if plot[0][-11:] == 'fcstthresh3':

                # Update XML file and run METviewer job
                update_xml('batch',plot[1],template_xml, updated_xml)
                run_metviewer('performance', updated_xml)

                '''
                # Use METviewer data file to reproduce performance diagram w/ python
                plot_files = os.listdir(PLOT_DIR)

                # Check to see if data file exists
                try:
                    data_fname = [x for x in plot_files if x.endswith('.data')][0]
                except:
                    data_fname = None

                # Only run python function if data file exists
                if data_fname is not None:
                    filename = os.path.join(PLOT_DIR,data_fname[:-5])
                    performance_diag(filename,plot[1])

                    # remove any data file(s)
                    data_files = glob.glob('*.data')
                    for data_file in data_files:
                        os.remove(data_file)
                  # os.remove(filename+'.data')
                '''



    # Move plots to appropriate directories
    organize_plots()

    t2a = time.time()
    t3a = round(t2a-t1a, 3)
    print(("\n %.3f seconds to generate all performance diagrams \n \n") % t3a)



#################################### Reliability Diagram Section  #####################################################


if doReliability:

    t1a = time.time()

    plottypes = ['reliability']

    # Loop through regions to generate reliability diagrams
    regions = ['CONUS','East','Plains','West','SPC']

    for region in regions:

        print('\n Working on '+region+' reliability diagrams \n')

        # Set domain_key so appropriate model name can be used
        # Define list of plots to make for each region 
        if str.lower(region) in conus_regions:
            domain_key = 'conus'

            # Plots for HREFv3 over CONUS/East/West
            if str.upper(verf_job) == 'HREFV3':
                if str.lower(region) == 'conus':
                    plottypes2 = ['24hpcp_lpmm','24hpcp_avrg','24hpcp_mean','refc','refd','retop']
                    plottypes2 = ['refc','refd','retop']
                    plottypes2 = ['3hpcp_prob','6hpcp_prob']
                    plottypes2 = []
                    plottypes2 = ['refc','refd','retop','surrsvr']
                    plottypes2 = ['refc','refd','retop']
                else:
                    plottypes2 = ['3hpcp_prob','6hpcp_prob']
                    plottypes2 = []
                    if str.lower(region) != 'west':
                       #plottypes2.extend(['refc','refd','retop','surrsvr'])
                        plottypes2.extend(['refc','refd','retop'])


        # Plots for SPC outlook areas
        elif str.lower(region) in spc_regions:
            domain_key = 'conus'
          # plottypes2 = ['refc','refd','retop','surrsvr']
            plottypes2 = ['refc','refd','retop']

        # Generate list of plotting jobs to run
        plots = [n for n in itertools.product(plottypes,plottypes2)]


        # Loop over cycles and generate plots
        for plot in plots:


            # Update final valid date and masking region
            mv_database, vday2 = update_db_vday2(verf_job,plot[1])
            vx_mask = update_vx_mask('batch',region)

            # Update XML file and run METviewer job
            template_xml = TEMPLATE_DIR+'/'+plot[0]+'_'+plot[1]+'.xml' 
            updated_xml = SCRIPT_DIR+'/'+plot[0]+'_'+plot[1]+'.xml'

            # Diagrams for radar verification
            if plot[1][0:2] == 're' or plot[1] == 'surrsvr':
                ensprod_key = 'prob'
                colors_list = 'c(\"'+hrefx['color']+'\",\"'+href['color']+'\")'
                legend_list = 'c(\"'+hrefx['name']+' '+hrefx[ensprod_key]+'\",\"'+href['name']+' '+href[ensprod_key]+'\")'

                if plot[1] == 'refc':
                    fcst_var = 'REFC'
                    thresholds = radar_thresholds
                elif plot[1] == 'refd':
                    fcst_var = 'REFD'
                    thresholds = refd_thresholds
                elif plot[1] == 'retop':
                    fcst_var = 'RETOP'
                    thresholds = retop_thresholds
                elif plot[1] == 'surrsvr':
                    fcst_var = 'UH_SSPF'
                    thresholds = surrsvr_rel_thresholds


            # Loop through thresholds and plot
            for thresh in thresholds:

                if plot[1] == 'retop':
                    imperial_thresh = radar_thresholds[retop_thresholds.index(thresh)]

                outfile = OUTPUT_DIR+'/'+plot[0]+'_'+plot[1]+'_'+str(thresh)+'_'+str.lower(region)+'.out'
                update_xml('batch',plot[1],template_xml, updated_xml)
                run_metviewer('reliability', updated_xml)


                '''
                # Use METviewer data file to reproduce reliability diagram w/ python
                plot_files = os.listdir(PLOT_DIR)

                # Check to see if data file exists
                try:
                    data_fname = [x for x in plot_files if x.endswith('.data')][0]
                except:
                    data_fname = None

                # Only run python function if data file exists
                if data_fname is not None:
                    filename = os.path.join(PLOT_DIR,data_fname[:-5])
                    reliability_diag(filename,plot[1])
                    os.remove('*.data')
                  # os.remove(filename+'.data')
                '''
               


    # Move plots to appropriate directories
    organize_plots()

    t2a = time.time()
    t3a = round(t2a-t1a, 3)
    print(("%.3f seconds to generate all reliability diagrams") % t3a)





#################################### Forecast Threshold Section  #####################################################


if doFcstThresh:

    t1a = time.time()

    plottypes = ['fcstthresh']

    # Loop through regions to generate fcst thresh series plots
    regions = ['CONUS','East','Plains','West']

    if str.upper(verf_job) != 'FV3CAM':
        regions.extend(['Alaska','NAK','SAK'])
    if str.upper(verf_job) != 'MESO':
        regions.extend(['SPC'])

    for region in regions:

        print('\n Working on '+region+' forecast threshold plots \n')

        # Set domain_key so appropriate model name can be used
        # Define list of plots to make for each region 
        if str.lower(region) in conus_regions:
            domain_key = 'conus'

            # Plots for HREFv3 over CONUS/East/West
            if str.upper(verf_job) == 'HREFV3':
                plottypes2 = ['24hpcp_lpmm','24hpcp_avrg','24hpcp_mean','ceiling','vis']
                if str.lower(region) == 'conus':
                    plottypes2.extend(['cape'])
                if str.lower(region) != 'west':
                   #plottypes2.extend(['radar_nbrcnt','radar_nbrctc','surrsvr_nbrcnt','surrsvr_pct'])
                    plottypes2.extend(['radar_nbrcnt','radar_nbrctc'])

            # Plots for deterministics over CONUS/East/West
            else:
                plottypes2 = ['24hpcp','ceiling','vis']
                if str.lower(region) in cape_regions:
                    plottypes2.extend(['cape'])
                if str.lower(region) in radar_regions and str.upper(verf_job) != 'MESO':
                  # plottypes2.extend(['radar_nbrcnt','radar_nbrctc','surrsvr_nbrcnt','surrsvr_pct'])
                    plottypes2.extend(['radar_nbrcnt','radar_nbrctc'])

        # Plots for Alaska
        elif str.lower(region) in alaska_regions:
            domain_key = 'alaska'
            plottypes2 = ['ceiling','vis']
            if str.lower(region) in cape_regions:
                plottypes2.extend(['cape'])

        # Plots for SPC outlook areas
        elif str.lower(region) in spc_regions:
            domain_key = 'conus'
          # plottypes2 = ['radar_nbrcnt','radar_nbrctc','surrsvr_nbrcnt','surrsvr_pct']
            plottypes2 = ['radar_nbrcnt','radar_nbrctc']
            if str.upper(verf_job) == 'HREFV3':
                plottypes2.extend(['radar_pct'])


        # Generate list of plotting jobs to run
        plots = [n for n in itertools.product(plottypes,plottypes2)]


        # Loop and generate plots
        for plot in plots:

            # Update final valid date and masking region
            mv_database, vday2 = update_db_vday2(verf_job,plot[1])
            vx_mask = update_vx_mask('batch',region)


            if plot[1] == 'radar_nbrcnt' or plot[1] == 'radar_nbrctc':
                nbrhd = radar_nbrhd    
                interp_pnts = radar_interp_pnts 
                ensprod_key = 'pmmn'
            elif plot[1][0:7] == 'surrsvr':
                nbrhd = surrsvr_nbrhd
                interp_pnts = surrsvr_interp_pnts
                ensprod_key = 'nbmax'


            # Define template XML filename
            if str.upper(verf_job) == 'HREFV3':

                # Plots comparing HREF and HREFX MEAN from Binbin
                if plot[1] == 'cape' or plot[1] == 'ceiling' or plot[1] == 'vis':
                    template_xml = TEMPLATE_DIR+'/'+plot[0]+'_'+plot[1]+'_href.xml'
                    ensprod_key = 'mean'

                    colors_list = 'c(\"'+href['color']+'\",\"'+hrefx['color']+'\")'
                    legend_list = 'c(\"'+href['name']+' '+href[ensprod_key]+'\",\"'+hrefx['name']+' '+hrefx[ensprod_key]+'\")'

                # Precip plots comparing HREF and HREFX MEAN
                elif plot[1][0:6] == '24hpcp' and plot[1][-4:] != 'lpmm' and plot[1][-4:] != 'avrg':
                    template_xml = TEMPLATE_DIR+'/'+plot[0]+'_'+plot[1][0:6]+'_href.xml' 
                    ensprod_key = plot[1][-4:]

                    colors_list = 'c(\"'+href['color']+'\",\"'+hrefx['color']+'\")'
                    legend_list = 'c(\"'+href['name']+' '+href[ensprod_key]+'\",\"'+hrefx['name']+' '+hrefx[ensprod_key]+'\")'

                # Precip plots comparing three HREF products
                elif plot[1][0:6] == '24hpcp' and (plot[1][-4:] == 'lpmm' or plot[1][-4:] == 'avrg'):
                    template_xml = TEMPLATE_DIR+'/'+plot[0]+'_'+plot[1][0:6]+'_href3.xml' 
                    ensprod_key = plot[1][-4:]

                    # Precip plots comparing PMMN, PMMN, and LPMM
                    if plot[1][-4:] == 'lpmm':
                        colors_list5 = 'c(\"'+href['color']+'\",\"'+nam3['color']+'\",\"'+hrefx['color']+'\",\"'+gfs['color']+'\",\"'+gfs['color']+'\",\"'+gfs['color']+'\")'
                        legend_list5 = 'c(\"'+href['name']+' '+href['pmmn']+'\",\"'+hrefx['name']+' '+hrefx['lpmm']+'\",\"'+hrefx['name']+' '+hrefx['pmmn']+'\",\"Obs\",\"Obs\",\"Obs\")'
                        colors_list6 = 'c(\"'+href['color']+'\",\"'+nam3['color']+'\",\"'+hrefx['color']+'\")'
                        legend_list6 = 'c(\"'+href['name']+' '+href['pmmn']+'\",\"'+hrefx['name']+' '+hrefx['lpmm']+'\",\"'+hrefx['name']+' '+hrefx['pmmn']+'\")'

                    # Precip plots comparing HREF AVRG, HREFX AVRG, and HREFX LAVG
                    elif plot[1][-4:] == 'avrg':
                        colors_list5 = 'c(\"'+href['color']+'\",\"'+hrefx['color']+'\",\"'+nam3['color']+'\",\"'+gfs['color']+'\",\"'+gfs['color']+'\",\"'+gfs['color']+'\")'
                        legend_list5 = 'c(\"'+href['name']+' '+href['avrg']+'\",\"'+hrefx['name']+' '+hrefx['avrg']+'\",\"'+hrefx['name']+' '+hrefx['lavg']+'\",\"Obs\",\"Obs\",\"Obs\")'
                        colors_list6 = 'c(\"'+href['color']+'\",\"'+hrefx['color']+'\",\"'+nam3['color']+'\")'
                        legend_list6 = 'c(\"'+href['name']+' '+href['avrg']+'\",\"'+hrefx['name']+' '+hrefx['avrg']+'\",\"'+hrefx['name']+' '+hrefx['lavg']+'\")'

                # Plots comparing HREF/X PMMN and PROB for radar
                elif plot[1][0:5] == 'radar':
                    if plot[1][6:] == 'pct':
                        ensprod_key = 'nbmax'
                    else:
                        ensprod_key = 'pmmn'

                    template_xml = TEMPLATE_DIR+'/'+plot[0]+'_'+plot[1]+'.xml' 

                    colors_list = 'c(\"'+hrefx['color']+'\",\"'+href['color']+'\")'
                    legend_list = 'c(\"'+hrefx['name']+' '+hrefx[ensprod_key]+'\",\"'+href['name']+' '+href[ensprod_key]+'\")'

                # Plots comparing HREF/X PMMN and PROB for surrogate severe
                elif plot[1][0:7] == 'surrsvr':
                    ensprod_key = 'nbmax'

                    template_xml = TEMPLATE_DIR+'/'+plot[0]+'_'+plot[1]+'.xml'

                    colors_list = 'c(\"'+hrefx['color']+'\",\"'+href['color']+'\")'
                    legend_list = 'c(\"'+hrefx['name']+' '+hrefx[ensprod_key]+'\",\"'+href['name']+' '+href[ensprod_key]+'\")'

                else:
                    print("plot_type "+plot[1]+" is not set up")
                    pass


            else:   
                template_xml = TEMPLATE_DIR+'/'+plot[0]+'_'+plot[1]+'.xml' 


            # Update XML file and run METviewer job
            updated_xml = SCRIPT_DIR+'/series_'+plot[0]+'_'+plot[1]+'.xml'
            outfile = OUTPUT_DIR+'/series_'+plot[0]+'_'+plot[1]+'_'+str.lower(region)+'.out'

            update_xml('batch',plot[1],template_xml, updated_xml)
            run_metviewer('batch', updated_xml)


    # Move plots to appropriate directories
    organize_plots()

    t2a = time.time()
    t3a = round(t2a-t1a, 3)
    print(("%.3f seconds to generate all forecast threshold plots") % t3a)





#################################### Valid Hour Section  #####################################################


if doValidHour:

    t1a = time.time()

    plottypes = ['validhour']

    # Loop through regions to generate valid hour series plots
    regions = ['CONUS','East','Plains','West']

    if str.upper(verf_job) != 'FV3CAM':
        regions.extend(['Alaska','NAK','SAK'])
    if str.upper(verf_job) != 'MESO':
      # regions.extend(['SPC'])
        pass

    for region in regions:

        print('\n Working on '+region+' valid hour plots \n')

        # Set domain_key so appropriate model name can be used
        # Define list of plots to make for each region 
        if str.lower(region) in conus_regions:
            domain_key = 'conus'

            # Plots for HREFv3 over CONUS/East/West
            if str.upper(verf_job) == 'HREFV3':
                plottypes2 = ['3hpcp_lpmm','3hpcp_avrg','3hpcp_mean','3hpcp_nbrcnt_lpmm','3hpcp_nbrcnt_avrg','3hpcp_nbrcnt_mean',
                              'sfc_z0','sfc_z2','sfc_sl1l2_z10','ceiling','vis']
                if str.lower(region) == 'conus':
                    plottypes2.extend(['upper','upperwind'])
                if str.lower(region) != 'west':
                    plottypes2.extend(['radar_nbrcnt','radar_nbrctc','radar_pct'])

            # Plots for deterministics over CONUS/East/West
            else:
              # plottypes2 = ['sfc_z0','sfc_z2','sfc_z10','3hpcp_sl1l2','ceiling','vis']
                plottypes2 = ['sfc_z0','sfc_z2','sfc_z10']
                if str.lower(region) in upper_air_regions:
                    plottypes2.extend(['upper','upperwind'])
                if str.lower(region) in cape_regions:
                  # plottypes2.extend(['cape'])
                    pass
                if str.lower(region) in radar_regions and str.upper(verf_job) != 'MESO':
                  # plottypes2.extend(['radar_nbrcnt','radar_nbrctc'])
                    pass

        # Plots for Alaska
        elif str.lower(region) in alaska_regions:
            domain_key = 'alaska' 
            if str.upper(verf_job) == 'HREFV3':
                plottypes2 = ['sfc_z0','sfc_z2','sfc_sl1l2_z10','upper','upperwind','ceiling','vis']
            else:
              # plottypes2 = ['sfc_z0','sfc_z2','sfc_z10','ceiling','vis']
                plottypes2 = ['sfc_z0','sfc_z2','sfc_z10']
                if str.lower(region) in upper_air_regions:
                    plottypes2.extend(['upper','upperwind'])

        # Plots for SPC outlook areas
        elif str.lower(region) in spc_regions:
            domain_key = 'conus'
            plottypes2 = ['radar_nbrcnt','radar_nbrctc']
            if str.upper(verf_job) == 'HREFV3':
                plottypes2.extend(['radar_pct'])



        # Generate list of plotting jobs to run
        plots = [n for n in itertools.product(plottypes,plottypes2)]


        # Loop and generate plots
        for plot in plots:

            # Update final valid date and masking region
            mv_database, vday2 = update_db_vday2(verf_job,plot[1])
            vx_mask = update_vx_mask('batch',region)


            # Define template XML filename
            if str.upper(verf_job) == 'HREFV3':

                # Plots comparing HREF and HREFX MEAN from Binbin
                if plot[1] == 'cape' or plot[1] == 'ceiling' or plot[1] == 'vis' or plot[1] == 'sfc_z0':
                    template_xml = TEMPLATE_DIR+'/'+plot[0]+'_'+plot[1]+'_href.xml'
                    ensprod_key = 'mean'

                    colors_list = 'c(\"'+href['color']+'\",\"'+hrefx['color']+'\")'
                    legend_list = 'c(\"'+href['name']+' '+href[ensprod_key]+'\",\"'+hrefx['name']+' '+hrefx[ensprod_key]+'\")'

                # Plots comparing HREF and HREFX MEAN from Binbin
                elif plot[1] == 'sfc_z2' or plot[1] == 'sfc_sl1l2_z10':
                    template_xml = TEMPLATE_DIR+'/'+plot[0]+'_'+plot[1]+'.xml'
                    ensprod_key = 'mean'

                    colors_list = 'c(\"'+href['color']+'\",\"'+hrefx['color']+'\")'
                    legend_list = 'c(\"'+href['name']+' '+href[ensprod_key]+'\",\"'+hrefx['name']+' '+hrefx[ensprod_key]+'\")'

                # Precip plots comparing HREF and HREFX MEAN
                elif plot[1][0:5] == '3hpcp' and plot[1][-4:] != 'lpmm' and plot[1][-4:] != 'avrg':
                    template_xml = TEMPLATE_DIR+'/'+plot[0]+'_'+plot[1][0:-5]+'_href.xml' 
                    ensprod_key = plot[1][-4:]

                    colors_list = 'c(\"'+href['color']+'\",\"'+hrefx['color']+'\")'
                    legend_list = 'c(\"'+href['name']+' '+href[ensprod_key]+'\",\"'+hrefx['name']+' '+hrefx[ensprod_key]+'\")'

                # Precip plots comparing three HREF products
                elif plot[1][0:5] == '3hpcp' and (plot[1][-4:] == 'lpmm' or plot[1][-4:] == 'avrg'):
                    template_xml = TEMPLATE_DIR+'/'+plot[0]+'_'+plot[1][0:-5]+'_href3.xml' 
                    ensprod_key = plot[1][-4:]

                    # Precip plots comparing PMMN, PMMN, and LPMM
                    if plot[1][-4:] == 'lpmm':
                        colors_list5 = 'c(\"'+href['color']+'\",\"'+nam3['color']+'\",\"'+hrefx['color']+'\",\"'+gfs['color']+'\",\"'+gfs['color']+'\",\"'+gfs['color']+'\")'
                        legend_list5 = 'c(\"'+href['name']+' '+href['pmmn']+'\",\"'+hrefx['name']+' '+hrefx['lpmm']+'\",\"'+hrefx['name']+' '+hrefx['pmmn']+'\",\"Obs\",\"Obs\",\"Obs\")'
                        colors_list6 = 'c(\"'+href['color']+'\",\"'+nam3['color']+'\",\"'+hrefx['color']+'\")'
                        legend_list6 = 'c(\"'+href['name']+' '+href['pmmn']+'\",\"'+hrefx['name']+' '+hrefx['lpmm']+'\",\"'+hrefx['name']+' '+hrefx['pmmn']+'\")'

                    # Precip plots comparing HREF AVRG, HREFX AVRG, and HREFX LAVG
                    elif plot[1][-4:] == 'avrg':
                        colors_list5 = 'c(\"'+href['color']+'\",\"'+hrefx['color']+'\",\"'+nam3['color']+'\",\"'+gfs['color']+'\",\"'+gfs['color']+'\",\"'+gfs['color']+'\")'
                        legend_list5 = 'c(\"'+href['name']+' '+href['avrg']+'\",\"'+hrefx['name']+' '+hrefx['avrg']+'\",\"'+hrefx['name']+' '+hrefx['lavg']+'\",\"Obs\",\"Obs\",\"Obs\")'
                        colors_list6 = 'c(\"'+href['color']+'\",\"'+hrefx['color']+'\",\"'+nam3['color']+'\")'
                        legend_list6 = 'c(\"'+href['name']+' '+href['avrg']+'\",\"'+hrefx['name']+' '+hrefx['avrg']+'\",\"'+hrefx['name']+' '+hrefx['lavg']+'\")'

                # Plots comparing HREF/X PMMN and PROB for radar
                # Plots comparing HREF/X MEAN for upper and upperwind
                elif plot[1][0:5] == 'radar' or plot[1][0:5] == 'upper':
                    if plot[1][0:5] == 'upper':
                        ensprod_key = 'mean'
                    elif plot[1][6:] == 'pct':
                        ensprod_key = 'nbmax'
                    else:
                        ensprod_key = 'pmmn'

                    template_xml = TEMPLATE_DIR+'/'+plot[0]+'_'+plot[1]+'.xml' 

                    colors_list = 'c(\"'+hrefx['color']+'\",\"'+href['color']+'\")'
                    legend_list = 'c(\"'+hrefx['name']+' '+hrefx[ensprod_key]+'\",\"'+href['name']+' '+href[ensprod_key]+'\")'

                else:
                    print("plot_type "+plot[1]+" is not set up")
                    pass

            else:
                template_xml = TEMPLATE_DIR+'/'+plot[0]+'_'+plot[1]+'.xml'


            updated_xml = SCRIPT_DIR+'/series_'+plot[0]+'_'+plot[1]+'.xml'


            # Loop through ceiling thresholds
            if plot[1] == 'ceiling': 
                if str.upper(verf_job) == 'HREFV3':
                    thresholds = href_ceil_thresholds
                else:
                    thresholds = ceil_thresholds

                for j in range(len(thresholds)):
                    thresh = thresholds[j]
                    if str.upper(verf_job) != 'HREFV3':
                        imperial_thresh = us_ceil_thresholds[j]

                    outfile = OUTPUT_DIR+'/series_'+plot[0]+'_'+plot[1]+'_'+str(thresh)+'_'+str.lower(region)+'.out'
                    update_xml('batch',plot[1],template_xml, updated_xml)
                    run_metviewer('batch', updated_xml)

            # Loop through visibility thresholds
            elif plot[1] == 'vis':
                if str.upper(verf_job) == 'HREFV3':
                    thresholds = href_vis_thresholds
                else:
                    thresholds = vis_thresholds

                for j in range(len(thresholds)):
                    thresh = thresholds[j]
                    if str.upper(verf_job) != 'HREFV3':
                        imperial_thresh = us_vis_thresholds[j]

                    outfile = OUTPUT_DIR+'/series_'+plot[0]+'_'+plot[1]+'_'+str(thresh)+'_'+str.lower(region)+'.out'
                    update_xml('batch',plot[1],template_xml, updated_xml)
                    run_metviewer('batch', updated_xml)

            # Loop through CAPE thresholds
            elif plot[1] == 'cape':
                if str.upper(verf_job) == 'HREFV3':
                    thresholds = href_cape_thresholds
                else:
                    thresholds = cape_thresholds

                for thresh in thresholds:

                    outfile = OUTPUT_DIR+'/series_'+plot[0]+'_'+plot[1]+'_'+str(thresh)+'_'+str.lower(region)+'.out'
                    update_xml('batch',plot[1],template_xml, updated_xml)
                    run_metviewer('batch', updated_xml)

        # REFL diurnal plots
    #   elif plot[1] == 'refl_diurnal':
    #       outfile = OUTPUT_DIR+'/series_'+plot[0]+'_'+plot[1]+'_'+str.lower(region)+'.out'
    #       update_xml('batch',template_xml, updated_xml)
    #       run_metviewer('batch', updated_xml)

            # Loop through radar thresholds
            elif plot[1] == 'radar_nbrcnt' or plot[1] == 'radar_nbrctc':
                nbrhd = radar_nbrhd    
                interp_pnts = radar_interp_pnts 

                for thresh in radar_thresholds:

                    outfile = OUTPUT_DIR+'/series_'+plot[0]+'_'+plot[1]+'_'+str(thresh)+'_'+str.lower(region)+'.out'
                    update_xml('batch',plot[1],template_xml, updated_xml)
                    run_metviewer('batch', updated_xml)

            # Loop through radar thresholds for HREFPROB
            elif plot[1] == 'radar_pct':

                if len(retop_thresholds) == 3:
                    retop_thresholds.extend('dummy')

                for thresh in radar_thresholds:
                    imperial_thresh = retop_thresholds[radar_thresholds.index(thresh)]

                    outfile = OUTPUT_DIR+'/series_'+plot[0]+'_'+plot[1]+'_'+str(thresh)+'_'+str.lower(region)+'.out'
                    update_xml('batch',plot[1],template_xml, updated_xml)
                    run_metviewer('batch', updated_xml)


            # Upper air plots
            elif plot[1][0:5] == 'upper':

                for cycle in upper_air_obs:

                    outfile = OUTPUT_DIR+'/series_'+plot[0]+'_'+plot[1]+'_'+str(cycle).zfill(2)+'z_'+str.lower(region)+'.out'
                    update_xml('batch',plot[1],template_xml, updated_xml)
                    run_metviewer('batch', updated_xml)

            # Sfc plots
            elif plot[1][0:3] == 'sfc':
                outfile = OUTPUT_DIR+'/series_'+plot[0]+'_'+plot[1]+'_'+str.lower(region)+'.out'
                update_xml('batch',plot[1],template_xml, updated_xml)
                run_metviewer('batch', updated_xml)

            # 3-h FSS plots
            elif plot[1] == '3hpcp_nbrcnt':
                interp_pnts = pcp3h_interp_pnts 
                nbrhd = pcp3h_nbrhd 

                for j in range(len(pcp3h_thresholds)):
                    thresh = pcp3h_thresholds[j]
                    imperial_thresh = us_pcp3h_thresholds[j]
                    outfile = OUTPUT_DIR+'/series_'+plot[0]+'_'+plot[1]+'_'+str(thresh)+'_'+str.lower(region)+'.out'
                    update_xml('batch',plot[1],template_xml, updated_xml)
                    run_metviewer('batch', updated_xml)

            # Diurnal precip plots
            elif plot[1] == '3hpcp_sl1l2':
                outfile = OUTPUT_DIR+'/series_'+plot[0]+'_'+plot[1]+'_'+str.lower(region)+'.out'
                update_xml('batch',plot[1],template_xml, updated_xml)
                run_metviewer('batch', updated_xml)

            else:
                print("plot_type "+plot[1]+" is not set up")
                pass


    # Move plots to appropriate directories
    organize_plots()

    t2a = time.time()
    t3a = round(t2a-t1a, 3)
    print(("%.3f seconds to generate all valid hour plots") % t3a)





#################################### Forecast Lead Section  #####################################################


if doFcstLead:

    t1a = time.time()

    plottypes = ['fcstlead']

    # Loop through regions to generate fcst lead series plots
    regions = ['CONUS','East','Plains','West']

    if str.upper(verf_job) != 'FV3CAM':
        regions.extend(['Alaska','NAK','SAK'])
    if str.upper(verf_job) != 'MESO':
        regions.extend(['SPC'])

    for region in regions:

        print('\n Working on '+region+' forecast lead plots \n')

        # Set domain_key so appropriate model name can be used
        # Define list of plots to make for each region 
        if str.lower(region) in conus_regions:
            domain_key = 'conus'

            # Plots for HREFv3 over CONUS/East/West
            if str.upper(verf_job) == 'HREFV3':
                plottypes2 = ['3hpcp_lpmm','3hpcp_avrg','3hpcp_mean','3hpcp_nbrcnt_lpmm','3hpcp_nbrcnt_avrg','3hpcp_nbrcnt_mean',
                              'sfc_z0','sfc_z2','sfc_sl1l2_z10','ceiling','vis']
                if str.lower(region) == 'conus':
                    plottypes2.extend(['upper','upperwind','cape'])
                if str.lower(region) != 'west':
                    plottypes2.extend(['radar_nbrcnt','radar_nbrctc','radar_pct'])

            # Plots for deterministics over CONUS/East/West
            else:
              # plottypes2 = ['sfc_z0','sfc_z2','sfc_z10','3hpcp_sl1l2','ceiling','vis']
                plottypes2 = ['sfc_z0','sfc_z2','sfc_z10','3hpcp_sl1l2']
                if str.lower(region) in upper_air_regions:
                    plottypes2.extend(['upper','upperwind'])
                if str.lower(region) in cape_regions:
                  # plottypes2.extend(['cape'])
                    plottypes2.extend(['cape_sl1l2'])
                if str.lower(region) in radar_regions and str.upper(verf_job) != 'MESO':
                  # plottypes2.extend(['radar_nbrcnt','radar_nbrctc'])
                    plottypes2.extend(['radar_nbrcnt'])


        # Plots for Alaska
        elif str.lower(region) in alaska_regions:
            domain_key = 'alaska' 
            if str.upper(verf_job) == 'HREFV3':
                plottypes2 = ['sfc_z0','sfc_z2','sfc_sl1l2_z10','upper','upperwind','ceiling','vis']
            else:
              # plottypes2 = ['sfc_z0','sfc_z2','sfc_z10','ceiling','vis']
                plottypes2 = ['sfc_z0','sfc_z2','sfc_z10']
                if str.lower(region) in upper_air_regions:
                    plottypes2.extend(['upper','upperwind'])


        # Plots for SPC outlook areas
        elif str.lower(region) in spc_regions:
            domain_key = 'conus'
          # plottypes2 = ['radar_nbrcnt','radar_nbrctc']
            plottypes2 = ['radar_nbrcnt']
            if str.upper(verf_job) == 'HREFV3':
                plottypes2.extend(['radar_pct'])



        # Generate list of plotting jobs to run
        plots = [n for n in itertools.product(plottypes,plottypes2)]


        # Appropriately set cycles for HREF/HiResW runs over Alaska 
        # Other verification jobs use cycles defined above within job block
        if str.upper(verf_job) == 'HREFV3' or str.upper(verf_job) == 'HREF_MEM':
            if str.lower(region) in alaska_regions:
                cycles = np.arange(6,19,12)
            else:
                cycles = np.arange(0,13,12)


        # Loop over cycles and generate plots
        for cycle in cycles:
            for plot in plots:

                # Update final valid date and masking region
                mv_database, vday2 = update_db_vday2(verf_job,plot[1])
                vx_mask = update_vx_mask('batch',region)


                # Define template XML filename
                if str.upper(verf_job) == 'HREFV3':

                    # Plots comparing HREF and HREFX MEAN from Binbin
                    if plot[1] == 'cape' or plot[1] == 'ceiling' or plot[1] == 'vis' or plot[1] == 'sfc_z0':
                        template_xml = TEMPLATE_DIR+'/'+plot[0]+'_'+plot[1]+'_href.xml'
                        ensprod_key = 'mean'

                        colors_list = 'c(\"'+href['color']+'\",\"'+hrefx['color']+'\")'
                        legend_list = 'c(\"'+href['name']+' '+href[ensprod_key]+'\",\"'+hrefx['name']+' '+hrefx[ensprod_key]+'\")'

                    # Plots comparing HREF and HREFX MEAN from Binbin
                    elif plot[1] == 'sfc_z2' or plot[1] == 'sfc_sl1l2_z10':
                        template_xml = TEMPLATE_DIR+'/'+plot[0]+'_'+plot[1]+'.xml'
                        ensprod_key = 'mean'

                        colors_list = 'c(\"'+href['color']+'\",\"'+hrefx['color']+'\")'
                        legend_list = 'c(\"'+href['name']+' '+href[ensprod_key]+'\",\"'+hrefx['name']+' '+hrefx[ensprod_key]+'\")'

                    # Precip plots comparing HREF and HREFX MEAN
                    elif plot[1][0:5] == '3hpcp' and plot[1][-4:] != 'lpmm' and plot[1][-4:] != 'avrg':
                        template_xml = TEMPLATE_DIR+'/'+plot[0]+'_'+plot[1][0:-5]+'_href.xml' 
                        ensprod_key = plot[1][-4:]

                        colors_list = 'c(\"'+href['color']+'\",\"'+hrefx['color']+'\")'
                        legend_list = 'c(\"'+href['name']+' '+href[ensprod_key]+'\",\"'+hrefx['name']+' '+hrefx[ensprod_key]+'\")'

                    # Precip plots comparing three HREF products
                    elif plot[1][0:5] == '3hpcp' and (plot[1][-4:] == 'lpmm' or plot[1][-4:] == 'avrg'):
                        template_xml = TEMPLATE_DIR+'/'+plot[0]+'_'+plot[1][0:-5]+'_href3.xml' 
                        ensprod_key = plot[1][-4:]

                        # Precip plots comparing PMMN, PMMN, and LPMM
                        if plot[1][-4:] == 'lpmm':
                            colors_list5 = 'c(\"'+href['color']+'\",\"'+nam3['color']+'\",\"'+hrefx['color']+'\",\"'+gfs['color']+'\",\"'+gfs['color']+'\",\"'+gfs['color']+'\")'
                            legend_list5 = 'c(\"'+href['name']+' '+href['pmmn']+'\",\"'+hrefx['name']+' '+hrefx['lpmm']+'\",\"'+hrefx['name']+' '+hrefx['pmmn']+'\",\"Obs\",\"Obs\",\"Obs\")'
                            colors_list6 = 'c(\"'+href['color']+'\",\"'+nam3['color']+'\",\"'+hrefx['color']+'\")'
                            legend_list6 = 'c(\"'+href['name']+' '+href['pmmn']+'\",\"'+hrefx['name']+' '+hrefx['lpmm']+'\",\"'+hrefx['name']+' '+hrefx['pmmn']+'\")'

                        # Precip plots comparing HREF AVRG, HREFX AVRG, and HREFX LAVG
                        elif plot[1][-4:] == 'avrg':
                            colors_list5 = 'c(\"'+href['color']+'\",\"'+hrefx['color']+'\",\"'+nam3['color']+'\",\"'+gfs['color']+'\",\"'+gfs['color']+'\",\"'+gfs['color']+'\")'
                            legend_list5 = 'c(\"'+href['name']+' '+href['avrg']+'\",\"'+hrefx['name']+' '+hrefx['avrg']+'\",\"'+hrefx['name']+' '+hrefx['lavg']+'\",\"Obs\",\"Obs\",\"Obs\")'
                            colors_list6 = 'c(\"'+href['color']+'\",\"'+hrefx['color']+'\",\"'+nam3['color']+'\")'
                            legend_list6 = 'c(\"'+href['name']+' '+href['avrg']+'\",\"'+hrefx['name']+' '+hrefx['avrg']+'\",\"'+hrefx['name']+' '+hrefx['lavg']+'\")'

                    # Plots comparing HREF/X PMMN and PROB for radar
                    # Plots comparing HREF/X MEAN for upper and upperwind
                    elif plot[1][0:5] == 'radar' or plot[1][0:5] == 'upper':
                        if plot[1][0:5] == 'upper':
                            ensprod_key = 'mean'
                        elif plot[1][6:] == 'pct':
                            ensprod_key = 'nbmax'
                        else:
                            ensprod_key = 'pmmn'

                        template_xml = TEMPLATE_DIR+'/'+plot[0]+'_'+plot[1]+'.xml' 

                        colors_list = 'c(\"'+hrefx['color']+'\",\"'+href['color']+'\")'
                        legend_list = 'c(\"'+hrefx['name']+' '+hrefx[ensprod_key]+'\",\"'+href['name']+' '+href[ensprod_key]+'\")'

                    else:
                        print("plot_type "+plot[1]+" is not set up")
                        pass

                else:
                    template_xml = TEMPLATE_DIR+'/'+plot[0]+'_'+plot[1]+'.xml'


                updated_xml = SCRIPT_DIR+'/series_'+plot[0]+'_'+plot[1]+'.xml'

                # Loop through ceiling thresholds
                if plot[1] == 'ceiling': 
                    if str.upper(verf_job) == 'HREFV3':
                        thresholds = href_ceil_thresholds
                    else:
                        thresholds = ceil_thresholds

                    for j in range(len(thresholds)):
                        thresh = thresholds[j]
                        if str.upper(verf_job) != 'HREFV3':
                            imperial_thresh = us_ceil_thresholds[j]

                        outfile = OUTPUT_DIR+'/series_'+plot[0]+'_'+plot[1]+'_'+str(cycle).zfill(2)+'z_'+str(thresh)+'_'+str.lower(region)+'.out'
                        update_xml('batch',plot[1],template_xml, updated_xml)
                        run_metviewer('batch', updated_xml)

                # Loop through visibility thresholds
                elif plot[1] == 'vis':
                    if str.upper(verf_job) == 'HREFV3':
                        thresholds = href_vis_thresholds
                    else:
                        thresholds = vis_thresholds

                    for j in range(len(thresholds)):
                        thresh = thresholds[j]
                        if str.upper(verf_job) != 'HREFV3':
                            imperial_thresh = us_vis_thresholds[j]

                        outfile = OUTPUT_DIR+'/series_'+plot[0]+'_'+plot[1]+'_'+str(cycle).zfill(2)+'z_'+str(thresh)+'_'+str.lower(region)+'.out'
                        update_xml('batch',plot[1],template_xml, updated_xml)
                        run_metviewer('batch', updated_xml)

                # Loop through CAPE thresholds
                elif plot[1] == 'cape':
                    if str.upper(verf_job) == 'HREFV3':
                        thresholds = href_cape_thresholds
                    else:
                        thresholds = cape_thresholds

                    for thresh in thresholds:

                        outfile = OUTPUT_DIR+'/series_'+plot[0]+'_'+plot[1]+'_'+str(cycle).zfill(2)+'z_'+str(thresh)+'_'+str.lower(region)+'.out'
                        update_xml('batch',plot[1],template_xml, updated_xml)
                        run_metviewer('batch', updated_xml)

                # Loop through radar thresholds
                elif plot[1] == 'radar_nbrctc' or plot[1] == 'radar_nbrcnt':
                    nbrhd = radar_nbrhd    
                    interp_pnts = radar_interp_pnts 

                    for thresh in radar_thresholds:

                        outfile = OUTPUT_DIR+'/series_'+plot[0]+'_'+plot[1]+'_'+str(cycle).zfill(2)+'z_'+str(thresh)+'_'+str.lower(region)+'.out'
                        update_xml('batch',plot[1],template_xml, updated_xml)
                        run_metviewer('batch', updated_xml)

                # Loop through radar thresholds for HREFPROB
                elif plot[1] == 'radar_pct':

                    if len(retop_thresholds) == 3:
                        retop_thresholds.extend('dummy')

                    for thresh in radar_thresholds:
                        imperial_thresh = retop_thresholds[radar_thresholds.index(thresh)]

                        outfile = OUTPUT_DIR+'/series_'+plot[0]+'_'+plot[1]+'_'+str(cycle).zfill(2)+'z_'+str(thresh)+'_'+str.lower(region)+'.out'
                        update_xml('batch',plot[1],template_xml, updated_xml)
                        run_metviewer('batch', updated_xml)


                # Loop through pressure levels
                elif plot[1][0:5] == 'upper':

                    for plev in plevs:
                        outfile = OUTPUT_DIR+'/series_'+plot[0]+'_'+plot[1]+'_'+str(cycle).zfill(2)+'z_'+str(plev)+'mb_'+str.lower(region)+'.out'
                        update_xml('batch',plot[1],template_xml, updated_xml)
                        run_metviewer('batch', updated_xml)

                # Sfc plots
                elif plot[1][0:3] == 'sfc':

                    outfile = OUTPUT_DIR+'/series_'+plot[0]+'_'+plot[1]+'_'+str(cycle).zfill(2)+'z_'+str.lower(region)+'.out'
                    update_xml('batch',plot[1],template_xml, updated_xml)
                    run_metviewer('batch', updated_xml)

                # 3-h FSS plots
                elif plot[1] == '3hpcp_nbrcnt':
                    interp_pnts = pcp3h_interp_pnts 
                    nbrhd = pcp3h_nbrhd 

                    for j in range(len(pcp3h_thresholds)):
                        thresh = pcp3h_thresholds[j]
                        imperial_thresh = us_pcp3h_thresholds[j]
                        outfile = OUTPUT_DIR+'/series_'+plot[0]+'_'+plot[1]+'_'+str(cycle).zfill(2)+'z_'+str(thresh)+'_'+str.lower(region)+'.out'
                        update_xml('batch',plot[1],template_xml, updated_xml)
                        run_metviewer('batch', updated_xml)

                # Diurnal FBAR/OBAR plots
                elif plot[1] == '3hpcp_sl1l2' or plot[1] == 'cape_sl1l2':

                    outfile = OUTPUT_DIR+'/series_'+plot[0]+'_'+plot[1]+'_'+str(cycle).zfill(2)+'z_'+str.lower(region)+'.out'
                    update_xml('batch',plot[1],template_xml, updated_xml)
                    run_metviewer('batch', updated_xml)

                else:
                    print("plot_type "+plot[1]+" is not set up")


    # Move plots to appropriate directories
    organize_plots()

    t2a = time.time()
    t3a = round(t2a-t1a, 3)
    print(("%.3f seconds to generate all forecast lead plots") % t3a)




#################################### Time Series Section  #####################################################


if doTimeSeries:

    t1a = time.time()

    plottypes = ['timeseries']

    # Make these time series just over the past 32 days
    # Unless we're doing an individual month already
    # Use original vday1 if already doing a monthly period
    if verf_period[0:3].capitalize() not in months:
        vday1 = now + datetime.timedelta(days=-32)    # for doing a past 32 days


    # Loop through regions to generate initialization date series plots
    regions = ['CONUS']

    for region in regions:

        print('\n Working on '+region+' time series plots \n')

        # Set domain_key so appropriate model name can be used
        # Define list of plots to make for each region 
        if str.lower(region) in conus_regions:
            domain_key = 'conus'
            plottypes2 = ['sfc_z2','sfc_z10','upper','upperwind']

        # Plots for Alaska
        elif str.lower(region) in alaska_regions:
            domain_key = 'alaska'
            plottypes2 = ['sfc_z2','sfc_z10','upper','upperwind']


        # Generate list of plotting jobs to run
        plots = [n for n in itertools.product(plottypes,plottypes2)]


        # Loop and generate plots
        for plot in plots:

            # Update final valid date and masking region
            mv_database, vday2 = update_db_vday2(verf_job,plot[1])
            vx_mask = update_vx_mask('batch',region)

            template_xml = TEMPLATE_DIR+'/'+plot[0]+'_'+plot[1]+'.xml' 
            updated_xml = SCRIPT_DIR+'/series_'+plot[0]+'_'+plot[1]+'.xml'


            # Sfc plots
            if plot[1][0:3] == 'sfc':
                for fhr in fhrs:
                    outfile = OUTPUT_DIR+'/series_'+plot[0]+'_'+plot[1]+'_f'+str(fhr).zfill(2)+'_'+str.lower(region)+'.out'
                    update_xml('batch',plot[1],template_xml, updated_xml)
                    run_metviewer('batch', updated_xml)

            # Upper TMP/HGT plots
            elif plot[1] == 'upper':
                for fhr in fhrs:
                    for plev in np.arange(500,851,350):
                        outfile = OUTPUT_DIR+'/series_'+plot[0]+'_'+plot[1]+'_f'+str(fhr).zfill(2)+'_'+str.lower(region)+'.out'
                        update_xml('batch',plot[1],template_xml, updated_xml)
                        run_metviewer('batch', updated_xml)

            # Upper wind plots
            elif plot[1] == 'upperwind':
                for fhr in fhrs:
                    for plev in np.arange(250,500,250):
                        outfile = OUTPUT_DIR+'/series_'+plot[0]+'_'+plot[1]+'_f'+str(fhr).zfill(2)+'_'+str.lower(region)+'.out'
                        update_xml('batch',plot[1],template_xml, updated_xml)
                        run_metviewer('batch', updated_xml)

            else:
                print("plot_type "+plot[1]+" is not set up")

    # Move plots to appropriate directories
    organize_plots()

    t2a = time.time()
    t3a = round(t2a-t1a, 3)
    print(("%.3f seconds to generate all time series plots") % t3a)










