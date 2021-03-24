import sys
import datetime
import shutil
import os 
import subprocess

METviewer_AWS_scripts_dir = "/gpfs/td1/emc/meso/save/Logan.Dawson/CAM_verif/AWS/METviewer_scripts"



### CREATE SCORECARD XML
scorecard_sfc_xml_file = os.path.join(os.path.join(os.getcwd(), "load_"+mv_database+".xml"))


# Function to write scorecard xml

def write_sfc_scorecard(xml_filename):

    if os.path.exists(xml_filename):
        os.remove(xml_filename)

    with open(load_xml_file, 'a') as xml:
        xml.write("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n")
        xml.write("<plot_spec>\n")
        xml.write("  <connection>\n")
        xml.write("    <host>metviewer-dev-cluster.cluster-czbts4gd2wm2.us-east-1.rds.amazonaws.com:3306</host>\n")
        xml.write("    <database>"+mv_database+"</database>\n")
        xml.write("    <user>rds_pwd</user>\n")
        xml.write("    <password>rds_pwd</password>\n")
        xml.write("  </connection>\n")
        xml.write("\n")
        xml.write("  <rscript>Rscript</rscript>\n")
        xml.write("  <folders>\n")
        xml.write("    <r_tmpl>rds_R_tmpl</r_tmpl>\n")
        xml.write("    <r_work>rds_R_work</r_work>\n")
        xml.write("    <plots>rds_plots</plots>\n")
        xml.write("    <data>rds_data</data>\n")
        xml.write("    <scripts>rds_scripts</scripts>\n")
        xml.write("  </folders>\n")
        xml.write("  <plot>\n")
        xml.write("    <view_value>true</view_value>\n")
        xml.write("    <view_symbol>true</view_symbol>\n")
        xml.write("    <view_legend>true</view_legend>\n")
        xml.write("    <printSQL>true</printSQL>\n")
        xml.write("    <stat_flag>NCAR</stat_flag>\n")
        xml.write("    <stat_value>DIFF</stat_value>\n")
        xml.write("    <stat_symbol>DIFF_SIG</stat_value>\n")
        xml.write("\n")





### PASSED AGRUEMENTS
mv_database = sys.argv[1]
new_or_add = sys.argv[2]
start_date = sys.argv[3]
end_date = sys.argv[4]

### DATABASE INFORMATION
print("=============== METviewer AWS database "+mv_database+" ===============")
if  mv_database == "mv_ldawson_refl_test":
    mv_desc = "METplus grid-to-grid reflectivity verification"
    mv_group = "ldawson"
    data_dir = "/gpfs/tp2/ptmp/Logan.Dawson/CAM_verif"
    models = [ "CONUSNEST", "FV3SAR", "FV3SARX","GFS", "HRRR", "RAP"]
    subdirs = [ "CONUSNEST", "FV3SAR", "FV3SARX","GFS", "HRRR", "RAP"]
    file_date_format = "%Y%m%d"
    file_format_list = [ "MODEL_DATE.stat" ]
    met_version = "8.1"
    date_inc = datetime.timedelta(hours=24)
elif mv_database == "mv_fv3cam_g2o":
    mv_desc = "Grid-to-obs VSDB data for FV3NEST and FV3SAR"
    mv_group = "ldawson"
    data_dir = "/meso/noscrub/Logan.Dawson/CAM_verif/SAR_paper"
    models = [ "fv3nest", "fv3sar"]
    file_date_format = "%Y%m%d"
    file_format_list = [ "MODEL_DATE.vsdb" ]
    met_version = "8.1"
    date_inc = datetime.timedelta(hours=24)
else:
    print(mv_database+" not recongized.")
    exit()


### COPY DATA TO TMP DIRECTORY TO AVOID
### COPYING UNNCESSARY FILES
sdate = datetime.datetime(int(start_date[0:4]), int(start_date[4:6]), int(start_date[6:]))
edate = datetime.datetime(int(end_date[0:4]), int(end_date[4:6]), int(end_date[6:]))
tmp_data_dir = os.path.join(os.getcwd(), 'tmp_data_'+mv_database)
print("1) Linking data from "+data_dir+" to "+os.path.join(os.getcwd(), tmp_data_dir))
if os.path.exists(tmp_data_dir):
    shutil.rmtree(tmp_data_dir)
os.makedirs(tmp_data_dir)

for model in models:
    date = sdate
    while date <= edate:
        file_date = date.strftime(file_date_format)
        for file_format in file_format_list:
            file_name = file_format.replace('MODEL', model).replace('DATE', file_date)
            full_file_name = os.path.join(data_dir, model, file_name)
            link_file_name_prefix = file_name.split(".")[0]
            link_file_name_suffix = file_name.split(".")[1]
            link_file_name = link_file_name_prefix
            link_file_name = link_file_name+"."+link_file_name_suffix
            full_link_file_name = os.path.join(os.getcwd(), tmp_data_dir, link_file_name)
            if os.path.exists(full_file_name):
                print("Linking "+full_file_name+" as "+full_link_file_name)
                subprocess.call(['ln', '-sf', full_file_name, full_link_file_name])
            else:
                print(full_file_name+" does not exist")
        date = date + date_inc


### CREATE LOAD XML
load_xml_file = os.path.join(os.path.join(os.getcwd(), "load_"+mv_database+".xml"))
print("2) Creating load xml "+load_xml_file)
if new_or_add == "new":
    drop_index = "false"
else:
    drop_index = "true"
if os.path.exists(load_xml_file):
    os.remove(load_xml_file)
with open(load_xml_file, 'a') as xml:
    xml.write("<load_spec>\n")
    xml.write("  <connection>\n")
    xml.write("    <host>metviewer-dev-cluster.cluster-czbts4gd2wm2.us-east-1.rds.amazonaws.com:3306</host>\n")
    xml.write("    <database>"+mv_database+"</database>\n")
    xml.write("    <user>rds_user</user>\n")
    xml.write("    <password>rds_pwd</password>\n")
    xml.write("    <management_system>aurora</management_system>\n")
    xml.write("  </connection>\n")
    xml.write("\n")
    xml.write("  <met_version>V"+met_version+"</met_version>\n")
    xml.write("\n")
    xml.write("  <verbose>true</verbose>\n")
    xml.write("  <insert_size>1</insert_size>\n")
    xml.write("  <mode_header_db_check>true</mode_header_db_check>\n")
    xml.write("  <stat_header_db_check>true</stat_header_db_check>\n")
    xml.write("  <drop_indexes>"+drop_index+"</drop_indexes>\n")
    xml.write("  <apply_indexes>true</apply_indexes>\n")
    xml.write("  <load_stat>true</load_stat>\n")
    xml.write("  <load_mode>true</load_mode>\n")
    xml.write("  <load_mpr>true</load_mpr>\n")
    xml.write("  <load_orank>true</load_orank>\n")
    xml.write("  <force_dup_file>false</force_dup_file>\n")
    xml.write("  <group>"+mv_group+"</group>\n")
    xml.write("  <description>"+mv_desc+"</description>\n")
    xml.write("  <load_files>\n")
for model in models:
    date = sdate
    while date <= edate:
        file_date = date.strftime(file_date_format)
        for file_format in file_format_list:
            file_name = file_format.replace("MODEL", model).replace("DATE", file_date)
            link_file_name_prefix = file_name.split(".")[0]
            link_file_name_suffix = file_name.split(".")[1]
            link_file_name = link_file_name_prefix
            link_file_name = link_file_name+"."+link_file_name_suffix
            full_link_file_name = os.path.join(os.getcwd(), tmp_data_dir, link_file_name)
            if os.path.exists(full_link_file_name):
                with open(load_xml_file, 'a') as xml:
                    xml.write("    <file>/base_dir/"+link_file_name+"</file>\n")
        date = date + date_inc
with open(load_xml_file, 'a') as xml:
    xml.write("  </load_files>\n")
    xml.write("\n")
    xml.write("</load_spec>")


### CREATE DATABASE IF NEEDED AND LOAD DATA
# mv_create_db_on_aws.sh agruments:
#    1 - username
#    2 - database name
# mv_load_to_aws.sh agruments:
#    1 - username
#    2 - base dir
#    3 - XML file
#    4 (opt) - sub dir
if new_or_add == "new":
    print("3) Creating database on METviewer AWS using mv_create_db_on_aws.sh")
    subprocess.call([os.path.join(METviewer_AWS_scripts_dir, "mv_create_db_on_aws.sh"), os.environ['USER'].lower(), mv_database])
    print("4) Loading data to METviewer AWS using mv_load_to_aws.sh")
else:
    print("3) Loading data to METviewer AWS using mv_load_to_aws.sh")
subprocess.call([os.path.join(METviewer_AWS_scripts_dir, "mv_load_to_aws.sh"), os.environ['USER'].lower(), tmp_data_dir, load_xml_file])

### CHECK METVIEWER AWS DATABASES
# mv_db_size_on_aws.sh
#    1 - username
if new_or_add == "new":
    print("5) Check METviewer AWS database list using mv_db_size_on_aws.sh")
else:
    print("4) Check METviewer AWS database list using mv_db_size_on_aws.sh")
subprocess.call([os.path.join(METviewer_AWS_scripts_dir, "mv_db_size_on_aws.sh"), os.environ['USER'].lower()])
shutil.rmtree(tmp_data_dir)
