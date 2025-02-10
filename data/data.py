import datetime
import os.path
import uuid
import json

from .wmisdb import WMISDB, DBError
from dotenv import load_dotenv
import os

load_dotenv()

class Data:
    meters = []
    meter_readings = []
    phantom_flows = False
    phantom_flows_30 = False
    comm_issue = False
    disconnected = False

    def __init__(self):
        pass


    def ami_meter_reads(self, meter_id:str) -> [dict]:
        lst = []
        try:
            wmisdb = WMISDB()
            conn = wmisdb.connection
            cursor = conn.cursor()
            cmd = f"exec sp_ami_phantom_flows '{meter_id}'"
            cursor.execute(cmd)
            rows = cursor.fetchall()
            if len(rows) > 0:
                for row in rows:
                    if isinstance(row[1], datetime.datetime):
                        prev_date = row[1].date()
                    else:
                        prev_date = ''
                    if isinstance(row[3], datetime.datetime):
                        curr_date = row[3].date()
                    else:
                        curr_date = ''

                    if isinstance(row[2], float):
                        prev_reading = round(row[2],4)
                    else:
                        prev_reading = ''

                    if isinstance(row[4], float):
                        curr_reading = round(row[4],4)
                    else:
                        curr_reading = ''

                    item = {
                        "meter_id": row[0],
                        "prev_date": prev_date,
                        "prev_reading": prev_reading,
                        "curr_date": curr_date,
                        "curr_reading": curr_reading,
                        "delta": row[5],
                        "calculated": row[6].strip(),
                        "phantom": row[7].strip(),
                    }
                    lst.append(item)
            wmisdb = None
        except DBError as err:
            print(f'DB Error:{err}')
        except Exception as err:
            print(f'Unexpected Error:{err}')

        self.meter_readings = lst

        # determine if phantom flows are present
        self.phantom_flows = False
        self.phantom_flows_30 = False
        for item in lst:
            if item['phantom'] > '':
                self.phantom_flows = True
                break

        today = datetime.date.today()
        early_date = today - datetime.timedelta(days=30)
        # determine if phantom flows are present in the last 30 days.
        for item in lst:
            if item['phantom'] > '':
                if item['curr_date'] > early_date:
                    self.phantom_flows_30 = True
                    break

        # determine if there is a communication issue, defined as any three consecutive days with calculated readings during the last 30 days.
        self.comm_issue = False
        days = 0
        for item in lst:

            if item['curr_date'] > early_date:  
                if item['calculated'] > '':
                    days += 1
                else:
                    days = 0
                if days >= 3:
                    self.comm_issue = True
                    break

        # determine if there meter is disconnected, defined as any 15 consecutive days with calculated readings during the last 30 days.
        self.disconnected = False
        days = 0
        for item in lst:
            if item['curr_date'] > early_date:
                if item['calculated'] > '':
                    days += 1
                else:
                    days = 0
                if days >= 15:
                    self.disconnected = True
                    break

        return

    def ami_meter_list(self) -> [dict]:
        lst = []
        try:
            wmisdb = WMISDB()
            conn = wmisdb.connection
            cursor = conn.cursor()
            cmd = f"exec sp_ami_meter_list"
            cursor.execute(cmd)
            rows = cursor.fetchall()
            if len(rows) > 0:
                for row in rows:
                    item = {
                        "meter_id": row[0],
                    }
                    lst.append(item)
            wmisdb = None
        except DBError as err:
            print(f'DB Error:{err}')
        except Exception as err:
            print(f'Unexpected Error:{err}')
        self.meters = lst
        return

