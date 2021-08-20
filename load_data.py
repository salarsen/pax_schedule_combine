import pymongo
import logging, sys, json, requests
from datetime import date, datetime
from pytz import timezone
from dateutil import tz

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
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
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
    result = session_requests.get('https://api-melupufoagt.stackpathdns.com/api/schedules?key=b0a264a7-7b5e-4a55-acde-16cb630bfe6d')

    if result.status_code == 200:   
        
        data = json.loads(result.content)

        # convert times for each event and find max and min time, in UTC from EST

        start = datetime.now()
        end = datetime.now()

        i = 0
        for event in data["schedules"]:
            # print(f'{event["start_time"]} - { type(event["start_time"])}')
            datetime_start = datetime.strptime(event["start_time"],"%Y-%m-%d %H:%M:%S")
            datetime_end = datetime.strptime(event["end_time"],"%Y-%m-%d %H:%M:%S")
            # print(f"Before: {datetime_obj}")
            eastern = timezone("EST")
            # print(eastern)
            datetime_start = datetime_start.replace(tzinfo=eastern)
            datetime_end = datetime_end.replace(tzinfo=eastern)
            # print(f"After: {datetime_obj}")
            start_conversion = convert_time(datetime_start)
            print(f"1) {event['start_time']}")
            event["start_time"] = str(start_conversion.isoformat()) + "Z" 
            print(f"2) {event['start_time']}")
            end_conversion = convert_time(datetime_end)
            event["end_time"] = str(end_conversion.isoformat()) + "Z"
            if i == 0:
                start = start_conversion
                end = end_conversion
                print(f"setting start: {start}")
                print(f"setting end: {end}")
            else:
                if start > start_conversion:
                    start = start_conversion
                if end < end_conversion:
                    end = end_conversion
            i += 1
        
        print(data["schedules"])
        print(f"Start: {start.isoformat()}")
        print(f"End: {end.isoformat()}")



        # print(events)
        # print(events['event_id'])
        # event_base = 'https://online.paxsite.com/schedule/panel/'
        
        # sys.exit()        
        event_count = 0
        mycol = mydb["shows"]

        ## set show values
        mydict = { 'show_id' : data["event_id"], 'event_name' : data["event_name"], 'event_slug' : data["event_slug"], 'active': False, 'start_date': str(start.isoformat()) + "Z", 'end_date' : str(end.isoformat()) + "Z", 'event_ids' : []}
        y = mycol.insert_one(mydict)

        logging.info(y.inserted_id)
        
        ## set event values
        mycol = mydb["events"]
        x = mycol.insert_many(data['schedules'])
        logging.info(x.inserted_ids)
        ## update event values with show they below too
        for event in x.inserted_ids:
            mycol.update_one(
                { '_id' : event },
                {
                    '$set' : {
                        'show_id' : y.inserted_id,
                    }
                
                })

            
        ## update show value with all event ids
        mycol = mydb["shows"]
        mycol.update_one(
            { '_id' : y.inserted_id },
            {
                '$set' : {
                    'event_ids' : x.inserted_ids,
                }
            }
        )
        
        myclient.close()