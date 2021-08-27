import pymongo
import logging, sys, json, requests
from datetime import date, datetime
from pytz import timezone
from dateutil import tz
import os, math
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

DB_USER = os.environ.get("DB_USER")
DB_PWD = os.environ.get("DB_PWD")
DB_IP = os.environ.get("DB_IP")
DB_PORT = os.environ.get("DB_PORT")

fromTimezone = 'US/Eastern'

def convert_time(mytime):
    from_zone = tz.gettz('US/Eastern')
    to_zone = tz.gettz('UTC')

    utc = mytime.replace(tzinfo=from_zone)

    # Convert time zone
    central = utc.astimezone(to_zone)
    # print(central)
    return central

if __name__ == '__main__':
    
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%m/%d/%Y %H:%M:%S")

    try:
        # MONGO_HOST = "localhost" 
        # MONGO_PORT = "27017"
        # MONGO_DB = "pax_events"
        # MONGO_USER = "username"
        # MONGO_PASS = "password"

        # uri = "mongodb://{}:{}@{}:{}/{}?authSource=admin".format(MONGO_USER, MONGO_PASS, MONGO_HOST, MONGO_PORT, MONGO_DB)
        # conn = pymongo.MongoClient(uri)
        # myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        myclient = pymongo.MongoClient(f"mongodb://{DB_USER}:{DB_PWD}@{DB_IP}:{DB_PORT}/pax_events")
        mydb = myclient["pax_events"]
        logging.info("Connected to MongoDB")
    except Exception as e:
        logging.info(f'Error: {e}')
        sys.exit()

    # lines = []
    # with open("test.json") as fp:
    #     lines = fp.readlines()
    #     fp.close()

    # logging.info(len(lines))

    # # raw_data = json.dumps(lines[0].strip())
    # # logging.info(raw_data)
    # # logging.info(type(raw_data))
    # data = json.loads(lines[0].strip())
    # logging.info(data)
    # logging.info(type(data))
    session_requests = requests.Session()

    # result = session_requests.get('https://assets.paxsite.com/online/schedule-export.json?t=' + str(round(time.time())))
    # result = session_requests.get('https://api-melupufoagt.stackpathdns.com/api/schedules?key=b0a264a7-7b5e-4a55-acde-16cb630bfe6d') # PAX EAST Online 2021
    result = session_requests.get('https://api-melupufoagt.stackpathdns.com/api/schedules?key=6f51c8aa-c4cd-4391-900c-ed9e1b1e6ad8') # Pax WEST 2021

    if result.status_code == 200:   
        
        data = json.loads(result.content)

        # convert times for each event and find max and min time, in UTC from EST

        start = datetime.now()
        end = datetime.now()
        locations = []
        date_bounds = []
        start_day = 0
        start_test = datetime.now()
        end_test = datetime.now()

        i = 0

        for event in data["schedules"]:
            if event["location"] not in locations:
                locations.append(event["location"])

            ### conversion to UTC standard time
            # print(f'{event["start_time"]} - { type(event["start_time"])}')
            datetime_start = datetime.strptime(event["start_time"],"%Y-%m-%d %H:%M:%S")
            datetime_end = datetime.strptime(event["end_time"],"%Y-%m-%d %H:%M:%S")
            # print(f"{datetime_start} to {datetime_end} = {(datetime_end - datetime_start).seconds}")
            rowCnt = math.ceil(((datetime_end - datetime_start).seconds / 60)/15)
            event["rowCnt"] = rowCnt
            # print(event["rowCnt"])
            # print(f"Before: {datetime_obj}")
            eastern = timezone("EST")
            # print(eastern)
            datetime_start = datetime_start.replace(tzinfo=eastern)
            datetime_end = datetime_end.replace(tzinfo=eastern)
            # print(f"After: {datetime_obj}")
            start_conversion = convert_time(datetime_start)
            # print(f"1) {event['start_time']}")
            # event["start_time"] = str(start_conversion.isoformat()) + "Z"
            event["start_time"] = start_conversion
            # print(f"2) {event['start_time']}")
            end_conversion = convert_time(datetime_end)
            # event["end_time"] = str(end_conversion.isoformat()) + "Z"
            event["end_time"] = end_conversion
            # print(datetime_start.day)



            ### this is for figuring the start and stop of events each day
            if i == 0:
                start = start_conversion
                end = end_conversion
                start_test = datetime_start
                end_test = datetime_start
                start_day = datetime_start.day
                # print(f"setting start: {start}")
                # print(f"setting end: {end}")
            else:
                if start > start_conversion:
                    start = start_conversion
                if end < end_conversion:
                    end = end_conversion
            if start_day != datetime_start.day:
                date_bounds.append({'start' : start_test, 'end': end_test})
                start_test = datetime_start
                start_day = datetime_start.day
            else:
                end_test = datetime_end


            i += 1
        date_bounds.append({'start' : convert_time(start_test), 'end' : convert_time(end_test)})
        # print(test_obj)
        # sys.exit()
        location_arr = []
        for location in locations:
            location_arr.append({ 'nickname': location, 'location': ''})

        # test_array = {
        #     "Time 1" : [{ 'location 1' : '_id1'}, {'location 2' : '_id2'}, {'location 3', '_id3'}]
        #     "Time 2" : [                          {'location 2' : '_id2'}]
        # }
        # for event in data["schedules"]:
        #     if test_obj.get(event["start"])


        print(date_bounds)
        # print(data["schedules"])
        print(f"Start: {start.isoformat()}")
        print(f"End: {end.isoformat()}")

        # sys.exit()

        # print(events)
        # print(events['event_id'])
        # event_base = 'https://online.paxsite.com/schedule/panel/'
        
        # sys.exit()        
        event_count = 0
        mycol = mydb["shows"]
        ## set show values
        mydict = {
            'show_id' : data["event_id"],
            'event_name' : data["event_name"],
            'event_slug' : data["event_slug"],
            'active': False,
            # 'start_date': str(start.isoformat()) + "Z",
            'start_date': start,
            # 'end_date' : str(end.isoformat()) + "Z",
            'end_date' : end,
            'default_timezone': fromTimezone,
            'locations': location_arr,
            '_events' : [],
            'date_bounds' : date_bounds
            # 'test_obj' : test_obj
        }
        y = mycol.insert_one(mydict)
        # sys.exit()
        logging.info(y.inserted_id)
        
        ## set event values
        mycol = mydb["events"]
        x = mycol.insert_many(data['schedules'])
        logging.info(x.inserted_ids)
        ## update event values with show they below too
        test_obj = {}
        for event in x.inserted_ids:
            mycol.update_one(
                { '_id' : event },
                {
                    '$set' : {
                        '_show' : y.inserted_id,
                    }
                
                })
            item = mycol.find_one({'_id' : event})
            start_conversion = convert_time(item["start_time"])

            if test_obj.get(str(start_conversion)):
                test_obj[str(start_conversion)].append({item["location"] : event})
            else:
                test_obj[str(start_conversion)] = []
                test_obj[str(start_conversion)].append({item["location"] : event})


            
        ## update show value with all event ids
        mycol = mydb["shows"]
        mycol.update_one(
            { '_id' : y.inserted_id },
            {
                '$set' : {
                    '_events' : x.inserted_ids,
                    '_mapping' : test_obj
                }
            }
        )
        
        myclient.close()