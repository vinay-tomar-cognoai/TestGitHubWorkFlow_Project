import json
import subprocess
import os

print("\n\nAbout to start data dumping process. Please make sure you are at right directory...\n\n")

for filename in os.listdir("DBMigrations/TableMeta/"):
    with open(os.path.join("DBMigrations/TableMeta/", filename), 'r') as file:
        table_names = json.loads(file.read())
        file.close()
        if not os.path.exists("./DBMigrations/" + filename.split("_")[0] + "_migrations/"):
            os.makedirs("./DBMigrations/" + filename.split("_")
                        [0] + "_migrations/")

        total_count = len(table_names)
        count = 1
        for table_group in table_names:
            print("Dumping data for table ", table_group["name"])

            try:
                table_group_name = ""
                for table in table_group["name"]:
                    table_group_name += " " + table

                cmd = "python -W ignore manage.py dumpdata " + table_group_name + " --indent 4 > DBMigrations/" + \
                    filename.split(
                        "_")[0] + "_migrations/datadump_" + table_group["name"][0] + ".json"
                subprocess.run(cmd, shell=True, check=True)
                percentage = (count * 100) / total_count
                count += 1
                print("Progress: " + str(round(percentage, 2)) + "%")
            except Exception:
                print("No such table " + table_group["name"][0])
                print("Setting default value...")
                temp_file = open("DBMigrations/" + filename.split(
                    "_")[0] + "_migrations/datadump_" + table_group["name"][0] + ".json", "w")
                temp_file.write("[]")
                temp_file.close()
            table_group["status"] = False

        print(table_names)
        temp_file = open(os.path.join(
            "DBMigrations/TableMeta/", filename), 'w')
        temp_file.write(json.dumps(table_names, indent=4))
        temp_file.close()

print("Data dumping process completed")
