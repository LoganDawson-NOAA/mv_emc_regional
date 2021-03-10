#!/bin/bash -l
# Author: L.C. Dawson
#
###################################################

set +x

source ~/.bashrc


######  REQUIRED ARGUMENTS ######

## RZDM_USER: your emcrzdm username
##
## verf_job: defines set of plots to make
##     options: FV3CAM, CAM, MESO, HREFV3, HREF_MEM
##
## verf_period: define period over which stats will be computed
##     past30days - previous 30 days
##     exp_period - experiment period defined in generate_AWS_plots.py (only for FV3CAM)
##     mmmYYYY - a specific month (e.g., jan2021, jul2020, etc.)
##
## verf_exp: defines FV3CAM comparison experiment
##     Only applicable and REQUIRED when verf_job=FV3CAM  


echo "--------------------------"
echo "`date`"
echo "--------------------------"

now=`date`
dayofweek=`echo $now | cut -c 1-3`

set -x

#verf_job=$1
#verf_period=$2

cd /gpfs/dell2/emc/verification/save/Logan.Dawson/CAM_verif/AWS

RZDM_USER=ldawson

verf_job=CAM
verf_period=past30days

echo "Running now. Date/Time is: `date`"
python generate_AWS_plots.py ${verf_job} ${verf_period}
make_verif_html.sh ${RZDM_USER} ${verf_job} ${verf_period}
echo "Done now. Date/Time is: `date`"



set +x 

echo "--------------------------"
echo "`date`"
echo "--------------------------"

exit



