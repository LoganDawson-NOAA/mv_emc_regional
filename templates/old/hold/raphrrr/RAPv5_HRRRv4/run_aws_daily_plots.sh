#!/bin/sh

# Author: Logan Dawson
# Created 29 March 2018

set -x

now=`date -u +%Y%m%d%H`
today=${now:0:8}

NDATE=/nwprod/util/exec/ndate

DIR=/meso/save/Logan.Dawson/CAM_verif
TEMPLATE_DIR=$DIR/RAPv5_HRRRv4
SCRIPT_DIR=$TEMPLATE_DIR/runscripts
METVIEWER_DIR=$DIR/AWS/METviewer_scripts
WORK_DIR=/ptmpp2/$USER/CAM_verif/AWS/RAPv5_HRRRv4
WORK_DATA=$WORK_DIR/data
WORK_PLOTS=$WORK_DIR/plots
WORK_OUT=$WORK_DIR/out

user=`echo "$USER" | tr '[:upper:]' '[:lower:]'`

cd $TEMPLATE_DIR

mkdir -p $SCRIPT_DIR
mkdir -p $WORK_DIR

rm -f $SCRIPT_DIR/*
rm -fR $WORK_DIR/*

mkdir -p $WORK_DATA
mkdir -p $WORK_PLOTS
mkdir -p $WORK_OUT

killtime=`$NDATE 13 $now`

donetime=`$NDATE 24 $now`
today=${donetime:0:8}


#### Set up valid dates ########
#vday1=`$NDATE -768 $now | cut -c 1-8`      # today minus 32
vday1=20191010 
vday2=`$NDATE  -48 $now | cut -c 1-8`      # today minus 2 
vday1dash=${vday1:0:4}-${vday1:4:2}-${vday1:6:2}
vday2dash=${vday2:0:4}-${vday2:4:2}-${vday2:6:2}
vday1year=${vday1:0:4}
vday1moind=${vday1:4:2}
vday1day=${vday1:6:2}
vday2year=${vday2:0:4}
vday2moind=${vday2:4:2}
vday2day=${vday2:6:2}

if [ $vday1moind == "01" ]; then
   vday1month="Jan"
elif [ $vday1moind == "02" ]; then
   vday1month="Feb"
elif [ $vday1moind == "03" ]; then
   vday1month="Mar"
elif [ $vday1moind == "04" ]; then
   vday1month="Apr"
elif [ $vday1moind == "05" ]; then
   vday1month="May"
elif [ $vday1moind == "06" ]; then
   vday1month="Jun"
elif [ $vday1moind == "07" ]; then
   vday1month="Jul"
elif [ $vday1moind == "08" ]; then
   vday1month="Aug"
elif [ $vday1moind == "09" ]; then
   vday1month="Sep"
elif [ $vday1moind == "10" ]; then
   vday1month="Oct"
elif [ $vday1moind == "11" ]; then
   vday1month="Nov"
elif [ $vday1moind == "12" ]; then
   vday1month="Dec"
fi

if [ $vday2moind == "01" ]; then
   vday2month="Jan"
elif [ $vday2moind == "02" ]; then
   vday2month="Feb"
elif [ $vday2moind == "03" ]; then
   vday2month="Mar"
elif [ $vday2moind == "04" ]; then
   vday2month="Apr"
elif [ $vday2moind == "05" ]; then
   vday2month="May"
elif [ $vday2moind == "06" ]; then
   vday2month="Jun"
elif [ $vday2moind == "07" ]; then
   vday2month="Jul"
elif [ $vday2moind == "08" ]; then
   vday2month="Aug"
elif [ $vday2moind == "09" ]; then
   vday2month="Sep"
elif [ $vday2moind == "10" ]; then
   vday2month="Oct"
elif [ $vday2moind == "11" ]; then
   vday2month="Nov"
elif [ $vday2moind == "12" ]; then
   vday2month="Dec"
fi

pcp_vday1=`$NDATE -912 $now | cut -c 1-8`  #today minus 38
pcp_vday2=`$NDATE -216 $now | cut -c 1-8`  #today minus 9
pcp_vday1dash=${vday1:0:4}-${vday1:4:2}-${vday1:6:2}
pcp_vday2dash=${vday2:0:4}-${vday2:4:2}-${vday2:6:2}

valid_date1="%VDAY1%"
valid_date2="%VDAY2%"
valid_dash1=$vday1dash
valid_dash2=$vday2dash



#######################################################################
# Generate forecast lead series plots 
#######################################################################
scripts0="sfc upper upperwind ceiling vis cape"
scripts0="sfc upper upperwind cape"
scripts0="sfc_z2 sfc_z10 sfc_z0"
plevs="50 100 150 200 250 300 400 500 700 850 1000"
cape_thresh="500 1000 1500 2000 3000 4000"
apcp_thresh=".01 .10 .25 .50 .75 1.0 1.5 2.0 3.0 4.0"
apcp_thresh2=(0.01 0.10 0.25 0.50 0.75 1 1.5 2 3 4)
apcp_thresh3=(0p01 0p10 0p25 0p50 0p75 1p0 1p5 2p0 3p0 4p0)
cycles="00 03 06 09 12 15 18 21"


for script in $scripts0; do

   #Set up new script name
   new_script=series_fcstlead_${script}.xml
   echo $new_script

   for cycle in $cycles; do

      # Replace beginning valid date
      sed 's/'${valid_date1}'/'${valid_dash1}'/' series_fcstlead_${script}.xml > $SCRIPT_DIR/tmp.file1
      # Replace ending valid date
      sed 's/'${valid_date2}'/'${valid_dash2}'/' $SCRIPT_DIR/tmp.file1 > $SCRIPT_DIR/tmp.file2

      # Replace cycle in plot fix
      sed 's/%CC%/'${cycle}'/' $SCRIPT_DIR/tmp.file2 > $SCRIPT_DIR/tmp.file3

      # Replace dates in plot title
      title_linenum=$(grep -n "<title>" $new_script | cut -f1 -d:)

      sed ''${title_linenum}'s/%DD1%/'${vday1day}'/' $SCRIPT_DIR/tmp.file3 > $SCRIPT_DIR/tmp.file4
      sed ''${title_linenum}'s/%MMM1%/'${vday1month}'/' $SCRIPT_DIR/tmp.file4 > $SCRIPT_DIR/tmp.file5
      sed ''${title_linenum}'s/%YYYY1%/'${vday1year}'/' $SCRIPT_DIR/tmp.file5 > $SCRIPT_DIR/tmp.file6

      sed ''${title_linenum}'s/%DD2%/'${vday2day}'/' $SCRIPT_DIR/tmp.file6 > $SCRIPT_DIR/tmp.file7
      sed ''${title_linenum}'s/%MMM2%/'${vday2month}'/' $SCRIPT_DIR/tmp.file7 > $SCRIPT_DIR/tmp.file8
      sed ''${title_linenum}'s/%YYYY2%/'${vday2year}'/' $SCRIPT_DIR/tmp.file8 > $SCRIPT_DIR/$new_script


      if [[ ${script} == "upper" || ${script} == "upperwind" ]]; then
         mv $SCRIPT_DIR/$new_script $SCRIPT_DIR/tmp.file9

         for plev in $plevs; do
            sed 's/%PPP%/'${plev}'/g' $SCRIPT_DIR/tmp.file9 > $SCRIPT_DIR/$new_script
            chmod +x $SCRIPT_DIR/$new_script
#           $METVIEWER_DIR/mv_batch_on_aws.sh $user $WORK_PLOTS $SCRIPT_DIR/$new_script > $WORK_OUT/${new_script}.out
         done

         rm $SCRIPT_DIR/tmp.file*

      elif [[ ${script} == "cape" ]]; then
         mv $SCRIPT_DIR/$new_script $SCRIPT_DIR/tmp.file9

         for thresh in $cape_thresh; do
            sed 's/%THRESH%/'${thresh}'/g' $SCRIPT_DIR/tmp.file9 > $SCRIPT_DIR/$new_script
            chmod +x $SCRIPT_DIR/$new_script
#           $METVIEWER_DIR/mv_batch_on_aws.sh $user $WORK_PLOTS $SCRIPT_DIR/$new_script > $WORK_OUT/${new_script}.out
         done

         rm $SCRIPT_DIR/tmp.file*

      else
         chmod +x $SCRIPT_DIR/$new_script
         rm $SCRIPT_DIR/tmp.file*
          $METVIEWER_DIR/mv_batch_on_aws.sh $user $WORK_PLOTS $SCRIPT_DIR/$new_script > $WORK_OUT/${new_script}.out
      fi

   done

done


# Prepare for move to rzdm
nfiles=$(ls -l $WORK_PLOTS/* | grep png | wc -l)
if [[ $number > 100 ]];then
   mkdir -p $WORK_PLOTS/series_fcstlead 
   rm -f $WORK_PLOTS/series_fcstlead/*
   mv $WORK_PLOTS/*.png $WORK_PLOTS/series_fcstlead

cat > $WORK_PLOTS/series_fcstlead/done.$today <<EOF1
Finished making forecast lead series plots
EOF1
   date >> $WORK_PLOTS/series_fcstlead/done.$today
fi


#######################################################################
# Generate initialization date series plots 
#######################################################################


scripts0="sfc upper upperwind cape ceiling vis refl"
scripts0="sfc upper upperwind cape"
scripts0=""
cycles="00 03 06 09 12 15 18 21"


# Loop over script/variable list 
for script in $scripts0; do

   #Set up new script name
   new_script=series_initbeg_${script}.xml

   for cycle in $cycles; do

      if [[ ${script} == "sfc" || ${script} == "ceiling" || ${script} == "vis" || ${script} == "refl" ]]; then
         fhrs1=(0 6 12 18 24 30 36)
         fhrs2="00 06 12 18 24 30 36"
      elif [[ ${script} == "upper" || ${script} == "upperwind" || ${script} == "cape" ]]; then
         if [[ ${cycle} == "00" || ${cycle} == "12" ]]; then
            fhrs1=(0 12 24 36)
            fhrs2="00 12 24 36"
         elif [[ ${cycle} == "03" || ${cycle} == "15" ]]; then
            fhrs1=(9 21 33)
            fhrs2="09 21 33"
         elif [[ ${cycle} == "06" || ${cycle} == "18" ]]; then
            fhrs1=(6 18 30)
            fhrs2="06 18 30"
         elif [[ ${cycle} == "09" || ${cycle} == "21" ]]; then
            fhrs1=(3 15 27 39)
            fhrs2="03 15 22 39"
         fi
      elif [[ ${script} == "24hpcp" ]]; then
         fhrs1=(36)
         fhrs2="36"
      fi


      # Replace beginning valid date
      sed 's/'${valid_date1}'/'${valid_dash1}'/' series_initbeg_${script}.xml > $SCRIPT_DIR/tmp.file1
      # Replace ending valid date
      sed 's/'${valid_date2}'/'${valid_dash2}'/' $SCRIPT_DIR/tmp.file1 > $SCRIPT_DIR/tmp.file2

      # Replace cycle in plot fix
      sed 's/%CC%/'${cycle}'/' $SCRIPT_DIR/tmp.file2 > $SCRIPT_DIR/tmp.file3

      # Replace dates in plot title
      title_linenum=$(grep -n "<title>" $new_script | cut -f1 -d:)

      sed ''${title_linenum}'s/%DD1%/'${vday1day}'/' $SCRIPT_DIR/tmp.file3 > $SCRIPT_DIR/tmp.file4
      sed ''${title_linenum}'s/%MMM1%/'${vday1month}'/' $SCRIPT_DIR/tmp.file4 > $SCRIPT_DIR/tmp.file5
      sed ''${title_linenum}'s/%YYYY1%/'${vday1year}'/' $SCRIPT_DIR/tmp.file5 > $SCRIPT_DIR/tmp.file6

      sed ''${title_linenum}'s/%DD2%/'${vday2day}'/' $SCRIPT_DIR/tmp.file6 > $SCRIPT_DIR/tmp.file7
      sed ''${title_linenum}'s/%MMM2%/'${vday2month}'/' $SCRIPT_DIR/tmp.file7 > $SCRIPT_DIR/tmp.file8
      sed ''${title_linenum}'s/%YYYY2%/'${vday2year}'/' $SCRIPT_DIR/tmp.file8 > $SCRIPT_DIR/tmp.file9


      i=0
      for fhr2 in $fhrs2; do
         sed 's/%F%/'${fhrs1[$i]}'/g' $SCRIPT_DIR/tmp.file9 > $SCRIPT_DIR/tmp.file10
         sed 's/%FF%/'${fhr2}'/g' $SCRIPT_DIR/tmp.file10 > $SCRIPT_DIR/$new_script

         if [[ ${script} == "upper" || ${script} == "upperwind" ]]; then
            mv $SCRIPT_DIR/$new_script $SCRIPT_DIR/tmp.file11

            for plev in $plevs; do
               sed 's/%PPP%/'${plev}'/g' $SCRIPT_DIR/tmp.file11 > $SCRIPT_DIR/$new_script
               chmod +x $SCRIPT_DIR/$new_script
        #       $METVIEWER_DIR/mv_batch_on_aws.sh $user $WORK_PLOTS $SCRIPT_DIR/$new_script > $WORK_OUT/${new_script}.out
            done

         elif [[ ${script} == "cape" ]]; then
            mv $SCRIPT_DIR/$new_script $SCRIPT_DIR/tmp.file11

            for thresh in $cape_thresh; do
               sed 's/%THRESH%/'${thresh}'/g' $SCRIPT_DIR/tmp.file11 > $SCRIPT_DIR/$new_script
               chmod +x $SCRIPT_DIR/$new_script
         #      $METVIEWER_DIR/mv_batch_on_aws.sh $user $WORK_PLOTS $SCRIPT_DIR/$new_script > $WORK_OUT/${new_script}.out
            done

         else
            chmod +x $SCRIPT_DIR/$new_script
       #     $METVIEWER_DIR/mv_batch_on_aws.sh $user $WORK_PLOTS $SCRIPT_DIR/$new_script > $WORK_OUT/${new_script}.out
         fi

         let "i++"
      done  # end of fhrs loop

      rm $SCRIPT_DIR/tmp.file*

   done  # end of cycles loop

done   # end of scripts/variables loop



# Prepare for move to rzdm
nfiles=$(ls -l $WORK_PLOTS/* | grep png | wc -l)
if [[ $number > 100 ]];then
   mkdir -p $WORK_PLOTS/series_initdate
   rm -f $WORK_PLOTS/series_initdate/*
   mv $WORK_PLOTS/*.png $WORK_PLOTS/series_initdate

cat > $WORK_PLOTS/series_initdate/done.$today <<EOF2
   Finished making init date series plots
EOF2
   date >> $WORK_PLOTS/series_initdate/done.$today
fi

#######################################################################
# Generate valid hour series plots 
#######################################################################

scripts0="sfc_z2 sfc_z0 sfc_z10"

# Loop over script/variable list 
for script in $scripts0; do

   #Set up new script name
   new_script=series_validhour_${script}.xml


 # if [[ ${script} == "sfc" || ${script} == "ceiling" || ${script} == "vis" || ${script} == "refl" ]]; then
   if [[ ${script} == "sfc_z2" || ${script} == "sfc_z10" || ${script} == "sfc_z0" || ${script} == "refl" ]]; then
      fhrs1=(0 3 6 9 12 15 18 21 24 27 30 33 36 39)
      fhrs2="00 03 06 09 12 15 18 21 24 27 30 33 36 39"
   elif [[ ${script} == "upper" || ${script} == "upperwind" || ${script} == "cape" ]]; then
      fhrs1=(0 6 12 18 24 30 36)
      fhrs2="00 06 12 18 24 30 36"
   elif [[ ${script} == "24hpcp" ]]; then
      fhrs1=(36)
      fhrs2="36"
   fi


   # Replace beginning valid date
   sed 's/'${valid_date1}'/'${valid_dash1}'/' series_validhour_${script}.xml > $SCRIPT_DIR/tmp.file1
   # Replace ending valid date
   sed 's/'${valid_date2}'/'${valid_dash2}'/' $SCRIPT_DIR/tmp.file1 > $SCRIPT_DIR/tmp.file2

   # Replace dates in plot title
   title_linenum=$(grep -n "<title>" $new_script | cut -f1 -d:)

   sed ''${title_linenum}'s/%DD1%/'${vday1day}'/' $SCRIPT_DIR/tmp.file2 > $SCRIPT_DIR/tmp.file3
   sed ''${title_linenum}'s/%MMM1%/'${vday1month}'/' $SCRIPT_DIR/tmp.file3 > $SCRIPT_DIR/tmp.file4
   sed ''${title_linenum}'s/%YYYY1%/'${vday1year}'/' $SCRIPT_DIR/tmp.file4 > $SCRIPT_DIR/tmp.file5

   sed ''${title_linenum}'s/%DD2%/'${vday2day}'/' $SCRIPT_DIR/tmp.file5 > $SCRIPT_DIR/tmp.file6
   sed ''${title_linenum}'s/%MMM2%/'${vday2month}'/' $SCRIPT_DIR/tmp.file6 > $SCRIPT_DIR/tmp.file7
   sed ''${title_linenum}'s/%YYYY2%/'${vday2year}'/' $SCRIPT_DIR/tmp.file7 > $SCRIPT_DIR/tmp.file8


   i=0
   for fhr2 in $fhrs2; do
 
      fhr_int="$((${fhrs1[$i]} * 10000))"
      sed 's/%F%/'${fhr_int}'/g' $SCRIPT_DIR/tmp.file8 > $SCRIPT_DIR/tmp.file9
      sed 's/%FF%/'${fhr2}'/g' $SCRIPT_DIR/tmp.file9 > $SCRIPT_DIR/$new_script

      if [[ ${script} == "upper" || ${script} == "upperwind" ]]; then
         mv $SCRIPT_DIR/$new_script $SCRIPT_DIR/tmp.file10

         for plev in $plevs; do
            sed 's/%PPP%/'${plev}'/g' $SCRIPT_DIR/tmp.file10 > $SCRIPT_DIR/$new_script
            chmod +x $SCRIPT_DIR/$new_script
       #     $METVIEWER_DIR/mv_batch_on_aws.sh $user $WORK_PLOTS $SCRIPT_DIR/$new_script > $WORK_OUT/${new_script}.out
         done

      elif [[ ${script} == "cape" ]]; then
         mv $SCRIPT_DIR/$new_script $SCRIPT_DIR/tmp.file10

         for thresh in $cape_thresh; do
            sed 's/%THRESH%/'${thresh}'/g' $SCRIPT_DIR/tmp.file10 > $SCRIPT_DIR/$new_script
            chmod +x $SCRIPT_DIR/$new_script
       #     $METVIEWER_DIR/mv_batch_on_aws.sh $user $WORK_PLOTS $SCRIPT_DIR/$new_script > $WORK_OUT/${new_script}.out
         done

      else
         chmod +x $SCRIPT_DIR/$new_script
          $METVIEWER_DIR/mv_batch_on_aws.sh $user $WORK_PLOTS $SCRIPT_DIR/$new_script > $WORK_OUT/${new_script}.out
      fi

      let "i++"
   done  # end of fhrs loop

   rm $SCRIPT_DIR/tmp.file*

done   # end of scripts/variables loop


# Prepare for move to rzdm
nfiles=$(ls -l $WORK_PLOTS/* | grep png | wc -l)
if [[ $number > 100 ]];then
   mkdir -p $WORK_PLOTS/series_validhour
   rm -f $WORK_PLOTS/series_validhour/*
   mv $WORK_PLOTS/*.png $WORK_PLOTS/series_validhour

cat > $WORK_PLOTS/series_validhour/done.$today <<EOF3
   Finished making valid hour series plots
EOF3
   date >> $WORK_PLOTS/series_validhour/done.$today
fi


#Mail -s "FV3CAM series plots complete" Logan.Dawson@noaa.gov <<EOF2
#    $today FV3CAM series plots complete
#EOF2


#######################################################################
# Generate forecast threshold performance diagrams 
#######################################################################

scripts0="fcstthresh3_24hpcp fcstthresh_24hpcp fcstthresh3_cape fcstthresh_cape"
scripts0=""

# Loop over script/variable list 
for script in $scripts0; do

   #Set up new script name
   new_script=perf_${script}.xml

   if [[ ${script} == "fcstthresh3_refl" || ${script} == "fcstthresh_refl" ]]; then
      cycles="00 03 06 09 12 15 18 21"
   elif [[ ${script} == "fcstthresh3_cape" || ${script} == "fcstthresh_cape" ]]; then
      cycles="00 03 06 09 12 15 18 21"
   elif [[ ${script} == "fcstthresh3_24hpcp" || ${script} == "fcstthresh_24hpcp" ]]; then
      cycles="00 03 06 09 12 21"
   fi

   for cycle in $cycles; do

      if [[ ${script} == "fcstthresh3_refl" || ${script} == "fcstthresh_refl" ]]; then
         fhrs1=(0 3 6 9 12 15 18 21 24 27 30 33 36 39)
         fhrs2="00 03 06 09 12 15 18 21 24 27 30 33 36 39"
      elif [[ ${script} == "fcstthresh3_cape" || ${script} == "fcstthresh_cape" ]]; then
         if [[ ${cycle} == "00" || ${cycle} == "12" ]]; then
            fhrs1=(0 12 24 36)
            fhrs2="00 12 24 36"
         elif [[ ${cycle} == "03" || ${cycle} == "15" ]]; then
            fhrs1=(9 21 33)
            fhrs2="09 21 33"
         elif [[ ${cycle} == "06" || ${cycle} == "18" ]]; then
            fhrs1=(6 18 30)
            fhrs2="06 18 30"
         elif [[ ${cycle} == "09" || ${cycle} == "21" ]]; then
            fhrs1=(3 15 27 39)
            fhrs2="03 15 22 39"
         fi
      elif [[ ${script} == "fcstthresh3_24hpcp" || ${script} == "fcstthresh_24hpcp" ]]; then
         if [[ ${cycle} == "00" ]]; then
            fhrs1=(36)
            fhrs2="36"
         elif [[ ${cycle} == "03" ]]; then
            fhrs1=(33)
            fhrs2="33"
         elif [[ ${cycle} == "06" ]]; then
            fhrs1=(30)
            fhrs2="30"
         elif [[ ${cycle} == "09" ]]; then
            fhrs1=(27)
            fhrs2="27"
         elif [[ ${cycle} == "12" ]]; then
            fhrs1=(24)
            fhrs2="24"
         elif [[ ${cycle} == "21" ]]; then
            fhrs1=(39)
            fhrs2="39"
         fi
      fi


      # Replace beginning valid date
      sed 's/'${valid_date1}'/'${valid_dash1}'/' perf_${script}.xml > $SCRIPT_DIR/tmp.file1
      # Replace ending valid date
      sed 's/'${valid_date2}'/'${valid_dash2}'/' $SCRIPT_DIR/tmp.file1 > $SCRIPT_DIR/tmp.file2

      # Replace cycle in plot fix
      sed 's/%CC%/'${cycle}'/' $SCRIPT_DIR/tmp.file2 > $SCRIPT_DIR/tmp.file3

      # Replace dates in plot title
      title_linenum=$(grep -n "<title>" $new_script | cut -f1 -d:)

      sed ''${title_linenum}'s/%DD1%/'${vday1day}'/' $SCRIPT_DIR/tmp.file3 > $SCRIPT_DIR/tmp.file4
      sed ''${title_linenum}'s/%MMM1%/'${vday1month}'/' $SCRIPT_DIR/tmp.file4 > $SCRIPT_DIR/tmp.file5
      sed ''${title_linenum}'s/%YYYY1%/'${vday1year}'/' $SCRIPT_DIR/tmp.file5 > $SCRIPT_DIR/tmp.file6

      sed ''${title_linenum}'s/%DD2%/'${vday2day}'/' $SCRIPT_DIR/tmp.file6 > $SCRIPT_DIR/tmp.file7
      sed ''${title_linenum}'s/%MMM2%/'${vday2month}'/' $SCRIPT_DIR/tmp.file7 > $SCRIPT_DIR/tmp.file8
      sed ''${title_linenum}'s/%YYYY2%/'${vday2year}'/' $SCRIPT_DIR/tmp.file8 > $SCRIPT_DIR/tmp.file9


      i=0
      for fhr2 in $fhrs2; do
         sed 's/%F%/'${fhrs1[$i]}'/g' $SCRIPT_DIR/tmp.file9 > $SCRIPT_DIR/tmp.file10
         sed 's/%FF%/'${fhr2}'/g' $SCRIPT_DIR/tmp.file10 > $SCRIPT_DIR/$new_script

         if [[ ${script} == "fcstthresh_cape" ]]; then
            mv $SCRIPT_DIR/$new_script $SCRIPT_DIR/tmp.file11

            for thresh in $cape_thresh; do
               sed 's/%THRESH%/'${thresh}'/g' $SCRIPT_DIR/tmp.file11 > $SCRIPT_DIR/$new_script
               chmod +x $SCRIPT_DIR/$new_script
         #      $METVIEWER_DIR/mv_batch_on_aws.sh $user $WORK_PLOTS $SCRIPT_DIR/$new_script > $WORK_OUT/${new_script}.out
            done

         elif [[ ${script} == "fcstthresh_24hpcp" ]]; then
            mv $SCRIPT_DIR/$new_script $SCRIPT_DIR/tmp.file11

            j=0
            for thresh in $apcp_thresh; do
               sed 's/%THRESH%/'${thresh}'/g' $SCRIPT_DIR/tmp.file11 > $SCRIPT_DIR/tmp.file12
               sed 's/%THRESH2%/'${apcp_thresh2[$j]}'/g' $SCRIPT_DIR/tmp.file12 > $SCRIPT_DIR/tmp.file13
               sed 's/%THRESH3%/'${apcp_thresh3[$j]}'/g' $SCRIPT_DIR/tmp.file13 > $SCRIPT_DIR/$new_script
               chmod +x $SCRIPT_DIR/$new_script
        #       $METVIEWER_DIR/mv_batch_on_aws.sh $user $WORK_PLOTS $SCRIPT_DIR/$new_script > $WORK_OUT/${new_script}.out
               let "j++"
            done

         else
            chmod +x $SCRIPT_DIR/$new_script
       #     $METVIEWER_DIR/mv_batch_on_aws.sh $user $WORK_PLOTS $SCRIPT_DIR/$new_script > $WORK_OUT/${new_script}.out
         fi

         let "i++"
      done  # end of fhrs loop

      rm $SCRIPT_DIR/tmp.file*

   done   # end of cycles loop

done   # end of scripts/variables loop


# Prepare for move to rzdm
nfiles=$(ls -l $WORK_PLOTS/* | grep png | wc -l)
if [[ $number > 100 ]];then
   mkdir -p $WORK_PLOTS/performance
   rm -f $WORK_PLOTS/performance/*
   mv $WORK_PLOTS/*perf*.png $WORK_PLOTS/performance

cat > $WORK_PLOTS/performance/done.$today <<EOF
Finished making performance diagrams
EOF
   date >> $WORK_PLOTS/performance/done.$today
fi



#######################################################################
# Create XMLs for scorecard comparisons
#######################################################################
scripts2="24hpcp 6hpcp sfc upper cape cv refl"
scripts2="24hpcp 6hpcp"
scripts2=""

MODELS=( HRRR RAP )
MODEL_LABELS=( HRRRv3 RAPv4 )
MODELX_LABELS=( HRRRv4  RAPv5 )
models=( hrrrv3  rapv4 )
modelxs=( hrrrv4 rapv5 )
GRIDS=( 255 130 )

len=${#models[@]}

k=0
for script in $scripts2; do

   data_linenum=$(grep -n "<data_file>" $script | cut -f1 -d:)
   plot_linenum=$(grep -n "<plot_file>" $script | cut -f1 -d:)
   title_linenum=$(grep -n "<title>" $script | cut -f1 -d:)
   data_line=$(grep "<data_file>" $script | cut -c 31-33)
   plot_line=$(grep "<plot_file>" $script | cut -c 31-33)
   title_line=$(grep "<title>" $script | cut -c 17-19)
   echo $data_line
   echo $plot_line
   echo $title_line


   if [[ $script == "24hpcp" || $script == "6hpcp" ]]; then
      valid_dash1=$pcp_vday1dash
      valid_dash2=$pcp_vday2dash
   else
      valid_dash1=$vday1dash
      valid_dash2=$vday2dash
   fi


   for (( i=0; i<$len; i++ )); do

      #Set up new script name
      new_script=${modelxs[$i]}_${script}_scorecard.xml
      echo $new_script


      # Replace model name
      sed 's/%MODEL%/'${MODELS[$i]}'/' scorecard_$script.xml > $SCRIPT_DIR/tmp.file1
      sed 's/%MODEL_LABEL%/'${MODEL_LABELS[$i]}'/' $SCRIPT_DIR/tmp.file1 > $SCRIPT_DIR/tmp.file2
      sed 's/%MODELX_LABEL%/'${MODELX_LABELS[$i]}'/' $SCRIPT_DIR/tmp.file2 > $SCRIPT_DIR/tmp.file3
      sed 's/%model%/'${models[$i]}'/' $SCRIPT_DIR/tmp.file3 > $SCRIPT_DIR/tmp.file4
      sed 's/%modelx%/'${modelxs[$i]}'/' $SCRIPT_DIR/tmp.file4 > $SCRIPT_DIR/tmp.file5
      # Replace beginning valid date
      sed 's/'${valid_date1}'/'${valid_dash1}'/' $SCRIPT_DIR/tmp.file5 > $SCRIPT_DIR/tmp.file6
      # Replace ending valid date
      sed 's/'${valid_date2}'/'${valid_dash2}'/' $SCRIPT_DIR/tmp.file6 > $SCRIPT_DIR/$new_script

      # Replace grid definition for mv_emc_g2o scorecards
      if [[ ${script} != "24hpcp" && ${script} != "6hpcp" ]]; then
         mv $SCRIPT_DIR/$new_script $SCRIPT_DIR/tmp.file7
         sed 's/%GGG%/'${GRIDS[$i]}'/' $SCRIPT_DIR/tmp.file7 > $SCRIPT_DIR/$new_script
      fi

      chmod +x $SCRIPT_DIR/$new_script
      rm $SCRIPT_DIR/tmp.file*

      $METVIEWER_DIR/mv_scorecard_on_aws.sh $user $WORK_PLOTS $SCRIPT_DIR/$new_script > $WORK_OUT/${new_script}.out

#     ncards=`ps -C mv_scorecard.sh --no-headers | wc -l`
#     if [ $ncards -le 5 ]; then
#        $METVIEWER_DIR/mv_scorecard_on_aws.sh $user $WORK_PLOTS $SCRIPT_DIR/$new_script > $WORK_OUT/${new_script}.out
#        sleep 5
#     else
#        ncards=`ps -C mv_scorecard.sh --no-headers | wc -l`
#        while [ $ncards -ge 5  ]; do
#           sleep 5m
#           ncards=`ps -C mv_scorecard.sh --no-headers | wc -l`
#        done
#        $AWS_SCORECARD_COMMAND $SCRIPT_DIR/$new_script >& $WORK_OUT/${new_script}.out &
#        sleep 5
#     fi



   done
   let "k++"

done

exit

# Wait until scorecards are done
nfiles=`ls $WORK_PLOTS/*.png -1 | wc -l`
#while [ $nfiles -lt 14 ]; do
while [ $nfiles -lt 4 ]; do

   now1=`date -u +%Y%m%d%H`
   if [[ $now1 > $killtime ]]; then
      echo "exiting script after 13 hrs"

         cat > $WORK_PLOTS/scorecards/done.$today <<EOF4
         Didn't finish making scorecards, but exiting now
EOF4
         date >> $WORK_PLOTS/scorecards/done.$today

         mv $WORK_PLOTS/*.png $WORK_PLOTS/scorecards

Mail -s "RAP/HRRR scorecards did not complete" Logan.Dawson@noaa.gov <<EOF5
    $today RAP/HRRR scorecards did not complete
EOF5

      exit
   fi

   echo "waiting for RAP/HRRR scorecards to complete"
   sleep 10m
   nfiles=`ls $WORK_PLOTS/*.png -1 | wc -l`
done
echo "RAP/HRRR scorecards finished at `date`"



# Prepare for move to rzdm
mkdir -p $WORK_PLOTS/scorecards/
rm -f $WORK_PLOTS/scorecards/*
mv $WORK_PLOTS/*.png $WORK_PLOTS/scorecards

cat > $WORK_PLOTS/scorecards/done.$today <<EOF5
Finished making scorecards
EOF5
date >> $WORK_PLOTS/scorecards/done.$today


exit

