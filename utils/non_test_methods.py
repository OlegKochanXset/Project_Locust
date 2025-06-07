import csv, random
from datetime import datetime, timedelta
from urllib.parse import unquote_plus

def open_csv_field(filepath=str):
    with open(filepath, 'r') as file:
        reader = csv.DictReader(file)
        return list(reader)

def generationFligthsDates():
    dates_list = {}

    dates_list["depart_Date"] = unquote_plus((datetime.now() + timedelta(days=random.randrange(1,5))).strftime("%m/%d/%Y"))
    dates_list["arrive_Date"] = unquote_plus((datetime.now() + timedelta(days=random.randrange(10, 20))).strftime("%m/%d/%Y"))

    return dates_list



