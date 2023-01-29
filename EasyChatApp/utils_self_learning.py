from xlsxwriter import Workbook

import re
import datetime
import sys
import requests
import warnings
import logging
import os
from django.conf import settings


logger = logging.getLogger(__name__)


def write_excel_clusters(cluster_dict, start_date, end_date):
    filename = "files/SelfLearning-Clusters_from_" + start_date + "_to_" + end_date + ".xlsx"
    try:
        test_wb = Workbook(filename)
        sheet1 = test_wb.add_worksheet("Sheet1")
        sheet1.write(0, 0, "Clusters ID")
        sheet1.write(0, 1, "Sentences")
        row = 1
        for key in sorted(cluster_dict.keys()):
            cluster_id = int(key) + 1
            sheet1.write(row, 0, cluster_id)
            sheet1.write(row, 1, "\n".join(cluster_dict[key]))
            row = row + 1
        test_wb.close()
        return filename
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error write_excel %s %s",
                     str(e), str(exc_tb.tb_lineno))
