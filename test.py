import requests, re, json, sys, os, time,math
from icalendar import Calendar, Event, vDatetime
from datetime import datetime, timedelta
from dateutil import tz, parser
import pytz

def convert_time(mytime):
    from_zone = tz.gettz('US/Eastern')
    to_zone = tz.gettz('UTC')

    utc = mytime.replace(tzinfo=from_zone)

    # Convert time zone
    central = utc.astimezone(to_zone)
    # print(central)
    return central

g = open('events/PAX-East21_TwitchArena.ics','rb')
gcal = Calendar.from_ical(g.read())
g.close()
for component in gcal.walk():
    if component.name == "VEVENT":
        # print(component.get('summary'))
        dtstart = datetime.strptime(component.get('dtstart').to_ical().decode("utf-8"),"%Y%m%dT%H%M%S")
        dtend = datetime.strptime(component.get('dtend').to_ical().decode("utf-8"),"%Y%m%dT%H%M%S")
        component["dtstart"] = vDatetime(convert_time(dtstart).replace(tzinfo=pytz.UTC))
        component["dtend"] = vDatetime(convert_time(dtend).replace(tzinfo=pytz.UTC))

f = open("events/PAX-East21_TwitchArena.ics","wb")
f.write(gcal.to_ical())
f.close()

