import requests, re, json, sys, os, time,math
from lxml import html
from bs4 import BeautifulSoup
from icalendar import Calendar, Event, vDatetime
from datetime import datetime, timedelta
from dateutil import tz

# setup calendar. X-WR-CALNAME will set calendar name in outlook and such
def setup_cal(pax_val):   
    newCal = Calendar()
    newCal["X-WR-CALNAME"] = pax_val
    newCal["PRODID"]="-//PAX Online//Pax Online 2020//EN"
    newCal["VERSION"]="2.0"
    newCal["CALSCALE"]="GREGORIAN"
    newCal["METHOD"]="PUBLISH"

    return newCal

def convert_time(mytime):
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('PST')

    utc = mytime.replace(tzinfo=from_zone)

    # Convert time zone
    central = utc.astimezone(to_zone)
    print(central)

# parse events
def parse_event(event_str, pax_cal, new_desc):
    cal = Calendar.from_ical(event_str)
  
    # walk the vents
    for component in cal.walk("VEVENT"):
        # new event to append to master schedule
        event = Event()

        # pull start and end date
        dstartFix = component.decoded('DTSTART')
        dendFix = component.decoded('DTEND')

        ## print PST converted timezones to verify if they cross midnight threshold
        # convert_time(dstartFix)
        # convert_time(dendFix)

        # if end date is less that start date, means we are straddling a midnight PST transition, add 1 day to end date to correct
        if dendFix < dstartFix:
            event["DTSTART"] = vDatetime(dstartFix)
            event["DTEND"] = vDatetime(dendFix + timedelta(days=1))
        else:
            event["DTSTART"] = component.get('DTSTART')
            event["DTEND"] = component.get('DTEND')

        for k,v in component.items():
            if k == 'DESCRIPTION':
                event[k] = new_desc
            elif k == "DTSTART":
                continue
            elif k == "DTEND":
                continue
            else:
                event[k] = v
        
        pax_cal.add_component(event)

if __name__ == "__main__":

    pax1_sch = setup_cal("PAX")
    pax2_sch = setup_cal("PAX2")
    pax3_sch = setup_cal("PAX3")
    paxArena_sch = setup_cal("PAX Arena")
    pax_tourny_sch = setup_cal("PAX Tournaments and Games")

    session_requests = requests.Session()

    result = session_requests.get('https://assets.paxsite.com/online/schedule-export.json?t=' + str(round(time.time())))

    if result.status_code == 200:
        events = json.loads(result.content)
        
        event_base = 'https://online.paxsite.com/schedule/panel/'
        
        event_count = 0
        for event in events["events"]:
            # print event we are on to console
            print(event["title"],flush=True)

            event_result = session_requests.get(event_base + event["urlTitle"])
            if event_result.status_code == 200:
                pax1 = False
                pax2 = False
                pax3 = False
                paxA = False
                paxTourney = False

                # turn result into soup for processing
                soup = BeautifulSoup(event_result.content, 'lxml')

                channel_search = soup.find('li',attrs={'class':'channel'})
                calendar_search = soup.find('li',attrs={'class':'cal'})
                ext_desc_search = soup.find('section',attrs={'class':'copy'})

                event_desc = ''

                # check for twitch channel for event and set event schedule type
                if channel_search:
                    channel_url = channel_search.a.get('href')
                    if "PAXArena" in channel_url:
                        paxA = True
                        event_desc = event_desc + channel_url + "\n\n"
                    elif "PAX2" in channel_url:
                        pax2 = True
                        event_desc = event_desc + channel_url + "\n\n"
                    elif "PAX3" in channel_url:
                        pax3 = True
                        event_desc = event_desc + channel_url + "\n\n"
                    elif "PAX" in channel_url and not "PAX2" in channel_url and not "PAX3" in channel_url and not "PAXArena" in channel_url:
                        pax1 = True
                        event_desc = event_desc + channel_url + "\n\n"
                else:
                    paxTourney = True

                # pull detail page description and append to current details
                # update discord link to point at discord server instead of paxsite since it's assumed they have the discord link already to get these files so allows a quick link back
                if ext_desc_search:
                    for child in ext_desc_search.findChildren():
                        if not child.findChildren():
                            if child.name == 'p':
                                event_desc = event_desc + child.text + "\n\n"
                            elif child.name == 'a':
                                if child.get("href"):
                                    event_desc = event_desc + child.text + "\n"
                                    if "https://online.paxsite.com/features/discord" in child.get("href"):
                                        event_desc = event_desc + "https://discord.gg/paxonline"
                                    else:
                                        event_desc = event_desc + child.get('href')

                #reference ical_base = 'https://online.paxsite.com/schedule/ical/'

                # fetch ics file for event and process it
                ics_result = session_requests.get(calendar_search.a.get('href'))
                if ics_result.status_code == 200:
                    if pax1:
                        parse_event(ics_result.content, pax1_sch, event_desc)
                    elif pax2:
                        parse_event(ics_result.content, pax2_sch, event_desc)
                    elif pax3:
                        parse_event(ics_result.content, pax3_sch, event_desc)
                    elif paxA:
                        parse_event(ics_result.content, paxArena_sch, event_desc)
                    elif paxTourney:
                        parse_event(ics_result.content, pax_tourny_sch, event_desc)
            event_count = event_count + 1
        
        #interesting tidbits
        print('Total events: {}'.format(event_count))

        #export ics files
        f = open("events/pax_v2.ics","wb")
        f.write(pax1_sch.to_ical())
        f.close()

        
        f = open("events/pax2_v2.ics","wb")
        f.write(pax2_sch.to_ical())
        f.close()

        
        f = open("events/pax3_v2.ics","wb")
        f.write(pax3_sch.to_ical())
        f.close()

        
        f = open("events/paxArena_v2.ics","wb")
        f.write(paxArena_sch.to_ical())
        f.close()

        
        f = open("events/paxTournaments-Games_v3.ics","wb")
        f.write(pax_tourny_sch.to_ical())
        f.close()