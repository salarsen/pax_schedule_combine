import requests, re, json, sys, os, time,math
from icalendar import Calendar, Event, vDatetime
from datetime import datetime, timedelta
from dateutil import tz, parser
import pytz

# setup calendar. X-WR-CALNAME will set calendar name in outlook and such
def setup_cal(pax_val):   
    newCal = Calendar()
    newCal["X-WR-CALNAME"] = pax_val
    newCal["PRODID"]="-//PAX Online//PAX East Online 2021//EN"
    newCal["VERSION"]="2.0"
    newCal["CALSCALE"]="GREGORIAN"
    newCal["METHOD"]="PUBLISH"

    return newCal

def convert_time(mytime):
    from_zone = tz.gettz('US/Eastern')
    to_zone = tz.gettz('UTC')

    utc = mytime.replace(tzinfo=from_zone)

    # Convert time zone
    central = utc.astimezone(to_zone)
    # print(central)
    return central

# # parse events
def parse_event(data, pax_cal, new_desc):
    # cal = Calendar.from_ical(event_str)

        # new event to append to master schedule
    event = Event()
    print(event)

    # pull start and end date

    dstartFix = parser.parse(data["start_time"])
    dendFix = parser.parse(data["end_time"])

    print(dstartFix)
    # print(dstartFix.year)
    test = datetime(dstartFix.year, dstartFix.month, dstartFix.day, dstartFix.hour, dstartFix.minute, dstartFix.second).replace(tzinfo=pytz.timezone("US/Eastern"))
    print(test)
    print(convert_time(test))
    print(vDatetime(test).to_ical())
    print(vDatetime(convert_time(test).replace(tzinfo=pytz.UTC)).to_ical())
    

    # sys.exit()

    ## print PST converted timezones to verify if they cross midnight threshold
    # convert_time(dstartFix)
    # convert_time(dendFix)

    # if end date is less that start date, means we are straddling a midnight PST transition, add 1 day to end date to correct
    if dendFix < dstartFix:
        dendFix = dendFix + timedelta(days=1)
    event.add('uid',data['id'])
    event_start = datetime(dstartFix.year, dstartFix.month, dstartFix.day, dstartFix.hour, dstartFix.minute, dstartFix.second, tzinfo=pytz.timezone('US/Eastern'))
    event_end = datetime(dendFix.year, dendFix.month, dendFix.day, dendFix.hour, dendFix.minute, dendFix.second, tzinfo=pytz.timezone('US/Eastern'))
    event.add('DTSTART', vDatetime(convert_time(event_start).replace(tzinfo=pytz.UTC)))
    event.add('DTEND',vDatetime(convert_time(event_end).replace(tzinfo=pytz.UTC)))
    event.add('summary', re.sub('\&amp\;','&',data["title"]))
    event.add('description', re.sub('\&amp\;','&',new_desc))
    event.add('location', "https://" + data['location'])

    # print(event)
    pax_cal.add_component(event)

if __name__ == "__main__":

    pax1_sch = setup_cal("twitch.tv-PAX")
    pax2_sch = setup_cal("twitch.tv-PAX2")
    pax3_sch = setup_cal("twitch.tv-PAX3")
    # paxArena_sch = setup_cal("twitch.tv-PAXArena")
    # pax_tourny_sch = setup_cal("PAX Tournaments and Games")

    session_requests = requests.Session()

    # result = session_requests.get('https://assets.paxsite.com/online/schedule-export.json?t=' + str(round(time.time())))
    result = session_requests.get('https://api-melupufoagt.stackpathdns.com/api/schedules?key=b0a264a7-7b5e-4a55-acde-16cb630bfe6d')

    if result.status_code == 200:
        
        events = json.loads(result.content)
        # print(events)
        # print(events['event_id'])
        # event_base = 'https://online.paxsite.com/schedule/panel/'
        
        
        event_count = 0
        for event in events['schedules']:
            print(event)
            # print event we are on to console
            print(event["title"],flush=True)
            test_str = re.sub('[^\w]+$','',re.sub('[^\w]+','-',event["title"]))
            print(test_str, flush=True)

            pax1 = False
            pax2 = False
            pax3 = False
            paxA = False
            paxTourney = False

            channel_url = ''
            channel_url = event["location"]

            event_desc = ''

            if event["location"] == "twitch.tv/pax3":
                pax3 = True
                event_desc = event["description"] + "\nhttps://" + channel_url + "\n\n"
            elif event["location"] == "twitch.tv/pax2":
                pax2 = True
                event_desc = event["description"] + "\nhttps://" + channel_url + "\n\n"
            
            elif event["location"] == "twitch.tv/pax":
                pax1 = True
                event_desc = event["description"] + "\nhttps://" + channel_url + "\n\n"

            # elif event["location"] == "twitch.tv/paxarena":
            #     paxA = True
            #     event_desc = event["description"] + "\nhttps://" + channel_url + "\n\n"

            if event['tags'] == "Recorded":
                event_desc = event_desc + "!Pre-Recorded!"
            elif event['tags'] == "Live":
                event_desc = event_desc + "!Live Stream!"

            # event_base = f'https://online.paxsite.com/content/sitebuilder/rna/pax/online/en-us/panels/panel-information.html?gtID={event["event_id"]}&panel-name={test_str}'
            # print(event_base,flush=True)

            # event_result = session_requests.get(event_base + event["urlTitle"])

            # if event_result.status_code == 200:
            #     pax1 = False
            #     pax2 = False
            #     pax3 = False
            #     paxA = False
            #     paxTourney = False

            #     # turn result into soup for processing
            #     soup = BeautifulSoup(event_result.content, 'lxml')

            #     channel_search = soup.find('li',attrs={'class':'channel'})
            #     calendar_search = soup.find('li',attrs={'class':'cal'})
            #     ext_desc_search = soup.find('section',attrs={'class':'copy'})

            #     event_desc = ''

            #     # check for twitch channel for event and set event schedule type
            #     if channel_search:
            #         channel_url = channel_search.a.get('href')
            #         if "PAXArena" in channel_url:
            #             paxA = True
            #             event_desc = event_desc + channel_url + "\n\n"
            #         elif "PAX2" in channel_url:
            #             pax2 = True
            #             event_desc = event_desc + channel_url + "\n\n"
            #         elif "PAX3" in channel_url:
            #             pax3 = True
            #             event_desc = event_desc + channel_url + "\n\n"
            #         elif "PAX" in channel_url and not "PAX2" in channel_url and not "PAX3" in channel_url and not "PAXArena" in channel_url:
            #             pax1 = True
            #             event_desc = event_desc + channel_url + "\n\n"
            #     else:
            #         paxTourney = True

            #     # pull detail page description and append to current details
            #     # update discord link to point at discord server instead of paxsite since it's assumed they have the discord link already to get these files so allows a quick link back
            #     if ext_desc_search:
            #         for child in ext_desc_search.findChildren():
            #             if not child.findChildren():
            #                 if child.name == 'p':
            #                     event_desc = event_desc + child.text + "\n\n"
            #                 elif child.name == 'a':
            #                     if child.get("href"):
            #                         event_desc = event_desc + child.text + "\n"
            #                         if "https://online.paxsite.com/features/discord" in child.get("href"):
            #                             event_desc = event_desc + "https://discord.gg/paxonline"
            #                         else:
            #                             event_desc = event_desc + child.get('href')

            #     #reference ical_base = 'https://online.paxsite.com/schedule/ical/'

            if pax1:
                parse_event(event, pax1_sch, event_desc)
            elif pax2:
                parse_event(event, pax2_sch, event_desc)
            elif pax3:
                parse_event(event, pax3_sch, event_desc)
            # elif paxA:
            #     parse_event(event, paxArena_sch, event_desc)

            #     # fetch ics file for event and process it
            #     ics_result = session_requests.get(calendar_search.a.get('href'))
            #     if ics_result.status_code == 200:
            #         if pax1:
            #             parse_event(ics_result.content, pax1_sch, event_desc)
            #         elif pax2:
            #             parse_event(ics_result.content, pax2_sch, event_desc)
            #         elif pax3:
            #             parse_event(ics_result.content, pax3_sch, event_desc)
            #         elif paxA:
            #             parse_event(ics_result.content, paxArena_sch, event_desc)
            #         elif paxTourney:
            #             parse_event(ics_result.content, pax_tourny_sch, event_desc)
            event_count = event_count + 1
            # sys.exit()
        
        # #interesting tidbits
        print('Total events: {}'.format(event_count))

        #export ics files
        f = open("events/PAX-East21_HorseTheatre.ics","wb")
        f.write(pax1_sch.to_ical())
        f.close()

        
        f = open("events/PAX-East21_UnicornTheatre.ics","wb")
        f.write(pax2_sch.to_ical())
        f.close()

        
        f = open("events/PAX-East21_GooseTheatre.ics","wb")
        f.write(pax3_sch.to_ical())
        f.close()

        
        # f = open("events/PAX-East21_TwitchArena.ics","wb")
        # f.write(paxArena_sch.to_ical())
        # f.close()

        
        # f = open("events/paxTournaments-Games_v3.ics","wb")
        # f.write(pax_tourny_sch.to_ical())
        # f.close()