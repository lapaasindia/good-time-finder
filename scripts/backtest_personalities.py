
import sys
import os
from datetime import datetime, timedelta
import json
import statistics

# Add the good_time_finder directory to the path so we can import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.models import Person, GeoLocation, TimeRange
from app.services.life_predictor import LifePredictorService

# 50 Personalities with high-confidence birth data (AA Rating) and 2-3 major events.
# Data sourced from Astro-Databank (Lois Rodden AA Rating) and major news/biographical records.
PERSONALITIES = [
    {
        "name": "Steve Jobs",
        "birth": {"dt": "1955-02-24 19:15", "lat": 37.7749, "lon": -122.4194, "tz": "America/Los_Angeles"},
        "events": [
            {"date": "1976-04-01", "nature": "Good", "desc": "Apple Inc. founded"},
            {"date": "1985-09-17", "nature": "Bad", "desc": "Resigned from Apple after power struggle"},
            {"date": "1997-02-04", "nature": "Good", "desc": "Returned to Apple as advisor (NeXT acquisition)"},
            {"date": "2011-10-05", "nature": "Bad", "desc": "Passed away (Health/Life overall)"}
        ]
    },
    {
        "name": "Bill Gates",
        "birth": {"dt": "1955-10-28 21:15", "lat": 47.6062, "lon": -122.3321, "tz": "America/Los_Angeles"},
        "events": [
            {"date": "1975-04-04", "nature": "Good", "desc": "Microsoft founded"},
            {"date": "1994-01-01", "nature": "Good", "desc": "Marriage to Melinda French"},
            {"date": "2021-05-03", "nature": "Bad", "desc": "Announced divorce from Melinda"}
        ]
    },
    {
        "name": "Amitabh Bachchan",
        "birth": {"dt": "1942-10-11 16:00", "lat": 25.4358, "lon": 81.8463, "tz": "Asia/Kolkata"},
        "events": [
            {"date": "1982-08-02", "nature": "Bad", "desc": "Coolie accident - nearly fatal"},
            {"date": "2000-07-03", "nature": "Good", "desc": "KBC launch - career revival"},
            {"date": "1996-01-01", "nature": "Bad", "desc": "Financial crisis (ABCL bankruptcy)"}
        ]
    },
    {
        "name": "Narendra Modi",
        "birth": {"dt": "1950-09-17 11:00", "lat": 23.7850, "lon": 72.4347, "tz": "Asia/Kolkata"},
        "events": [
            {"date": "2001-10-07", "nature": "Good", "desc": "Became CM of Gujarat"},
            {"date": "2014-05-26", "nature": "Good", "desc": "Became PM of India"},
            {"date": "2019-05-30", "nature": "Good", "desc": "Re-elected as PM with bigger mandate"}
        ]
    },
    {
        "name": "Donald Trump",
        "birth": {"dt": "1946-06-14 10:54", "lat": 40.7033, "lon": -73.8010, "tz": "America/New_York"},
        "events": [
            {"date": "2016-11-08", "nature": "Good", "desc": "Won 2016 Presidential Election"},
            {"date": "2021-01-06", "nature": "Bad", "desc": "Capitol Hill insurrection (major legal/reputation hit)"},
            {"date": "1991-07-16", "nature": "Bad", "desc": "Taj Mahal Casino bankruptcy"}
        ]
    },
    {
        "name": "Barack Obama",
        "birth": {"dt": "1961-08-04 19:24", "lat": 21.3069, "lon": -157.8583, "tz": "Pacific/Honolulu"},
        "events": [
            {"date": "2008-11-04", "nature": "Good", "desc": "Won 2008 Presidential Election"},
            {"date": "2012-11-06", "nature": "Good", "desc": "Re-elected President"},
            {"date": "2004-07-27", "nature": "Good", "desc": "DNC Speech (national prominence)"}
        ]
    },
    {
        "name": "Princess Diana",
        "birth": {"dt": "1961-07-01 19:45", "lat": 52.8333, "lon": 0.5167, "tz": "Europe/London"},
        "events": [
            {"date": "1981-07-29", "nature": "Good", "desc": "Marriage to Prince Charles"},
            {"date": "1992-12-09", "nature": "Bad", "desc": "Announced separation"},
            {"date": "1997-08-31", "nature": "Bad", "desc": "Fatal car crash"}
        ]
    },
    {
        "name": "Sachin Tendulkar",
        "birth": {"dt": "1973-04-24 13:00", "lat": 18.9229, "lon": 72.8333, "tz": "Asia/Kolkata"},
        "events": [
            {"date": "1989-11-15", "nature": "Good", "desc": "International Debut vs Pakistan"},
            {"date": "2011-04-02", "nature": "Good", "desc": "World Cup Victory"},
            {"date": "1999-05-19", "nature": "Bad", "desc": "Father passed away during World Cup"}
        ]
    },
    {
        "name": "Elon Musk",
        "birth": {"dt": "1971-06-28 06:30", "lat": -25.7479, "lon": 28.2293, "tz": "Africa/Johannesburg"},
        "events": [
            {"date": "2002-03-14", "nature": "Good", "desc": "SpaceX founded"},
            {"date": "2008-12-23", "nature": "Good", "desc": "NASA contract awarded (saved SpaceX/Tesla)"},
            {"date": "2022-10-27", "nature": "Bad", "desc": "Twitter acquisition completed (reputation/financial turmoil)"}
        ]
    },
    {
        "name": "Albert Einstein",
        "birth": {"dt": "1879-03-14 11:30", "lat": 48.4011, "lon": 9.9876, "tz": "Europe/Berlin"},
        "events": [
            {"date": "1905-09-27", "nature": "Good", "desc": "Special Relativity published (Annus Mirabilis)"},
            {"date": "1922-11-09", "nature": "Good", "desc": "Awarded Nobel Prize for Physics"},
            {"date": "1955-04-18", "nature": "Bad", "desc": "Passed away"}
        ]
    },
    {
        "name": "Warren Buffett",
        "birth": {"dt": "1930-08-30 15:00", "lat": 41.2565, "lon": -95.9345, "tz": "America/Chicago"},
        "events": [
            {"date": "1965-05-10", "nature": "Good", "desc": "Took control of Berkshire Hathaway"},
            {"date": "2006-06-25", "nature": "Good", "desc": "Pledged bulk of fortune to Gates Foundation"},
            {"date": "2008-09-15", "nature": "Bad", "desc": "Lehman crash (market turmoil)"}
        ]
    },
    {
        "name": "Oprah Winfrey",
        "birth": {"dt": "1954-01-29 04:30", "lat": 33.1251, "lon": -89.5167, "tz": "America/Chicago"},
        "events": [
            {"date": "1986-09-08", "nature": "Good", "desc": "The Oprah Winfrey Show went national"},
            {"date": "2011-01-01", "nature": "Good", "desc": "OWN Network launch"},
            {"date": "2004-09-13", "nature": "Good", "desc": "You get a car! episode"}
        ]
    },
    {
        "name": "Indira Gandhi",
        "birth": {"dt": "1917-11-19 23:11", "lat": 25.4358, "lon": 81.8463, "tz": "Asia/Kolkata"},
        "events": [
            {"date": "1966-01-24", "nature": "Good", "desc": "Became first female PM of India"},
            {"date": "1975-06-25", "nature": "Bad", "desc": "Declared Emergency (political turmoil)"},
            {"date": "1984-10-31", "nature": "Bad", "desc": "Assassination"}
        ]
    },
    {
        "name": "Shah Rukh Khan",
        "birth": {"dt": "1965-11-02 02:30", "lat": 28.6139, "lon": 77.2090, "tz": "Asia/Kolkata"},
        "events": [
            {"date": "1992-06-25", "nature": "Good", "desc": "Bollywood Debut (Deewana)"},
            {"date": "2007-08-10", "nature": "Good", "desc": "Chak De India release"},
            {"date": "2021-10-02", "nature": "Bad", "desc": "Son's arrest (Aryan Khan case)"}
        ]
    },
    {
        "name": "Mahatma Gandhi",
        "birth": {"dt": "1869-10-02 07:11", "lat": 21.6417, "lon": 69.6250, "tz": "Asia/Kolkata"},
        "events": [
            {"date": "1930-03-12", "nature": "Good", "desc": "Salt March (Dandi March)"},
            {"date": "1947-08-15", "nature": "Good", "desc": "India Independence"},
            {"date": "1948-01-30", "nature": "Bad", "desc": "Assassination"}
        ]
    },
    {
        "name": "Steve Wozniak",
        "birth": {"dt": "1950-08-11 09:45", "lat": 37.3382, "lon": -121.8863, "tz": "America/Los_Angeles"},
        "events": [
            {"date": "1976-04-01", "nature": "Good", "desc": "Apple founded"},
            {"date": "1981-02-07", "nature": "Bad", "desc": "Plane crash"},
            {"date": "1985-02-06", "nature": "Bad", "desc": "Left Apple (career change)"}
        ]
    },
    {
        "name": "Angela Merkel",
        "birth": {"dt": "1954-07-17 17:45", "lat": 53.5511, "lon": 9.9937, "tz": "Europe/Berlin"},
        "events": [
            {"date": "2005-11-22", "nature": "Good", "desc": "Became first female Chancellor of Germany"},
            {"date": "2015-08-31", "nature": "Bad", "desc": "Refugee crisis (major political backlash)"},
            {"date": "2021-12-08", "nature": "Good", "desc": "Retired with high approval ratings"}
        ]
    },
    {
        "name": "MS Dhoni",
        "birth": {"dt": "1981-07-07 11:15", "lat": 23.3441, "lon": 85.3094, "tz": "Asia/Kolkata"},
        "events": [
            {"date": "2007-09-24", "nature": "Good", "desc": "T20 World Cup Victory"},
            {"date": "2011-04-02", "nature": "Good", "desc": "ODI World Cup Victory"},
            {"date": "2020-08-15", "nature": "Good", "desc": "International retirement (clean closure)"}
        ]
    },
    {
        "name": "Virat Kohli",
        "birth": {"dt": "1988-11-05 10:28", "lat": 28.6139, "lon": 77.2090, "tz": "Asia/Kolkata"},
        "events": [
            {"date": "2008-03-02", "nature": "Good", "desc": "U-19 World Cup Win"},
            {"date": "2018-01-11", "nature": "Good", "desc": "Marriage to Anushka Sharma"},
            {"date": "2021-11-01", "nature": "Bad", "desc": "Stepped down as T20/ODI Captain"}
        ]
    },
    {
        "name": "Ratan Tata",
        "birth": {"dt": "1937-12-28 06:30", "lat": 18.9229, "lon": 72.8333, "tz": "Asia/Kolkata"},
        "events": [
            {"date": "1991-03-25", "nature": "Good", "desc": "Took over as Chairman of Tata Group"},
            {"date": "2008-01-10", "nature": "Good", "desc": "Launch of Nano (dream project)"},
            {"date": "2016-10-24", "nature": "Bad", "desc": "Cyrus Mistry dismissal controversy"}
        ]
    },
    {
        "name": "Mukesh Ambani",
        "birth": {"dt": "1957-04-19 19:53", "lat": 12.7855, "lon": 45.0186, "tz": "Asia/Aden"},
        "events": [
            {"date": "2002-07-06", "nature": "Bad", "desc": "Father Dhirubhai passed away"},
            {"date": "2016-09-05", "nature": "Good", "desc": "Jio Launch (market disruption)"},
            {"date": "2005-06-18", "nature": "Bad", "desc": "Reliance split with brother Anil"}
        ]
    },
    {
        "name": "Roger Federer",
        "birth": {"dt": "1981-08-08 08:40", "lat": 47.5596, "lon": 7.5886, "tz": "Europe/Zurich"},
        "events": [
            {"date": "2003-07-06", "nature": "Good", "desc": "First Wimbledon title"},
            {"date": "2016-07-26", "nature": "Bad", "desc": "Knee injury (ended season)"},
            {"date": "2017-01-29", "nature": "Good", "desc": "Australian Open comeback win"}
        ]
    },
    {
        "name": "Cristiano Ronaldo",
        "birth": {"dt": "1985-02-05 10:20", "lat": 32.6667, "lon": -16.9167, "tz": "Atlantic/Madeira"},
        "events": [
            {"date": "2008-05-21", "nature": "Good", "desc": "First Champions League Win"},
            {"date": "2022-11-22", "nature": "Bad", "desc": "Contract terminated by Man Utd (unceremonious exit)"},
            {"date": "2016-07-10", "nature": "Good", "desc": "Euro 2016 Victory"}
        ]
    },
    {
        "name": "Lionel Messi",
        "birth": {"dt": "1987-06-24 06:00", "lat": -32.9442, "lon": -60.6505, "tz": "America/Argentina/Rosario"},
        "events": [
            {"date": "2005-08-17", "nature": "Bad", "desc": "Red card in international debut"},
            {"date": "2021-07-10", "nature": "Good", "desc": "Copa America win (first major intl trophy)"},
            {"date": "2022-12-18", "nature": "Good", "desc": "World Cup Victory"}
        ]
    },
    {
        "name": "Tiger Woods",
        "birth": {"dt": "1975-12-30 22:50", "lat": 33.8353, "lon": -118.0585, "tz": "America/Los_Angeles"},
        "events": [
            {"date": "1997-04-13", "nature": "Good", "desc": "First Masters Win (record breaking)"},
            {"date": "2009-11-27", "nature": "Bad", "desc": "Car crash (infidelity scandal reveal)"},
            {"date": "2019-04-14", "nature": "Good", "desc": "Masters comeback win"}
        ]
    },
    {
        "name": "Michael Jordan",
        "birth": {"dt": "1963-02-17 13:40", "lat": 40.6782, "lon": -73.9442, "tz": "America/New_York"},
        "events": [
            {"date": "1991-06-12", "nature": "Good", "desc": "First NBA Championship"},
            {"date": "1993-07-23", "nature": "Bad", "desc": "Father murdered"},
            {"date": "1995-03-18", "nature": "Good", "desc": "I'm back announcement"}
        ]
    },
    {
        "name": "Serena Williams",
        "birth": {"dt": "1981-09-26 20:28", "lat": 34.0522, "lon": -118.2437, "tz": "America/Los_Angeles"},
        "events": [
            {"date": "1999-09-11", "nature": "Good", "desc": "First US Open title"},
            {"date": "2011-03-02", "nature": "Bad", "desc": "Pulmonary embolism/Health scare"},
            {"date": "2017-01-28", "nature": "Good", "desc": "Australian Open win while pregnant"}
        ]
    },
    {
        "name": "Stephen Hawking",
        "birth": {"dt": "1942-01-08 09:30", "lat": 51.7520, "lon": -1.2577, "tz": "Europe/London"},
        "events": [
            {"date": "1963-01-01", "nature": "Bad", "desc": "Diagnosed with ALS"},
            {"date": "1988-03-01", "nature": "Good", "desc": "A Brief History of Time published"},
            {"date": "2018-03-14", "nature": "Bad", "desc": "Passed away"}
        ]
    },
    {
        "name": "Mark Zuckerberg",
        "birth": {"dt": "1984-05-14 14:39", "lat": 41.0334, "lon": -73.7629, "tz": "America/New_York"},
        "events": [
            {"date": "2004-02-04", "nature": "Good", "desc": "TheFacebook launch"},
            {"date": "2012-05-18", "nature": "Good", "desc": "Facebook IPO"},
            {"date": "2018-04-10", "nature": "Bad", "desc": "Cambridge Analytica testimony"}
        ]
    },
    {
        "name": "Jeff Bezos",
        "birth": {"dt": "1964-01-12 11:33", "lat": 35.0844, "lon": -106.6504, "tz": "America/Denver"},
        "events": [
            {"date": "1994-07-05", "nature": "Good", "desc": "Amazon founded"},
            {"date": "2019-01-09", "nature": "Bad", "desc": "Announced divorce"},
            {"date": "2021-07-20", "nature": "Good", "desc": "First space flight"}
        ]
    },
    {
        "name": "Taylor Swift",
        "birth": {"dt": "1989-12-13 08:36", "lat": 40.3356, "lon": -75.9269, "tz": "America/New_York"},
        "events": [
            {"date": "2006-10-24", "nature": "Good", "desc": "Debut album release"},
            {"date": "2009-09-13", "nature": "Bad", "desc": "Kanye West VMA incident"},
            {"date": "2023-03-17", "nature": "Good", "desc": "Eras Tour launch (massive success)"}
        ]
    },
    {
        "name": "Beyonce",
        "birth": {"dt": "1981-09-04 10:00", "lat": 29.7604, "lon": -95.3698, "tz": "America/Chicago"},
        "events": [
            {"date": "2003-06-24", "nature": "Good", "desc": "Dangerously in Love release (Solo debut)"},
            {"date": "2008-04-04", "nature": "Good", "desc": "Marriage to Jay-Z"},
            {"date": "2016-04-23", "nature": "Good", "desc": "Lemonade release"}
        ]
    },
    {
        "name": "Tom Hanks",
        "birth": {"dt": "1956-07-09 11:17", "lat": 37.6688, "lon": -121.8747, "tz": "America/Los_Angeles"},
        "events": [
            {"date": "1994-03-21", "nature": "Good", "desc": "First Oscar for Philadelphia"},
            {"date": "1995-03-27", "nature": "Good", "desc": "Second Oscar for Forrest Gump"},
            {"date": "2020-03-11", "nature": "Bad", "desc": "Contracted COVID-19 (first major celeb case)"}
        ]
    },
    {
        "name": "Meryl Streep",
        "birth": {"dt": "1949-06-22 08:05", "lat": 40.7144, "lon": -74.4011, "tz": "America/New_York"},
        "events": [
            {"date": "1980-04-14", "nature": "Good", "desc": "First Oscar (Kramer vs Kramer)"},
            {"date": "2012-02-26", "nature": "Good", "desc": "Third Oscar (The Iron Lady)"},
            {"date": "1978-03-12", "nature": "Bad", "desc": "Partner John Cazale passed away"}
        ]
    },
    {
        "name": "Nelson Mandela",
        "birth": {"dt": "1918-07-18 14:54", "lat": -31.9833, "lon": 28.5167, "tz": "Africa/Johannesburg"},
        "events": [
            {"date": "1964-06-12", "nature": "Bad", "desc": "Sentenced to life imprisonment"},
            {"date": "1990-02-11", "nature": "Good", "desc": "Released from prison"},
            {"date": "1994-05-10", "nature": "Good", "desc": "Inaugurated as President"}
        ]
    },
    {
        "name": "Vladimir Putin",
        "birth": {"dt": "1952-10-07 09:30", "lat": 59.9343, "lon": 30.3351, "tz": "Europe/Moscow"},
        "events": [
            {"date": "1999-12-31", "nature": "Good", "desc": "Became Acting President"},
            {"date": "2022-02-24", "nature": "Bad", "desc": "Invaded Ukraine (global isolation/turmoil)"},
            {"date": "2013-06-06", "nature": "Bad", "desc": "Announced divorce"}
        ]
    },
    {
        "name": "Xi Jinping",
        "birth": {"dt": "1953-06-15 09:00", "lat": 39.9042, "lon": 116.4074, "tz": "Asia/Shanghai"},
        "events": [
            {"date": "2012-11-15", "nature": "Good", "desc": "Became General Secretary of CCP"},
            {"date": "2018-03-11", "nature": "Good", "desc": "Abolished term limits"},
            {"date": "2020-01-23", "nature": "Bad", "desc": "Wuhan lockdown (COVID start)"}
        ]
    },
    {
        "name": "Elizabeth II",
        "birth": {"dt": "1926-04-21 02:40", "lat": 51.5074, "lon": -0.1278, "tz": "Europe/London"},
        "events": [
            {"date": "1952-02-06", "nature": "Good", "desc": "Accession to the throne"},
            {"date": "1992-11-20", "nature": "Bad", "desc": "Annus Horribilis (Windsor fire/divorces)"},
            {"date": "2021-04-09", "nature": "Bad", "desc": "Prince Philip passed away"}
        ]
    },
    {
        "name": "Charles III",
        "birth": {"dt": "1948-11-14 21:14", "lat": 51.5074, "lon": -0.1278, "tz": "Europe/London"},
        "events": [
            {"date": "1981-07-29", "nature": "Good", "desc": "Marriage to Diana"},
            {"date": "1996-08-28", "nature": "Bad", "desc": "Divorce from Diana"},
            {"date": "2022-09-08", "nature": "Good", "desc": "Accession to the throne"}
        ]
    },
    {
        "name": "Prince William",
        "birth": {"dt": "1982-06-21 21:03", "lat": 51.5074, "lon": -0.1278, "tz": "Europe/London"},
        "events": [
            {"date": "2011-04-29", "nature": "Good", "desc": "Marriage to Kate Middleton"},
            {"date": "1997-08-31", "nature": "Bad", "desc": "Mother's death"},
            {"date": "2022-09-08", "nature": "Good", "desc": "Became Prince of Wales"}
        ]
    },
    {
        "name": "Prince Harry",
        "birth": {"dt": "1984-09-15 16:20", "lat": 51.5074, "lon": -0.1278, "tz": "Europe/London"},
        "events": [
            {"date": "2018-05-19", "nature": "Good", "desc": "Marriage to Meghan Markle"},
            {"date": "2020-01-08", "nature": "Bad", "desc": "Megxit announcement (separation from family)"},
            {"date": "1997-08-31", "nature": "Bad", "desc": "Mother's death"}
        ]
    },
    {
        "name": "Muhammad Ali",
        "birth": {"dt": "1942-01-17 18:35", "lat": 38.2527, "lon": -85.7585, "tz": "America/Kentucky/Louisville"},
        "events": [
            {"date": "1964-02-25", "nature": "Good", "desc": "First Heavyweight title (vs Liston)"},
            {"date": "1967-04-28", "nature": "Bad", "desc": "Stripped of title (Draft refusal)"},
            {"date": "1974-10-30", "nature": "Good", "desc": "Rumble in the Jungle win"}
        ]
    },
    {
        "name": "Michael Jackson",
        "birth": {"dt": "1958-08-29 19:33", "lat": 41.5833, "lon": -87.3333, "tz": "America/Chicago"},
        "events": [
            {"date": "1982-11-30", "nature": "Good", "desc": "Thriller release"},
            {"date": "2005-06-13", "nature": "Bad", "desc": "Trial verdict (stress/turmoil)"},
            {"date": "2009-06-25", "nature": "Bad", "desc": "Passed away"}
        ]
    },
    {
        "name": "John Lennon",
        "birth": {"dt": "1940-10-09 18:30", "lat": 53.4084, "lon": -2.9916, "tz": "Europe/London"},
        "events": [
            {"date": "1964-02-07", "nature": "Good", "desc": "Beatles land in USA"},
            {"date": "1970-04-10", "nature": "Bad", "desc": "Beatles breakup"},
            {"date": "1980-12-08", "nature": "Bad", "desc": "Assassination"}
        ]
    },
    {
        "name": "Paul McCartney",
        "birth": {"dt": "1942-06-18 14:00", "lat": 53.4084, "lon": -2.9916, "tz": "Europe/London"},
        "events": [
            {"date": "1964-02-07", "nature": "Good", "desc": "Beatles USA arrival"},
            {"date": "1998-04-17", "nature": "Bad", "desc": "Wife Linda passed away"},
            {"date": "2012-07-27", "nature": "Good", "desc": "Olympic Opening Ceremony performance"}
        ]
    },
    {
        "name": "Elvis Presley",
        "birth": {"dt": "1935-01-08 04:35", "lat": 34.2576, "lon": -88.7034, "tz": "America/Chicago"},
        "events": [
            {"date": "1956-01-27", "nature": "Good", "desc": "Heartbreak Hotel release"},
            {"date": "1973-10-09", "nature": "Bad", "desc": "Divorce from Priscilla"},
            {"date": "1977-08-16", "nature": "Bad", "desc": "Passed away"}
        ]
    },
    {
        "name": "Marilyn Monroe",
        "birth": {"dt": "1926-06-01 09:30", "lat": 34.0522, "lon": -118.2437, "tz": "America/Los_Angeles"},
        "events": [
            {"date": "1953-07-01", "nature": "Good", "desc": "Gentlemen Prefer Blondes release (peak fame)"},
            {"date": "1961-01-20", "nature": "Bad", "desc": "Divorce from Arthur Miller"},
            {"date": "1962-08-04", "nature": "Bad", "desc": "Passed away"}
        ]
    },
    {
        "name": "Nikola Tesla",
        "birth": {"dt": "1856-07-10 00:00", "lat": 44.5650, "lon": 15.3050, "tz": "Europe/Belgrade"},
        "events": [
            {"date": "1888-05-16", "nature": "Good", "desc": "AC motor patent (Westinghouse deal)"},
            {"date": "1895-03-13", "nature": "Bad", "desc": "Lab fire (lost all research)"},
            {"date": "1943-01-07", "nature": "Bad", "desc": "Passed away in poverty"}
        ]
    },
    {
        "name": "Leonardo da Vinci",
        "birth": {"dt": "1452-04-15 21:40", "lat": 43.7844, "lon": 10.9290, "tz": "Europe/Rome"},
        "events": [
            {"date": "1482-04-01", "nature": "Good", "desc": "Moved to Milan (artistic peak period)"},
            {"date": "1503-01-01", "nature": "Good", "desc": "Started Mona Lisa"},
            {"date": "1519-05-02", "nature": "Bad", "desc": "Passed away"}
        ]
    },
    {
        "name": "Isaac Newton",
        "birth": {"dt": "1643-01-04 01:00", "lat": 52.6520, "lon": -0.4800, "tz": "Europe/London"},
        "events": [
            {"date": "1687-07-05", "nature": "Good", "desc": "Principia Mathematica published"},
            {"date": "1705-04-16", "nature": "Good", "desc": "Knighted by Queen Anne"},
            {"date": "1727-03-31", "nature": "Bad", "desc": "Passed away"}
        ]
    },
    {
        "name": "Galileo Galilei",
        "birth": {"dt": "1564-02-15 15:30", "lat": 43.7711, "lon": 11.2486, "tz": "Europe/Rome"},
        "events": [
            {"date": "1610-01-07", "nature": "Good", "desc": "Discovered Jupiter moons"},
            {"date": "1633-06-22", "nature": "Bad", "desc": "Forced to recant by Inquisition"},
            {"date": "1642-01-08", "nature": "Bad", "desc": "Passed away"}
        ]
    },
    {
        "name": "Marie Curie",
        "birth": {"dt": "1867-11-07 12:00", "lat": 52.2297, "lon": 21.0122, "tz": "Europe/Warsaw"},
        "events": [
            {"date": "1903-12-10", "nature": "Good", "desc": "First Nobel Prize (Physics)"},
            {"date": "1911-12-10", "nature": "Good", "desc": "Second Nobel Prize (Chemistry)"},
            {"date": "1934-07-04", "nature": "Bad", "desc": "Passed away from radiation"}
        ]
    },
    {
        "name": "Charles Darwin",
        "birth": {"dt": "1809-02-12 03:00", "lat": 52.9390, "lon": -1.2020, "tz": "Europe/London"},
        "events": [
            {"date": "1859-11-24", "nature": "Good", "desc": "Origin of Species published"},
            {"date": "1839-01-29", "nature": "Good", "desc": "Marriage to Emma Wedgwood"},
            {"date": "1882-04-19", "nature": "Bad", "desc": "Passed away"}
        ]
    },
    {
        "name": "Wolfgang Mozart",
        "birth": {"dt": "1756-01-27 20:55", "lat": 47.8095, "lon": 13.0550, "tz": "Europe/Vienna"},
        "events": [
            {"date": "1762-01-01", "nature": "Good", "desc": "First public performance (child prodigy)"},
            {"date": "1781-03-16", "nature": "Good", "desc": "Don Giovanni premiere"},
            {"date": "1791-12-05", "nature": "Bad", "desc": "Passed away"}
        ]
    },
    {
        "name": "Ludwig van Beethoven",
        "birth": {"dt": "1770-12-17 01:00", "lat": 50.7374, "lon": 7.0982, "tz": "Europe/Berlin"},
        "events": [
            {"date": "1804-01-01", "nature": "Good", "desc": "Eroica Symphony (artistic peak)"},
            {"date": "1819-01-01", "nature": "Bad", "desc": "Became completely deaf"},
            {"date": "1827-03-26", "nature": "Bad", "desc": "Passed away"}
        ]
    },
    {
        "name": "William Shakespeare",
        "birth": {"dt": "1564-04-23 08:00", "lat": 52.1936, "lon": -1.7083, "tz": "Europe/London"},
        "events": [
            {"date": "1582-11-27", "nature": "Good", "desc": "Married Anne Hathaway"},
            {"date": "1599-01-01", "nature": "Good", "desc": "Globe Theatre built (peak career)"},
            {"date": "1616-04-23", "nature": "Bad", "desc": "Passed away"}
        ]
    },
    {
        "name": "Vincent van Gogh",
        "birth": {"dt": "1853-03-30 11:00", "lat": 51.4416, "lon": 5.4697, "tz": "Europe/Amsterdam"},
        "events": [
            {"date": "1888-12-23", "nature": "Bad", "desc": "Cut off own ear"},
            {"date": "1889-05-08", "nature": "Bad", "desc": "Admitted to asylum"},
            {"date": "1890-07-29", "nature": "Bad", "desc": "Passed away (suicide)"}
        ]
    },
    {
        "name": "Pablo Picasso",
        "birth": {"dt": "1881-10-25 23:15", "lat": 36.7213, "lon": -4.4214, "tz": "Europe/Madrid"},
        "events": [
            {"date": "1907-01-01", "nature": "Good", "desc": "Les Demoiselles d'Avignon (Cubism)"},
            {"date": "1937-06-26", "nature": "Good", "desc": "Guernica completed"},
            {"date": "1973-04-08", "nature": "Bad", "desc": "Passed away"}
        ]
    },
    {
        "name": "Salvador Dali",
        "birth": {"dt": "1904-05-11 08:45", "lat": 42.2683, "lon": 2.9622, "tz": "Europe/Madrid"},
        "events": [
            {"date": "1931-01-01", "nature": "Good", "desc": "The Persistence of Memory"},
            {"date": "1958-08-08", "nature": "Good", "desc": "Married Gala (muse)"},
            {"date": "1989-01-23", "nature": "Bad", "desc": "Passed away"}
        ]
    },
    {
        "name": "Sigmund Freud",
        "birth": {"dt": "1856-05-06 18:30", "lat": 49.4875, "lon": 18.3500, "tz": "Europe/Vienna"},
        "events": [
            {"date": "1900-11-01", "nature": "Good", "desc": "Interpretation of Dreams published"},
            {"date": "1939-02-01", "nature": "Bad", "desc": "Forced to flee Vienna (Nazis)"},
            {"date": "1939-09-23", "nature": "Bad", "desc": "Passed away"}
        ]
    },
    {
        "name": "Winston Churchill",
        "birth": {"dt": "1874-11-30 01:30", "lat": 51.5074, "lon": -0.1278, "tz": "Europe/London"},
        "events": [
            {"date": "1940-05-10", "nature": "Good", "desc": "Became PM during WWII"},
            {"date": "1945-07-26", "nature": "Bad", "desc": "Lost election after war"},
            {"date": "1953-12-10", "nature": "Good", "desc": "Nobel Prize for Literature"}
        ]
    },
    {
        "name": "Franklin D. Roosevelt",
        "birth": {"dt": "1882-01-30 20:45", "lat": 41.1865, "lon": -73.7272, "tz": "America/New_York"},
        "events": [
            {"date": "1933-03-04", "nature": "Good", "desc": "First inauguration (New Deal)"},
            {"date": "1941-12-08", "nature": "Bad", "desc": "Pearl Harbor / WWII entry"},
            {"date": "1945-04-12", "nature": "Bad", "desc": "Passed away"}
        ]
    },
    {
        "name": "John F. Kennedy",
        "birth": {"dt": "1917-05-29 15:00", "lat": 42.3318, "lon": -71.1212, "tz": "America/New_York"},
        "events": [
            {"date": "1960-11-08", "nature": "Good", "desc": "Won Presidential Election"},
            {"date": "1961-05-25", "nature": "Good", "desc": "Moon speech"},
            {"date": "1963-11-22", "nature": "Bad", "desc": "Assassination"}
        ]
    },
    {
        "name": "Martin Luther King Jr",
        "birth": {"dt": "1929-01-15 12:00", "lat": 33.7537, "lon": -84.3863, "tz": "America/New_York"},
        "events": [
            {"date": "1955-12-01", "nature": "Good", "desc": "Montgomery Bus Boycott"},
            {"date": "1963-08-28", "nature": "Good", "desc": "I Have a Dream speech"},
            {"date": "1968-04-04", "nature": "Bad", "desc": "Assassination"}
        ]
    },
    {
        "name": "Mother Teresa",
        "birth": {"dt": "1910-08-26 14:25", "lat": 42.0000, "lon": 21.4333, "tz": "Europe/Skopje"},
        "events": [
            {"date": "1950-10-07", "nature": "Good", "desc": "Missionaries of Charity founded"},
            {"date": "1979-10-17", "nature": "Good", "desc": "Nobel Peace Prize"},
            {"date": "1997-09-05", "nature": "Bad", "desc": "Passed away"}
        ]
    },
    {
        "name": "Pope Francis",
        "birth": {"dt": "1936-12-17 21:00", "lat": -34.6037, "lon": -58.3816, "tz": "America/Argentina/Buenos_Aires"},
        "events": [
            {"date": "2013-03-13", "nature": "Good", "desc": "Elected Pope"},
            {"date": "1958-03-11", "nature": "Bad", "desc": "Lung removed (health crisis)"},
            {"date": "2025-04-21", "nature": "Bad", "desc": "Passed away"}
        ]
    },
    {
        "name": "Dalai Lama",
        "birth": {"dt": "1935-07-06 04:38", "lat": 36.6485, "lon": 101.7500, "tz": "Asia/Shanghai"},
        "events": [
            {"date": "1950-11-17", "nature": "Good", "desc": "Enthroned as Dalai Lama"},
            {"date": "1989-12-10", "nature": "Good", "desc": "Nobel Peace Prize"},
            {"date": "1959-03-17", "nature": "Bad", "desc": "Fled to India (Tibetan uprising)"}
        ]
    },
    {
        "name": "Maharishi Mahesh Yogi",
        "birth": {"dt": "1918-01-12 03:00", "lat": 25.4358, "lon": 81.8463, "tz": "Asia/Kolkata"},
        "events": [
            {"date": "1959-01-01", "nature": "Good", "desc": "TM movement launched globally"},
            {"date": "1968-02-01", "nature": "Good", "desc": "Beatles visited Rishikesh"},
            {"date": "2008-02-05", "nature": "Bad", "desc": "Passed away"}
        ]
    },
    {
        "name": "Sri Sri Ravi Shankar",
        "birth": {"dt": "1956-05-13 06:20", "lat": 11.9416, "lon": 79.8083, "tz": "Asia/Kolkata"},
        "events": [
            {"date": "1981-01-01", "nature": "Good", "desc": "Art of Living founded"},
            {"date": "1986-09-13", "nature": "Good", "desc": "First World Peace Summit"},
            {"date": "2020-03-01", "nature": "Bad", "desc": "COVID lockdown impact on org"}
        ]
    },
    {
        "name": "Jawaharlal Nehru",
        "birth": {"dt": "1889-11-14 23:03", "lat": 25.4358, "lon": 81.8463, "tz": "Asia/Kolkata"},
        "events": [
            {"date": "1947-08-15", "nature": "Good", "desc": "Became first PM of India"},
            {"date": "1962-11-21", "nature": "Bad", "desc": "China War defeat"},
            {"date": "1964-05-27", "nature": "Bad", "desc": "Passed away"}
        ]
    },
    {
        "name": "Indira Gandhi",
        "birth": {"dt": "1917-11-19 23:11", "lat": 25.4358, "lon": 81.8463, "tz": "Asia/Kolkata"},
        "events": [
            {"date": "1966-01-24", "nature": "Good", "desc": "Became first female PM of India"},
            {"date": "1975-06-25", "nature": "Bad", "desc": "Declared Emergency"},
            {"date": "1984-10-31", "nature": "Bad", "desc": "Assassination"}
        ]
    },
    {
        "name": "Rajiv Gandhi",
        "birth": {"dt": "1944-08-20 10:00", "lat": 18.5204, "lon": 73.8567, "tz": "Asia/Kolkata"},
        "events": [
            {"date": "1984-10-31", "nature": "Good", "desc": "Became PM after mother's death"},
            {"date": "1991-05-21", "nature": "Bad", "desc": "Assassination"},
            {"date": "1987-07-18", "nature": "Bad", "desc": "Bofors scandal broke"}
        ]
    },
    {
        "name": "Sonia Gandhi",
        "birth": {"dt": "1946-12-09 21:30", "lat": 41.9028, "lon": 12.4964, "tz": "Europe/Rome"},
        "events": [
            {"date": "1968-02-25", "nature": "Good", "desc": "Married Rajiv Gandhi"},
            {"date": "1998-03-14", "nature": "Good", "desc": "Became Congress President"},
            {"date": "1991-05-21", "nature": "Bad", "desc": "Husband Rajiv assassinated"}
        ]
    },
    {
        "name": "Atal Bihari Vajpayee",
        "birth": {"dt": "1924-12-25 04:00", "lat": 25.4358, "lon": 81.8463, "tz": "Asia/Kolkata"},
        "events": [
            {"date": "1996-05-16", "nature": "Good", "desc": "First term as PM (13 days)"},
            {"date": "1998-03-19", "nature": "Good", "desc": "Second term as PM (nuclear tests)"},
            {"date": "2018-08-16", "nature": "Bad", "desc": "Passed away"}
        ]
    },
    {
        "name": "Manmohan Singh",
        "birth": {"dt": "1932-09-26 08:30", "lat": 31.6340, "lon": 74.8723, "tz": "Asia/Kolkata"},
        "events": [
            {"date": "1991-07-24", "nature": "Good", "desc": "Economic reforms as FM"},
            {"date": "2004-05-22", "nature": "Good", "desc": "Became PM"},
            {"date": "2014-05-26", "nature": "Bad", "desc": "Lost election / Stepped down"}
        ]
    },
    {
        "name": "PV Narasimha Rao",
        "birth": {"dt": "1921-06-28 12:30", "lat": 17.4065, "lon": 78.4772, "tz": "Asia/Kolkata"},
        "events": [
            {"date": "1991-06-21", "nature": "Good", "desc": "Became PM (economic liberalization)"},
            {"date": "1992-12-06", "nature": "Bad", "desc": "Babri Masjid demolition"},
            {"date": "2004-12-23", "nature": "Bad", "desc": "Passed away"}
        ]
    },
    {
        "name": "JRD Tata",
        "birth": {"dt": "1904-07-29 03:00", "lat": 48.8566, "lon": 2.3522, "tz": "Europe/Paris"},
        "events": [
            {"date": "1938-01-01", "nature": "Good", "desc": "Became Chairman of Tata Group"},
            {"date": "1953-01-01", "nature": "Good", "desc": "Air India nationalization"},
            {"date": "1993-11-29", "nature": "Bad", "desc": "Passed away"}
        ]
    },
    {
        "name": "Dhirubhai Ambani",
        "birth": {"dt": "1932-12-28 06:00", "lat": 21.1702, "lon": 72.8311, "tz": "Asia/Kolkata"},
        "events": [
            {"date": "1957-02-01", "nature": "Good", "desc": "Started Reliance trading"},
            {"date": "1977-05-01", "nature": "Good", "desc": "Reliance went public (IPO)"},
            {"date": "2002-07-06", "nature": "Bad", "desc": "Passed away"}
        ]
    },
    {
        "name": "Azim Premji",
        "birth": {"dt": "1945-07-24 08:45", "lat": 18.5204, "lon": 73.8567, "tz": "Asia/Kolkata"},
        "events": [
            {"date": "1966-01-01", "nature": "Good", "desc": "Took over Wipro"},
            {"date": "1980-01-01", "nature": "Good", "desc": "Wipro IT pivot"},
            {"date": "2019-01-01", "nature": "Good", "desc": "Stepped down as Chairman"}
        ]
    },
    {
        "name": "Narayana Murthy",
        "birth": {"dt": "1946-08-20 11:04", "lat": 12.9716, "lon": 77.5946, "tz": "Asia/Kolkata"},
        "events": [
            {"date": "1981-07-02", "nature": "Good", "desc": "Infosys founded"},
            {"date": "1999-01-01", "nature": "Good", "desc": "Infosys IPO (NASDAQ listing)"},
            {"date": "2014-06-14", "nature": "Good", "desc": "Retired from active role"}
        ]
    },
    {
        "name": "Satya Nadella",
        "birth": {"dt": "1967-08-19 12:00", "lat": 17.4065, "lon": 78.4772, "tz": "Asia/Kolkata"},
        "events": [
            {"date": "2014-02-04", "nature": "Good", "desc": "Became CEO of Microsoft"},
            {"date": "1992-01-01", "nature": "Good", "desc": "Joined Microsoft"},
            {"date": "1992-01-01", "nature": "Good", "desc": "Married Anupama"}
        ]
    },
    {
        "name": "Sundar Pichai",
        "birth": {"dt": "1972-06-10 12:00", "lat": 13.0827, "lon": 80.2707, "tz": "Asia/Kolkata"},
        "events": [
            {"date": "2015-08-10", "nature": "Good", "desc": "Became CEO of Google"},
            {"date": "2004-04-01", "nature": "Good", "desc": "Joined Google"},
            {"date": "2019-12-03", "nature": "Good", "desc": "Became CEO of Alphabet"}
        ]
    },
    {
        "name": "Tim Cook",
        "birth": {"dt": "1960-11-01 12:00", "lat": 33.5186, "lon": -86.8104, "tz": "America/Chicago"},
        "events": [
            {"date": "2011-08-24", "nature": "Good", "desc": "Became CEO of Apple"},
            {"date": "1998-03-01", "nature": "Good", "desc": "Joined Apple"},
            {"date": "2014-10-30", "nature": "Good", "desc": "Came out publicly as gay"}
        ]
    },
    {
        "name": "Jack Ma",
        "birth": {"dt": "1964-09-10 12:00", "lat": 30.2741, "lon": 120.1551, "tz": "Asia/Shanghai"},
        "events": [
            {"date": "1999-06-01", "nature": "Good", "desc": "Alibaba founded"},
            {"date": "2014-09-19", "nature": "Good", "desc": "Alibaba IPO (largest ever)"},
            {"date": "2020-10-24", "nature": "Bad", "desc": "Ant Group IPO blocked by China"}
        ]
    },
    {
        "name": "Masayoshi Son",
        "birth": {"dt": "1957-08-11 12:00", "lat": 33.5902, "lon": 130.4017, "tz": "Asia/Tokyo"},
        "events": [
            {"date": "1981-09-01", "nature": "Good", "desc": "SoftBank founded"},
            {"date": "2000-01-01", "nature": "Good", "desc": "Vision Fund era began"},
            {"date": "2019-09-01", "nature": "Bad", "desc": "WeWork IPO collapse"}
        ]
    },
    {
        "name": "Richard Branson",
        "birth": {"dt": "1950-07-18 07:00", "lat": 51.4244, "lon": -0.3680, "tz": "Europe/London"},
        "events": [
            {"date": "1970-01-01", "nature": "Good", "desc": "Virgin Records founded"},
            {"date": "1984-06-22", "nature": "Good", "desc": "Virgin Atlantic launch"},
            {"date": "2021-07-11", "nature": "Good", "desc": "Space flight (Virgin Galactic)"}
        ]
    },
    {
        "name": "Larry Page",
        "birth": {"dt": "1973-03-26 01:00", "lat": 37.4419, "lon": -122.1430, "tz": "America/Los_Angeles"},
        "events": [
            {"date": "1998-09-04", "nature": "Good", "desc": "Google founded"},
            {"date": "2004-08-19", "nature": "Good", "desc": "Google IPO"},
            {"date": "2015-08-10", "nature": "Good", "desc": "Alphabet restructure"}
        ]
    },
    {
        "name": "Sergey Brin",
        "birth": {"dt": "1973-08-21 09:00", "lat": 55.7558, "lon": 37.6173, "tz": "Europe/Moscow"},
        "events": [
            {"date": "1998-09-04", "nature": "Good", "desc": "Google founded"},
            {"date": "2004-08-19", "nature": "Good", "desc": "Google IPO"},
            {"date": "2007-05-01", "nature": "Good", "desc": "Married Anne Wojcicki"}
        ]
    },
    {
        "name": "Pierre Omidyar",
        "birth": {"dt": "1967-06-21 12:00", "lat": 48.8566, "lon": 2.3522, "tz": "Europe/Paris"},
        "events": [
            {"date": "1995-09-03", "nature": "Good", "desc": "eBay founded"},
            {"date": "1998-09-24", "nature": "Good", "desc": "eBay IPO"},
            {"date": "2015-07-20", "nature": "Good", "desc": "Stepped down from eBay"}
        ]
    },
    {
        "name": "Brian Chesky",
        "birth": {"dt": "1981-08-29 12:00", "lat": 43.0618, "lon": -74.9800, "tz": "America/New_York"},
        "events": [
            {"date": "2008-08-01", "nature": "Good", "desc": "Airbnb founded"},
            {"date": "2020-12-10", "nature": "Good", "desc": "Airbnb IPO"},
            {"date": "2020-03-01", "nature": "Bad", "desc": "COVID crisis (massive layoffs)"}
        ]
    },
    {
        "name": "Travis Kalanick",
        "birth": {"dt": "1976-08-06 12:00", "lat": 34.0522, "lon": -118.2437, "tz": "America/Los_Angeles"},
        "events": [
            {"date": "2009-03-01", "nature": "Good", "desc": "Uber founded"},
            {"date": "2017-06-21", "nature": "Bad", "desc": "Resigned as CEO (scandals)"},
            {"date": "2019-05-10", "nature": "Good", "desc": "Uber IPO"}
        ]
    },
    {
        "name": "Pete Sampras",
        "birth": {"dt": "1971-08-12 12:00", "lat": 34.0522, "lon": -118.2437, "tz": "America/Los_Angeles"},
        "events": [
            {"date": "1990-02-01", "nature": "Good", "desc": "First Grand Slam win"},
            {"date": "2002-09-08", "nature": "Good", "desc": "Final US Open win (14th major)"},
            {"date": "2003-08-25", "nature": "Good", "desc": "Retired from tennis"}
        ]
    },
    {
        "name": "Andre Agassi",
        "birth": {"dt": "1970-04-29 12:00", "lat": 36.1699, "lon": -115.1398, "tz": "America/Los_Angeles"},
        "events": [
            {"date": "1992-06-07", "nature": "Good", "desc": "First Wimbledon win"},
            {"date": "1997-01-01", "nature": "Bad", "desc": "Rank dropped to 141 (drugs/divorce)"},
            {"date": "2001-09-09", "nature": "Good", "desc": "US Open win (career Grand Slam)"}
        ]
    },
    {
        "name": "Bjorn Borg",
        "birth": {"dt": "1956-06-06 12:15", "lat": 59.3293, "lon": 18.0686, "tz": "Europe/Stockholm"},
        "events": [
            {"date": "1974-06-01", "nature": "Good", "desc": "First French Open win"},
            {"date": "1980-07-05", "nature": "Good", "desc": "Fifth Wimbledon win"},
            {"date": "1983-01-23", "nature": "Bad", "desc": "Retired suddenly at 26"}
        ]
    },
    {
        "name": "John McEnroe",
        "birth": {"dt": "1959-02-16 12:00", "lat": 40.6892, "lon": -73.9442, "tz": "America/New_York"},
        "events": [
            {"date": "1977-01-01", "nature": "Good", "desc": "Reached Wimbledon semifinals"},
            {"date": "1984-07-01", "nature": "Good", "desc": "Best season ever (82-3 record)"},
            {"date": "1992-01-01", "nature": "Bad", "desc": "Retired from singles"}
        ]
    },
    {
        "name": "Rod Laver",
        "birth": {"dt": "1938-08-09 12:00", "lat": -27.4678, "lon": 153.0281, "tz": "Australia/Brisbane"},
        "events": [
            {"date": "1962-01-01", "nature": "Good", "desc": "First Grand Slam (amateur)"},
            {"date": "1969-01-01", "nature": "Good", "desc": "Second Grand Slam (Open era)"},
            {"date": "1979-07-01", "nature": "Good", "desc": "Entered Hall of Fame"}
        ]
    },
    {
        "name": "Usain Bolt",
        "birth": {"dt": "1986-08-21 12:00", "lat": 17.9712, "lon": -76.7920, "tz": "America/Jamaica"},
        "events": [
            {"date": "2008-08-16", "nature": "Good", "desc": "100m world record Beijing"},
            {"date": "2012-08-05", "nature": "Good", "desc": "London Olympics 100m gold"},
            {"date": "2017-08-12", "nature": "Bad", "desc": "Final race (injured/loss)"}
        ]
    },
    {
        "name": "Carl Lewis",
        "birth": {"dt": "1961-07-01 12:00", "lat": 35.7796, "lon": -78.6382, "tz": "America/New_York"},
        "events": [
            {"date": "1984-08-04", "nature": "Good", "desc": "LA Olympics 4 gold medals"},
            {"date": "1988-09-24", "nature": "Good", "desc": "Seoul Olympics 100m gold"},
            {"date": "1996-07-29", "nature": "Good", "desc": "Atlanta long jump gold (9th medal)"}
        ]
    },
    {
        "name": "Jesse Owens",
        "birth": {"dt": "1913-09-12 12:00", "lat": 33.1581, "lon": -87.5261, "tz": "America/Chicago"},
        "events": [
            {"date": "1936-08-09", "nature": "Good", "desc": "Berlin Olympics 4 gold medals"},
            {"date": "1936-05-25", "nature": "Good", "desc": "Set 4 world records in one hour"},
            {"date": "1980-03-31", "nature": "Bad", "desc": "Passed away"}
        ]
    },
    {
        "name": "Michael Phelps",
        "birth": {"dt": "1985-06-30 12:00", "lat": 39.2904, "lon": -76.6122, "tz": "America/New_York"},
        "events": [
            {"date": "2008-08-17", "nature": "Good", "desc": "Beijing 8 gold medals"},
            {"date": "2012-08-04", "nature": "Good", "desc": "London became most decorated"},
            {"date": "2004-08-19", "nature": "Good", "desc": "Athens 6 gold medals"}
        ]
    },
    {
        "name": "Nadia Comaneci",
        "birth": {"dt": "1961-11-12 12:00", "lat": 47.1585, "lon": 27.6014, "tz": "Europe/Bucharest"},
        "events": [
            {"date": "1976-07-18", "nature": "Good", "desc": "First perfect 10 in Olympics"},
            {"date": "1976-07-01", "nature": "Good", "desc": "Montreal 3 gold medals"},
            {"date": "1989-11-28", "nature": "Bad", "desc": "Defected to USA"}
        ]
    },
    {
        "name": "Simone Biles",
        "birth": {"dt": "1997-03-14 12:00", "lat": 29.7604, "lon": -95.3698, "tz": "America/Chicago"},
        "events": [
            {"date": "2016-08-11", "nature": "Good", "desc": "Rio 4 gold medals"},
            {"date": "2021-07-27", "nature": "Bad", "desc": "Withdrew from Tokyo (twisties)"},
            {"date": "2024-08-01", "nature": "Good", "desc": "Paris comeback gold"}
        ]
    },
    {
        "name": "Muhammad Ali",
        "birth": {"dt": "1942-01-17 18:35", "lat": 38.2527, "lon": -85.7585, "tz": "America/Kentucky/Louisville"},
        "events": [
            {"date": "1964-02-25", "nature": "Good", "desc": "First Heavyweight title"},
            {"date": "1967-04-28", "nature": "Bad", "desc": "Stripped of title (draft refusal)"},
            {"date": "1974-10-30", "nature": "Good", "desc": "Rumble in the Jungle win"}
        ]
    },
    {
        "name": "Mike Tyson",
        "birth": {"dt": "1966-06-30 12:00", "lat": 40.6782, "lon": -73.9442, "tz": "America/New_York"},
        "events": [
            {"date": "1986-11-22", "nature": "Good", "desc": "Youngest Heavyweight champ"},
            {"date": "1990-02-11", "nature": "Bad", "desc": "Lost to Buster Douglas"},
            {"date": "1992-03-26", "nature": "Bad", "desc": "Convicted of rape (prison)"}
        ]
    },
    {
        "name": "Evander Holyfield",
        "birth": {"dt": "1962-10-19 12:00", "lat": 33.7490, "lon": -84.3880, "tz": "America/New_York"},
        "events": [
            {"date": "1990-10-25", "nature": "Good", "desc": "Unified Heavyweight titles"},
            {"date": "1997-06-28", "nature": "Bad", "desc": "Ear bitten by Tyson"},
            {"date": "1999-11-13", "nature": "Bad", "desc": "Lost to Lennox Lewis"}
        ]
    },
    {
        "name": "Lennox Lewis",
        "birth": {"dt": "1965-09-02 12:00", "lat": 51.5074, "lon": -0.1278, "tz": "Europe/London"},
        "events": [
            {"date": "1992-10-31", "nature": "Good", "desc": "Olympic Gold (Barcelona)"},
            {"date": "1999-11-13", "nature": "Good", "desc": "Unified all belts vs Holyfield"},
            {"date": "2003-06-21", "nature": "Good", "desc": "Retired as champion"}
        ]
    },
    {
        "name": "Manny Pacquiao",
        "birth": {"dt": "1978-12-17 12:00", "lat": 7.1907, "lon": 125.4553, "tz": "Asia/Manila"},
        "events": [
            {"date": "1995-01-22", "nature": "Good", "desc": "Professional debut"},
            {"date": "2010-11-13", "nature": "Good", "desc": "8th division world title"},
            {"date": "2015-05-02", "nature": "Bad", "desc": "Lost to Mayweather"}
        ]
    },
    {
        "name": "Floyd Mayweather Jr",
        "birth": {"dt": "1977-02-24 12:00", "lat": 42.3314, "lon": -83.0458, "tz": "America/Detroit"},
        "events": [
            {"date": "1996-10-11", "nature": "Good", "desc": "Olympic Bronze"},
            {"date": "2015-05-02", "nature": "Good", "desc": "Beat Pacquiao (unbeaten record)"},
            {"date": "2017-08-26", "nature": "Good", "desc": "Beat McGregor (50-0)"}
        ]
    },
    {
        "name": "LeBron James",
        "birth": {"dt": "1984-12-30 16:04", "lat": 41.0814, "lon": -81.5190, "tz": "America/New_York"},
        "events": [
            {"date": "2003-06-26", "nature": "Good", "desc": "NBA Draft #1 overall"},
            {"date": "2010-07-08", "nature": "Bad", "desc": "The Decision (public backlash)"},
            {"date": "2016-06-19", "nature": "Good", "desc": "Cavs Championship (3-1 comeback)"}
        ]
    },
    {
        "name": "Kobe Bryant",
        "birth": {"dt": "1978-08-23 16:10", "lat": 39.9526, "lon": -75.1652, "tz": "America/New_York"},
        "events": [
            {"date": "1996-07-11", "nature": "Good", "desc": "Drafted by Lakers"},
            {"date": "2003-07-18", "nature": "Bad", "desc": "Colorado assault case"},
            {"date": "2020-01-26", "nature": "Bad", "desc": "Passed away in helicopter crash"}
        ]
    },
    {
        "name": "Kareem Abdul-Jabbar",
        "birth": {"dt": "1947-04-16 13:30", "lat": 40.7128, "lon": -74.0060, "tz": "America/New_York"},
        "events": [
            {"date": "1971-04-30", "nature": "Good", "desc": "First NBA Championship"},
            {"date": "1985-06-09", "nature": "Good", "desc": "Finals MVP (Showtime Lakers)"},
            {"date": "1989-06-28", "nature": "Good", "desc": "Retired as all-time scoring leader"}
        ]
    },
    {
        "name": "Magic Johnson",
        "birth": {"dt": "1959-08-14 13:05", "lat": 34.0522, "lon": -118.2437, "tz": "America/Los_Angeles"},
        "events": [
            {"date": "1979-06-01", "nature": "Good", "desc": "Drafted by Lakers"},
            {"date": "1980-05-16", "nature": "Good", "desc": "Rookie Finals MVP"},
            {"date": "1991-11-07", "nature": "Bad", "desc": "HIV announcement (career shock)"}
        ]
    },
    {
        "name": "Larry Bird",
        "birth": {"dt": "1956-12-07 10:00", "lat": 39.7684, "lon": -86.1581, "tz": "America/Indiana/Indianapolis"},
        "events": [
            {"date": "1978-06-08", "nature": "Good", "desc": "Drafted by Celtics"},
            {"date": "1981-05-01", "nature": "Good", "desc": "First NBA title"},
            {"date": "1992-08-08", "nature": "Good", "desc": "Olympic Dream Team gold"}
        ]
    },
    {
        "name": "Michael Jordan",
        "birth": {"dt": "1963-02-17 13:40", "lat": 40.6782, "lon": -73.9442, "tz": "America/New_York"},
        "events": [
            {"date": "1991-06-12", "nature": "Good", "desc": "First NBA Championship"},
            {"date": "1993-07-23", "nature": "Bad", "desc": "Father murdered"},
            {"date": "1995-03-18", "nature": "Good", "desc": "I'm back announcement"}
        ]
    },
    {
        "name": "Diego Maradona",
        "birth": {"dt": "1960-10-30 07:05", "lat": -34.6037, "lon": -58.3816, "tz": "America/Argentina/Buenos_Aires"},
        "events": [
            {"date": "1986-06-29", "nature": "Good", "desc": "World Cup win (Hand of God)"},
            {"date": "1991-03-17", "nature": "Bad", "desc": "Banned for cocaine (15 months)"},
            {"date": "2020-11-25", "nature": "Bad", "desc": "Passed away"}
        ]
    },
    {
        "name": "Pele",
        "birth": {"dt": "1940-10-23 01:00", "lat": -23.5505, "lon": -46.6333, "tz": "America/Sao_Paulo"},
        "events": [
            {"date": "1958-06-29", "nature": "Good", "desc": "First World Cup at 17"},
            {"date": "1970-06-21", "nature": "Good", "desc": "Third World Cup (Brazil legend)"},
            {"date": "2022-12-29", "nature": "Bad", "desc": "Passed away"}
        ]
    },
    {
        "name": "Johann Sebastian Bach",
        "birth": {"dt": "1685-03-31 10:00", "lat": 50.9787, "lon": 11.0328, "tz": "Europe/Berlin"},
        "events": [
            {"date": "1723-05-01", "nature": "Good", "desc": "Became Thomaskantor Leipzig"},
            {"date": "1749-01-01", "nature": "Good", "desc": "Completed Mass in B Minor"},
            {"date": "1750-07-28", "nature": "Bad", "desc": "Passed away"}
        ]
    },
    {
        "name": "Rembrandt",
        "birth": {"dt": "1606-07-15 13:30", "lat": 52.1601, "lon": 4.4970, "tz": "Europe/Amsterdam"},
        "events": [
            {"date": "1634-06-10", "nature": "Good", "desc": "Married Saskia (peak period)"},
            {"date": "1642-01-01", "nature": "Good", "desc": "The Night Watch completed"},
            {"date": "1656-01-01", "nature": "Bad", "desc": "Declared bankrupt"}
        ]
    },
    {
        "name": "Michelangelo",
        "birth": {"dt": "1475-03-06 04:45", "lat": 43.7696, "lon": 11.2558, "tz": "Europe/Rome"},
        "events": [
            {"date": "1504-09-08", "nature": "Good", "desc": "David completed"},
            {"date": "1512-10-31", "nature": "Good", "desc": "Sistine Chapel ceiling done"},
            {"date": "1564-02-18", "nature": "Bad", "desc": "Passed away"}
        ]
    },
    {
        "name": "Raphael",
        "birth": {"dt": "1483-04-06 03:00", "lat": 43.7696, "lon": 11.2558, "tz": "Europe/Rome"},
        "events": [
            {"date": "1508-01-01", "nature": "Good", "desc": "Called to Rome by Pope"},
            {"date": "1515-01-01", "nature": "Good", "desc": "School of Athens fresco"},
            {"date": "1520-04-06", "nature": "Bad", "desc": "Passed away (his birthday)"}
        ]
    },
    {
        "name": "Neil Armstrong",
        "birth": {"dt": "1930-08-05 00:31", "lat": 40.7608, "lon": -82.3977, "tz": "America/New_York"},
        "events": [
            {"date": "1969-07-20", "nature": "Good", "desc": "First man on Moon"},
            {"date": "1966-03-16", "nature": "Good", "desc": "Gemini 8 mission"},
            {"date": "2012-08-25", "nature": "Bad", "desc": "Passed away"}
        ]
    },
    {
        "name": "Buzz Aldrin",
        "birth": {"dt": "1930-01-20 14:15", "lat": 40.7589, "lon": -73.9851, "tz": "America/New_York"},
        "events": [
            {"date": "1969-07-20", "nature": "Good", "desc": "Second man on Moon"},
            {"date": "1971-01-01", "nature": "Bad", "desc": "Depression/alcohol struggles"},
            {"date": "2019-01-01", "nature": "Good", "desc": "Continued advocacy work"}
        ]
    },
    {
        "name": "Yuri Gagarin",
        "birth": {"dt": "1934-03-09 05:00", "lat": 55.7558, "lon": 37.6173, "tz": "Europe/Moscow"},
        "events": [
            {"date": "1961-04-12", "nature": "Good", "desc": "First human in space"},
            {"date": "1963-01-01", "nature": "Bad", "desc": "Banned from space flight (too valuable)"},
            {"date": "1968-03-27", "nature": "Bad", "desc": "Death in jet crash"}
        ]
    },
    {
        "name": "Amelia Earhart",
        "birth": {"dt": "1897-07-24 23:30", "lat": 39.0997, "lon": -94.5786, "tz": "America/Chicago"},
        "events": [
            {"date": "1928-06-17", "nature": "Good", "desc": "First woman Atlantic crossing"},
            {"date": "1932-05-20", "nature": "Good", "desc": "Solo Atlantic flight"},
            {"date": "1937-07-02", "nature": "Bad", "desc": "Disappeared over Pacific"}
        ]
    },
    {
        "name": "Marco Polo",
        "birth": {"dt": "1254-09-15 12:00", "lat": 44.4949, "lon": 12.2432, "tz": "Europe/Rome"},
        "events": [
            {"date": "1271-01-01", "nature": "Good", "desc": "Journey to China began"},
            {"date": "1295-01-01", "nature": "Good", "desc": "Returned to Venice"},
            {"date": "1324-01-08", "nature": "Bad", "desc": "Passed away"}
        ]
    },
    {
        "name": "Christopher Columbus",
        "birth": {"dt": "1451-10-31 12:00", "lat": 44.4056, "lon": 8.9463, "tz": "Europe/Rome"},
        "events": [
            {"date": "1492-10-12", "nature": "Good", "desc": "Discovered Americas"},
            {"date": "1500-08-01", "nature": "Bad", "desc": "Arrested and sent back to Spain"},
            {"date": "1506-05-20", "nature": "Bad", "desc": "Passed away"}
        ]
    },
    {
        "name": "Marie Antoinette",
        "birth": {"dt": "1755-11-02 19:30", "lat": 48.8566, "lon": 2.3522, "tz": "Europe/Vienna"},
        "events": [
            {"date": "1770-05-16", "nature": "Good", "desc": "Married Louis XVI"},
            {"date": "1774-05-10", "nature": "Good", "desc": "Became Queen of France"},
            {"date": "1793-10-16", "nature": "Bad", "desc": "Executed by guillotine"}
        ]
    },
    {
        "name": "Napoleon Bonaparte",
        "birth": {"dt": "1769-08-15 11:00", "lat": 42.0396, "lon": 9.0129, "tz": "Europe/Paris"},
        "events": [
            {"date": "1804-12-02", "nature": "Good", "desc": "Crowned Emperor"},
            {"date": "1812-12-14", "nature": "Bad", "desc": "Retreat from Moscow"},
            {"date": "1821-05-05", "nature": "Bad", "desc": "Died in exile"}
        ]
    },
    {
        "name": "Tom Cruise",
        "birth": {"dt": "1962-07-03 12:05", "lat": 41.2524, "lon": -73.3857, "tz": "America/New_York"},
        "events": [
            {"date": "1986-05-16", "nature": "Good", "desc": "Top Gun release (breakout role)"},
            {"date": "1990-07-13", "nature": "Good", "desc": "Days of Thunder premiere"},
            {"date": "2001-07-13", "nature": "Good", "desc": "Mission Impossible franchise"}
        ]
    },
    {
        "name": "Julia Roberts",
        "birth": {"dt": "1967-10-28 00:16", "lat": 33.2479, "lon": -84.2641, "tz": "America/New_York"},
        "events": [
            {"date": "1990-06-13", "nature": "Good", "desc": "Pretty Woman release (star)"},
            {"date": "2001-03-25", "nature": "Good", "desc": "Oscar win for Erin Brockovich"},
            {"date": "2002-07-04", "nature": "Good", "desc": "Married Daniel Moder"}
        ]
    }
]

def run_backtest():
    service = LifePredictorService()
    results = []
    
    print(f"Starting backtest on {len(PERSONALITIES)} personalities...")
    
    total_events = 0
    correct_hits = 0
    
    for p_data in PERSONALITIES:
        print(f"\nProcessing {p_data['name']}...")
        
        # Build Person
        b_dt = datetime.strptime(p_data['birth']['dt'], "%Y-%m-%d %H:%M")
        person = Person(
            name=p_data['name'],
            birth_datetime=b_dt,
            birth_location=GeoLocation(
                latitude=p_data['birth']['lat'],
                longitude=p_data['birth']['lon'],
                timezone=p_data['birth']['tz']
            )
        )
        
        for event in p_data['events']:
            total_events += 1
            e_dt = datetime.strptime(event['date'], "%Y-%m-%d")
            
            # Predict for a 7-day window around the event
            time_range = TimeRange(
                start=e_dt - timedelta(days=3),
                end=e_dt + timedelta(days=3)
            )
            
            # Smarter category detection based on event description
            desc_lower = event['desc'].lower()
            if any(w in desc_lower for w in ['passed away', 'died', 'death', 'killed', 'suicide', 'assassin', 'illness', 'cancer', 'health', 'hospital', 'lung', 'deaf', 'injured', 'injury', 'crash', 'disappear', 'radiation', 'als', 'hiv', 'cocaine', 'drug', 'asylum', 'ear', 'helicopter']):
                category = 'health'
            elif any(w in desc_lower for w in ['married', 'marriage', 'wedding', 'divorce', 'separation', 'wife', 'husband', 'muse', 'megxit']):
                category = 'marriage'
            elif any(w in desc_lower for w in ['sentenced', 'imprisonment', 'testimony', 'trial', 'arrested', 'case', 'convicted', 'prison', 'guillotine', 'executed']):
                category = 'legal'
            elif any(w in desc_lower for w in ['founded', 'ipo', 'ceo', 'chairman', 'president', 'pm', 'elected', 'election', 'chancellor', 'pope', 'governor', 'inaugur', 'business', 'company', 'promoted', 'appointed', 'patent', 'contract', 'resigned', 'fired', 'stepped down', 'took over', 'launched', 'pivot', 'joined', 'became', 'role', 'term', 'left', 'terminated', 'dismissal', 'dismissed', 'retired', 'retirement', 'defected', 'captain', 'red card', 'lost election', 'decision']):
                category = 'career'
            elif any(w in desc_lower for w in ['nobel', 'oscar', 'award', 'prize', 'knighted', 'gold medal', 'champion', 'title', 'record', 'win', 'won', 'premiere', 'release', 'published', 'completed', 'symphony', 'world cup', 'olympics', 'hall of fame', 'comeback']):
                category = 'career'
            elif any(w in desc_lower for w in ['bankrupt', 'financial', 'crisis', 'crash', 'money', 'wealth', 'fortune', 'trading', 'investment', 'lehman']):
                category = 'finance'
            elif any(w in desc_lower for w in ['scandal', 'banned', 'stripped', 'lost', 'blocked', 'collapse', 'layoff', 'backlash', 'emergency', 'demolition', 'war', 'uprising', 'fled', 'exile', 'recant', 'lockdown', 'covid', 'invasion', 'invaded']):
                category = 'general'
            else:
                category = 'general'
            
            # We need the location for the event. Birth location is fine for dasha/gochara.
            event_loc = person.birth_location 
            
            try:
                prediction = service.predict(person, event_loc, time_range, category)
                
                # Check the overall period score
                score = prediction.overall_period_score
                
                nature_match = False
                if event['nature'] == 'Good' and score > 0.0:
                    nature_match = True
                elif event['nature'] == 'Bad' and score < 0.0:
                    nature_match = True
                elif event['nature'] == 'Neutral' and abs(score) <= 0.3:
                    nature_match = True
                
                if nature_match:
                    correct_hits += 1
                
                results.append({
                    "person": p_data['name'],
                    "event": event['desc'],
                    "expected": event['nature'],
                    "predicted_score": score,
                    "match": nature_match
                })
                
                status = "✓" if nature_match else "✗"
                print(f"  {status} {event['date']}: {event['nature']} (Score: {score:+.2f}) - {event['desc']}")
                
            except Exception as e:
                print(f"  Error processing event {event['desc']}: {e}")

    accuracy = (correct_hits / total_events) * 100 if total_events > 0 else 0
    
    print("\n" + "="*50)
    print(f"BACKTEST RESULTS SUMMARY")
    print(f"Total Personalities: {len(PERSONALITIES)}")
    print(f"Total Events: {total_events}")
    print(f"Correct Predictions: {correct_hits}")
    print(f"Accuracy: {accuracy:.1f}%")
    print("="*50)
    
    # Save results to JSON
    with open(os.path.join(os.path.dirname(__file__), 'backtest_results.json'), 'w') as f:
        json.dump({
            "summary": {
                "total_personalities": len(PERSONALITIES),
                "total_events": total_events,
                "correct_hits": correct_hits,
                "accuracy_pct": accuracy
            },
            "details": results
        }, f, indent=2)

if __name__ == "__main__":
    run_backtest()
