from xlsxwriter import Workbook
import datetime
import re
import sys
import requests
import warnings
import logging
import os
import xlrd
from django.conf import settings

from EasyChatApp.utils import ensure_element_tree

from zipfile import ZipFile

logger = logging.getLogger(__name__)

ensure_element_tree(xlrd)


def write_excel_feedback(general_feedback_queryset):
    filename = "files/GeneralFeedback.xlsx"
    try:
        zip_obj = ZipFile('files/GeneralFeedback.zip', 'w')
        test_wb = Workbook("files/GeneralFeedback.xlsx")
        sheet1 = test_wb.add_worksheet("Sheet1")
        sheet1.write(0, 0, "Sr. No.")
        sheet1.write(0, 1, "UID")
        sheet1.write(0, 2, "Raised By")
        sheet1.write(0, 3, "Description")
        sheet1.write(0, 4, "Category")
        sheet1.write(0, 5, "Priority")
        sheet1.write(0, 6, "Screenshot")
        sheet1.write(0, 7, "Date Added")
        sheet1.write(0, 8, "Status")
        sheet1.write(0, 9, "Remarks")
        row = 1
        for feedback in general_feedback_queryset:
            sheet1.write(row, 0, row)
            sheet1.write(row, 1, feedback.pk)
            sheet1.write(row, 2, feedback.user.name())
            sheet1.write(row, 3, str(feedback))
            sheet1.write(row, 4, feedback.get_category())
            sheet1.write(row, 5, feedback.get_priority())
            if(feedback.screenshot):
                sheet1.write(row, 6, str(feedback.screenshot)
                             [1:].split('/')[1])
                zip_obj.write(str(feedback.screenshot)[1:])

            else:
                sheet1.write(row, 6, "No Screenshot Attached")
            sheet1.write(row, 7, str(feedback.added_datetime.date()))
            sheet1.write(row, 8, feedback.get_status())
            sheet1.write(row, 9, feedback.get_remarks())
            row += 1

        test_wb.close()
        zip_obj.write(filename)
        zip_obj.close()
        return filename
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error write_excel %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def write_excel_feedbacks(feedback, pk):
    filename = "files/GeneralFeedbackUpdated.xlsx"
    try:
        zip_obj = ZipFile('files/GeneralFeedback.zip', 'r')
        zip_obj_wrtie = ZipFile('files/GeneralFeedbackUpdated.zip', 'w')
        test_wb = Workbook("files/GeneralFeedbackUpdated.xlsx")
        read_wb = xlrd.open_workbook("files/GeneralFeedback.xlsx")
        sheet1 = test_wb.add_worksheet("Sheet1")
        read_sheet = read_wb.sheet_by_name("Sheet1")
        nrows = read_sheet.nrows
        sheet1.write(0, 0, "Sr. No.")
        sheet1.write(0, 1, "UID")
        sheet1.write(0, 2, "Raised By")
        sheet1.write(0, 3, "Description")
        sheet1.write(0, 4, "Category")
        sheet1.write(0, 5, "Priority")
        sheet1.write(0, 6, "Screenshot")
        sheet1.write(0, 7, "Date Added")
        sheet1.write(0, 8, "Status")
        sheet1.write(0, 9, "Remarks")
        row = 1
        for row in range(1, nrows):
            if int(read_sheet.cell_value(row, 1) == int(pk)):
                sheet1.write(row, 0, row)
                sheet1.write(row, 1, feedback.pk)
                sheet1.write(row, 2, feedback.user.name())
                sheet1.write(row, 3, str(feedback))
                sheet1.write(row, 4, feedback.get_category())
                sheet1.write(row, 5, feedback.get_priority())
                if(feedback.screenshot):
                    sheet1.write(row, 6, str(feedback.screenshot)
                                 [1:].split('/')[1])
                    zip_obj_wrtie.write(str(feedback.screenshot)[1:])

                else:
                    sheet1.write(row, 6, "No Screenshot Attached")
                sheet1.write(row, 7, str(feedback.added_datetime.date()))
                sheet1.write(row, 8, feedback.get_status())
                sheet1.write(row, 9, feedback.get_remarks())
            else:
                sheet1.write(row, 0, row)
                sheet1.write(row, 1, read_sheet.cell_value(row, 1))
                sheet1.write(row, 2, read_sheet.cell_value(row, 2))
                sheet1.write(row, 3, read_sheet.cell_value(row, 3))
                sheet1.write(row, 4, read_sheet.cell_value(row, 4))
                sheet1.write(row, 5, read_sheet.cell_value(row, 5))
                sheet1.write(row, 6, read_sheet.cell_value(row, 6))
                sheet1.write(row, 7, read_sheet.cell_value(row, 7))
                sheet1.write(row, 8, read_sheet.cell_value(row, 8))
                sheet1.write(row, 9, read_sheet.cell_value(row, 9))
            row += 1

        test_wb.close()
        for item in zip_obj.infolist():
            # buffer = zip_obj.read(item.filename)
            if (item.filename[-5:] != '.xlsx'):
                # zip_obj_wrtie.write(item)
                zip_obj_wrtie.write(item.filename)

        zip_obj_wrtie.write(filename)
        zip_obj.close()
        zip_obj_wrtie.close()
        cmd = "rm files/GeneralFeedback.zip"
        os.system(cmd)
        os.rename('files/GeneralFeedbackUpdated.zip',
                  'files/GeneralFeedback.zip')
        return filename
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error write_excel %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
