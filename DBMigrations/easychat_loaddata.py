import json
import subprocess
import os
from EasyChatApp.models import *
from LiveChatApp.models import *

print("\n\nAbout to start data loading process. Please make sure you are at right directory...\n\n")


def check_no_attribute_conflict(filename, table_names):
    print("\nChecking for attribute conflict in " +
          filename.split("_")[0] + "...\n")
    import json
    from django.apps import apps
    try:
        for table_group in table_names:
            table_datadump_filepath = "DBMigrations/" + \
                filename.split("_")[0] + "_migrations/datadump_" + \
                table_group["name"][0] + ".json"
            table_datadump = open(table_datadump_filepath, "r")
            table_datadump = json.loads(table_datadump.read())
            if not len(table_datadump):
                continue
            table_name = table_group["name"][0].split(".")[1]
            if table_name == "Intent":
                for table in table_datadump:
                    table_name = table["model"].split(".")[1]
                    table_datadump = list(table["fields"].keys())
                    table_objs = apps.get_model(
                        filename.split("_")[0], table_name)
                    for key in table_datadump:
                        if table_objs._meta.get_field(key):
                            continue
            else:
                table_datadump = list(table_datadump[0]["fields"].keys())
                table_objs = apps.get_model(filename.split("_")[0], table_name)
                for key in table_datadump:
                    if table_objs._meta.get_field(key):
                        continue
    except Exception as e:
        print("Getting error: " + str(e))
        return False
    print("\nNo attribute conflict.\n")
    return True


filename_list = ["EasyChatApp_table_meta.json", "LiveChatApp_table_meta.json"]
for filename in filename_list:
    with open(os.path.join("DBMigrations/TableMeta/", filename), 'r') as file:
        table_names = json.loads(file.read())
        file.close()

        # Checking if all table and it's attributes are present in new DB schema

        if not check_no_attribute_conflict(filename, table_names):
            break

        # Loading data of every table to new databse
        total_count = len(table_names)
        count = 0

        for table_group in table_names:
            count += 1
            print("Loading data for table ", table_group["name"])

            # If this table aleardy loaded, then it will be skipped.
            if table_group["status"]:
                print("Data already loaded for this table. Skipping...")
                continue
            try:
                cmd = "python -W ignore manage.py loaddata DBMigrations/" + \
                    filename.split(
                        "_")[0] + "_migrations/datadump_" + table_group["name"][0] + ".json"
                subprocess.run(cmd, shell=True, check=True)
                percentage = (count * 100) / total_count
                print("Progress: " + str(round(percentage, 2)) + "%")

                # Marking it loaded.
                table_group["status"] = True
            except subprocess.CalledProcessError as error:
                print("Something went wrong..." + str(error))
                break
            except Exception as e:
                print("Something went wrong..." + str(e))
                break

        temp_file = open(os.path.join(
            "DBMigrations/TableMeta/", filename), 'w')
        temp_file.write(json.dumps(table_names, indent=4))
        temp_file.close()


print("Data loading process completed")
