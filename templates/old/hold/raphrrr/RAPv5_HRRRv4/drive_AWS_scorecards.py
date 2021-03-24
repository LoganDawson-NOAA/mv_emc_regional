import sys
import datetime
import shutil
import os
import subprocess
import re

# Function to do multiple replacements using re.sub
# From: https://stackoverflow.com/questions/15175142/how-can-i-do-multiple-substitutions-using-regex-in-python
def multiple_replace(dict, text):
    # Create a regular expression  from the dictionary keys
    regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))

    # For each match, look-up corresponding value in dictionary
    return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text) 

    if __name__ == "__main__": 

        text = "Larry Wall is the creator of Perl"

        dict = {
            "Larry Wall" : "Guido van Rossum",
            "creator" : "Benevolent Dictator for Life",
            "Perl" : "Python",
        } 

        print multiple_replace(dict, text)


# Function to create final xml using template and  multiple_replace function
def modify_scorecard_xml(template_xml, scorecard_xml):

    replacements = {
        "%MODELX%"       : str.upper(para),
        "%MODEL%"        : str.upper(prod),
        "%MODELX_LABEL%" : para_label,
        "%MODEL_LABEL%"  : prod_label,
        "%VDAY1%"        : "2019-10-15",
        "%VDAY2%"        : "2019-10-16",
        "%modelx%"       : str.lower(para_label),
        "%model%"        : str.lower(prod_label),
        "%GGG%"          : str.upper(vx_mask[0]),
        "%GGG_LABEL%"    : str.upper(regions[0]),
        "%region%"       : str.lower(regions[0]),
    } 

    with open(template_xml) as f:
        new_text = multiple_replace(replacements, f.read())

    with open(scorecard_xml, "w") as result:
        result.write(new_text)





# Loop through to generate scorecard xmls
prods = ['RAP','RAPAK','HRRRAK','HRRR']
paras = ['RAPX','RAPXAK','HRRRXAK','HRRRX']
prod_labels = ['RAPv4','RAPv4','HRRRv3-AK','HRRRv3']
para_labels = ['RAPv5','RAPv5','HRRRv4-AK','HRRRv4']

for i in xrange(len(prods)):
    prod = prods[i]
    para = paras[i]
    prod_label = prod_labels[i]
    para_label = para_labels[i]


    if prod[-2:] == 'AK' and para[-2:] == 'AK':
        scorecards = ['sfc','upper','24hpcp']
        regions = ['Alaska']
    else:
        scorecards = ['sfc','upper','24hpcp','6hpcp','cape','refl','cv']
        scorecards = ['sfc','upper','cape','cv']
        regions = ['CONUS']
        vx_mask = ['G236']


    for scorecard in scorecards:
        template_xml = 'scorecard_'+scorecard+'.xml'
        scorecard_xml = '/meso/save/Logan.Dawson/CAM_verif/RAPv5_HRRRv4/runscripts/'+str.lower(para_label)+'_'+str.lower(prod_label)+'_'+scorecard+'_scorecard.xml'

        modify_scorecard_xml(template_xml,scorecard_xml)

        
# Loop through to generate performance xmls
domains = ['CONUS','Alaska','East','West']

for region in regions:
    if region == 'Alaska':
        diags = ['ceiling','vis']
    else:
        diags = ['ceiling','vis','cape','24hpcp','refc','retop']



