import pymongo
import logging, sys, json, requests

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
        mycol = mydb["events"]
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
        # print(events)
        # print(events['event_id'])
        # event_base = 'https://online.paxsite.com/schedule/panel/'
        
        # sys.exit()        
        event_count = 0
        x = mycol.insert_many(data['schedules'])
        logging.info(x.inserted_ids)
        for event in x.inserted_ids:
            mycol.update_one(
                { '_id' : event },
                {
                    '$set' : {
                        'event_name' : "PAX East Online 2021",
                        'event_id' : '18792'
                    }
                
                })
        # for event in data['schedules']:
        #     print(event)

        #     coll.insert_one(event)
        
        myclient.close()