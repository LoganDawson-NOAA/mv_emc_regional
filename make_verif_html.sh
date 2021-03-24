#!/bin/bash
# update verification web page
set -x
now=`date -u +%Y%m%d%H%M`
yyyy=${now:0:4}
dd=${now:6:2}
hhmm=${now:8:4}
today=${now:0:8}
month=`date -u +%B`


# Set your RZDM username
RZDM_USER=$1

# Verification job
verf_job=$2

# Verification period: past30days or month (as mmmYYYY)
verf_period=$3

# Verification experiment: para/lam/da_exp for FV3CAM
verf_exp=$4



# Specify beginning of RZDM path where images will be transferred
if [ $verf_job == 'FV3CAM' ]; then
   RZDM_HEAD=/home/people/emc/www/htdocs/users/verification/regional/cam/para/${verf_exp}
elif [ $verf_job == 'HREFV3' ]; then
   RZDM_HEAD=/home/people/emc/www/htdocs/users/meg/hrefv3/verif/href
elif [ $verf_job == 'HREF_MEM' ]; then
   RZDM_HEAD=/home/people/emc/www/htdocs/users/meg/hrefv3/verif/hiresw_mem
elif [ $verf_job == 'MESO' ]; then
   RZDM_HEAD=/home/people/emc/www/htdocs/users/verification/regional/mesoscale/ops
elif [ $verf_job == 'CAM' ]; then
   RZDM_HEAD=/home/people/emc/www/htdocs/users/verification/regional/cam/ops
else
   echo "RZDM_HEAD is undefined. Use appropriate 'verf_job' string. Exiting."
   exit
fi

# Specify WCOSS directory for plots to transfer
# Specify WCOSS directory where phps will be saved and updated  
if [ $verf_job == 'FV3CAM' ]; then
   PLOT_DIR=/gpfs/dell2/ptmp/${USER}/CAM_verif/${verf_job}/${verf_exp}/${verf_period}/plots
   HTML_DIR=/gpfs/dell2/ptmp/${USER}/CAM_verif/${verf_job}/${verf_exp}/${verf_period}/html
else
   PLOT_DIR=/gpfs/dell2/ptmp/${USER}/CAM_verif/${verf_job}/${verf_period}/plots
   HTML_DIR=/gpfs/dell2/ptmp/${USER}/CAM_verif/${verf_job}/${verf_period}/html
fi

# Create/clear HTML directory
mkdir -p $HTML_DIR
rm $HTML_DIR/*
cd $HTML_DIR


# List of sub-directories where plots have been saved
directories="scorecards sfc_upper ceil_vis cape precip radar surrogate_svr"

# Copy images to appropriate directories on RZDM
for directory in $directories; do

   RZDM_DIR=$RZDM_HEAD/$directory
   if ! [ -s $PLOT_DIR/$directory/done.$today ]; then
      echo $PLOT_DIR/$directory/done.$today not found.  $directory page not updated.
   else
      ssh ${RZDM_USER}@emcrzdm "mkdir -m 775 -p $RZDM_DIR/${verf_period}"
      scp $PLOT_DIR/$directory/*.png ${RZDM_USER}@emcrzdm.ncep.noaa.gov:$RZDM_DIR/${verf_period}
      scp ${RZDM_USER}@emcrzdm:$RZDM_DIR/*.php $HTML_DIR
   fi

done


# Change permissions on image files to make visible online
# This line may error out. Need to determine if it's necessary
#ssh ${RZDM_USER}@emcrzdm.ncep.noaa.gov "chmod 775 ${RZDM_HEAD}/*/${verf_period}/*.png"


# Update date line on webpages
# Only webpages with updated plots were previously copied from RZDM
webpages=$HTML_DIR/*.php
for webpage in $webpages; do

   dateline=$(grep -n "Plots updated at" $webpage | cut -f1 -d:)
   sed -e ''${dateline}'s/^Plots updated at.*/Plots updated at '${hhmm}' UTC '${dd}' '${month}' '${yyyy}'/' $webpage > tmpfile ; mv tmpfile $webpage
 
done



directories="scorecards cape precip radar sfc_upper sfc_upper ceil_vis ceil_vis ceil_vis"
php_strings=(scorecard _cape. _precip. _radar. _sfc. _upper. _cv. _ceiling. _vis.)

# Copy webpages back to RZDM
i=0
for directory in $directories; do
   RZDM_DIR=$RZDM_HEAD/$directory/
   scp $HTML_DIR/*${php_strings[$i]}*php ${RZDM_USER}@emcrzdm.ncep.noaa.gov:$RZDM_DIR
   let "i++"
done


exit
