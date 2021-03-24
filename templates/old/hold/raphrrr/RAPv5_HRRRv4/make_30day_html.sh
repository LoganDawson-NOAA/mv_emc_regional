#!/bin/bash
# make RAP/HRRR verification web page
set -x
now=`date -u +%Y%m%d%H%M`
yyyy=${now:0:4}
dd=${now:6:2}
hhmm=${now:8:4}
today=${now:0:8}
month=`date -u +%B`

PLOT_DIR=/ptmpp2/Logan.Dawson/CAM_verif/RAPv5_HRRRv4/plots
RZDM_DIR=/home/people/emc/www/htdocs/users/meg/rapv5_hrrrv4/verif/eval_period
HTML_DIR=/meso/save/Logan.Dawson/CAM_verif/RAPv5_HRRRv4/html

mkdir -p $HTML_DIR
rm $HTML_DIR/*
cd $HTML_DIR

# Copy forecast lead series plots to RZDM
RZDM_DIR=/home/people/emc/www/htdocs/users/meg/rapv5_hrrrv4/verif/eval_period/series_fcstlead/
if ! [ -s $PLOT_DIR/series_fcstlead/done.$today ]; then
  echo $PLOT_DIR/series_fcstlead/done.$today not found.  Exit w/o updating scores page
  Mail -s "RAP/HRRR forecast lead series plots: web page not made" Logan.Dawson@noaa.gov <<EOF
    done.$today not found
EOF
else
  scp $PLOT_DIR/series_fcstlead/*.png ldawson@emcrzdm:$RZDM_DIR
  scp ldawson@emcrzdm:$RZDM_DIR/*.php $HTML_DIR
fi


# Copy valid hour series plots to RZDM
RZDM_DIR=/home/people/emc/www/htdocs/users/meg/rapv5_hrrrv4/verif/eval_period/series_validhour/
if ! [ -s $PLOT_DIR/series_validhour/done.$today ]; then
  echo $PLOT_DIR/series_validhour/done.$today not found.  Exit w/o updating scores page
  Mail -s "RAP/HRRR valid hour series plots: web page not made" Logan.Dawson@noaa.gov <<EOF
    done.$today not found
EOF
else
  scp $PLOT_DIR/series_validhour/*.png ldawson@emcrzdm:$RZDM_DIR
  scp ldawson@emcrzdm:$RZDM_DIR/*.php $HTML_DIR
fi


# Copy init date series plots to RZDM
RZDM_DIR=/home/people/emc/www/htdocs/users/meg/rapv5_hrrrv4/verif/eval_period/series_initdate/
if ! [ -s $PLOT_DIR/series_initdate/done.$today ]; then
  echo $PLOT_DIR/series_initdate/done.$today not found.  Exit w/o updating scores page
  Mail -s "RAP/HRRR init date series plots: web page not made" Logan.Dawson@noaa.gov <<EOF
    done.$today not found
EOF
#exit
else
  scp $PLOT_DIR/series_initdate/*.png ldawson@emcrzdm:$RZDM_DIR
  scp ldawson@emcrzdm:$RZDM_DIR/*.php $HTML_DIR
fi


# Copy performance diagrams to RZDM
RZDM_DIR=/home/people/emc/www/htdocs/users/meg/rapv5_hrrrv4/verif/eval_period/performance/
if ! [ -s $PLOT_DIR/performance/done.$today ]; then
  echo $PLOT_DIR/performance/done.$today not found.  Exit w/o updating scores page
  Mail -s "RAP/HRRR performance diagrams: web page not made" Logan.Dawson@noaa.gov <<EOF
    done.$today not found
EOF
#exit
else
  scp $PLOT_DIR/performance/*.png ldawson@emcrzdm:$RZDM_DIR
  scp ldawson@emcrzdm:$RZDM_DIR/*.php $HTML_DIR
fi


# Copy scorecards to RZDM
RZDM_DIR=/home/people/emc/www/htdocs/users/meg/rapv5_hrrrv4/verif/eval_period/scorecards/
if ! [ -s $PLOT_DIR/scorecards/done.$today ]; then
  echo $PLOT_DIR/scorecards/done.$today not found.  Exit w/o updating scores page
  Mail -s "RAP/HRRR scorecards: web page not made" Logan.Dawson@noaa.gov <<EOF
    done.$today not found
EOF
#exit
else
  scp $PLOT_DIR/scorecards/*.png ldawson@emcrzdm:$RZDM_DIR
  scp ldawson@emcrzdm:$RZDM_DIR/*.php $HTML_DIR
fi


# Update date line on webpages
# Only webpages with updated plots were previously copied from RZDM
webpages=$HTML_DIR/*.php
for webpage in $webpages; do

   dateline=$(grep -n "Plots updated at" $webpage | cut -f1 -d:)
   sed -e ''${dateline}'s/^Plots updated at.*/Plots updated at '${hhmm}' UTC '${dd}' '${month}' '${yyyy}'/' $webpage > tmpfile ; mv tmpfile $webpage
 
done


# Copy webpages back to RZDM
scp $HTML_DIR/*scorecard*.php ldawson@emcrzdm:$RZDM_DIR

RZDM_DIR=/home/people/emc/www/htdocs/users/meg/rapv5_hrrrv4/verif/eval_period/performance/
scp $HTML_DIR/performance*.php ldawson@emcrzdm:$RZDM_DIR

RZDM_DIR=/home/people/emc/www/htdocs/users/meg/rapv5_hrrrv4/verif/eval_period/series_fcstlead/
scp $HTML_DIR/series_fcstlead*.php ldawson@emcrzdm:$RZDM_DIR

RZDM_DIR=/home/people/emc/www/htdocs/users/meg/rapv5_hrrrv4/verif/eval_period/series_validhour/
scp $HTML_DIR/series_validhour*.php ldawson@emcrzdm:$RZDM_DIR

RZDM_DIR=/home/people/emc/www/htdocs/users/meg/rapv5_hrrrv4/verif/eval_period/series_initdate/
scp $HTML_DIR/series_initbeg*.php ldawson@emcrzdm:$RZDM_DIR

exit
