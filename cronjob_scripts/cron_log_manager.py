from django.conf import settings
from datetime import datetime, timedelta
import sqlite3
import os
import sys

LOG_FOLDER = os.path.join(settings.BASE_DIR, 'log/cron/')
CRON_DB_FILE = LOG_FOLDER + "cognoai_cron_log.sqlite"
CRON_ERROR_FILE = LOG_FOLDER + "cron_error.log"

CRON_LOG_TABLE = """
CREATE TABLE IF NOT EXISTS CRON_LOG (
    id INTEGER PRIMARY KEY,
    file_name TEXT NOT NULL,
    start_time timestamp DEFAULT (datetime('now','localtime')),
    end_time timestamp DEFAULT NULL
);
"""

CRON_EMAIL_REPORT = """
CREATE TABLE IF NOT EXISTS CRON_EMAIL_REPORT (
    id INTEGER PRIMARY KEY,
    file_name TEXT NOT NULL,
    sent_time timestamp DEFAULT (datetime('now','localtime'))
);
"""


class CronLogManager():
    def __init__(self):
        self._connection = sqlite3.connect(CRON_DB_FILE, detect_types=sqlite3.PARSE_DECLTYPES)
        self._connection.row_factory = sqlite3.Row
        self.create_schema()
        self.delete_past_cron_logs()

    def __del__(self):
        try:
            self._connection.close()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            log_cron_error("Destructor", e, exc_tb.tb_lineno)

    def get_cursor(self):
        try:
            return self._connection.cursor()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            log_cron_error("get_cursor", e, exc_tb.tb_lineno)

    def create_schema(self):
        try:
            cursor = self.get_cursor()
            cursor.execute(CRON_LOG_TABLE)
            cursor.execute(CRON_EMAIL_REPORT)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            log_cron_error("create_schema", e, exc_tb.tb_lineno)

    def get_email_sent_time(self, file_name):  # Returns datetime object
        try:
            cursor = self.get_cursor()
            email_sent_query = """
            SELECT sent_time FROM CRON_EMAIL_REPORT 
            WHERE file_name = ?
            ORDER BY sent_time DESC LIMIT 1;
            """

            cursor.execute(email_sent_query, (file_name,))
            record_obj = cursor.fetchone()

            if record_obj is None:
                return None

            sent_time = record_obj["sent_time"]
            return sent_time
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            log_cron_error("get_email_sent_time", e, exc_tb.tb_lineno)
            return None

    def get_file_run_time_map(self):
        try:
            records = self.get_cron_log()

            file_run_time_map = {
                record["file_name"]: convert_str_to_datetime(record["start_time"])
                for record in records
            }
            return file_run_time_map
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            log_cron_error("get_file_run_time_map", e, exc_tb.tb_lineno)
            return dict()

    def get_cron_log(self):
        try:
            cursor = self.get_cursor()

            cron_log_query = """
            SELECT file_name, MAX(start_time) AS start_time FROM CRON_LOG 
            GROUP BY file_name;
            """

            cursor.execute(cron_log_query)
            records = cursor.fetchall()
            return records
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            log_cron_error("get_cron_log", e, exc_tb.tb_lineno)
            return []

    def get_prev_record(self, file_name):  # Return dictionary object
        try:
            cursor = self.get_cursor()
            cron_log_query = """
            SELECT * FROM CRON_LOG 
            WHERE file_name = ?
            ORDER BY start_time DESC LIMIT 1;
            """

            cursor.execute(cron_log_query, (file_name,))
            record = cursor.fetchone()
            return record
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            log_cron_error("get_prev_record", e, exc_tb.tb_lineno)
            return None

    def create_start_cron_log(self, file_name):  # Return integer (primary key)
        try:
            cursor = self.get_cursor()
            cron_log_query = """
            INSERT INTO CRON_LOG (file_name) VALUES(?);
            """

            cursor.execute(cron_log_query, (file_name, ))
            self._connection.commit()

            return cursor.lastrowid
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            log_cron_error("create_start_cron_log", e, exc_tb.tb_lineno)

    def create_end_cron_log(self, log_obj_id):
        try:
            cursor = self.get_cursor()
            end_time = datetime.now()

            cron_log_query = """
            UPDATE CRON_LOG 
            SET end_time=?
            WHERE id=?;
            """

            cursor.execute(cron_log_query, (end_time, log_obj_id))
            self._connection.commit()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            log_cron_error("create_end_cron_log", e, exc_tb.tb_lineno)

    def create_email_sent_log(self, file_name):
        try:
            cursor = self.get_cursor()
            email_sent_query = """
            INSERT INTO CRON_EMAIL_REPORT (file_name) VALUES(?);
            """

            cursor.execute(email_sent_query, (file_name,))
            self._connection.commit()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            log_cron_error("create_email_sent_log", e, exc_tb.tb_lineno)

    def delete_past_cron_logs(self):
        try:
            current_time = datetime.now()
            if current_time.hour != 1:
                return

            if not (current_time.minute >= 1 and current_time.minute <= 5):
                return

            delete_log_query = """
            DELETE FROM CRON_LOG 
            WHERE start_time <= ?;
            """

            time_stamp = datetime.now() - timedelta(days=10)
            cursor = self.get_cursor()
            cursor.execute(delete_log_query, (time_stamp,))
            self._connection.commit()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            log_cron_error("delete_past_cron_logs", e, exc_tb.tb_lineno)


def convert_str_to_datetime(date_str):
    try:
        date_format = "%Y-%m-%d %H:%M:%S"
        datetime_obj = datetime.strptime(date_str, date_format)
        return datetime_obj
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        log_cron_error("convert_str_to_datetime", e, exc_tb.tb_lineno)
        return date_str


def log_cron_error(function_name, error, line_no):
    try:
        current_time = datetime.now()
        error_message = "[{}] Error cron_log_manager - {}: {} at {}\n".format(
            str(current_time), function_name, str(error), str(line_no))

        with open(CRON_ERROR_FILE, 'a') as file:
            file.write(error_message)
    except Exception as e:
        print(e)
