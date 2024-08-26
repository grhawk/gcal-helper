import datetime
import logging
import re
from collections import defaultdict
from typing import DefaultDict

import pytz as pytz
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
log = logging.getLogger('main')

def run_example(creds, calendar_name):

    try:
        regex_category = re.compile(r'.*\[(.*)\].*')
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API



        print('Getting the upcoming 10 events')

        calendars = service.calendarList().list(showDeleted=True, showHidden=True).execute()

        for cal in calendars.get('items', []):
            log.debug(f"Found calendar: {cal}")
            if cal.get('summary', "") == calendar_name or cal.get('id', "") == calendar_name:
                calendar_id = cal['id']
                calendar_timezone = cal['timeZone']
                break
        else:
            raise RuntimeError("Calendar not found!")

        print(calendar_id)

        beginning_of_week, end_of_week = compute_actual_week_begin_and_end(calendar_timezone)

        events_result = service.events().list(calendarId=calendar_id, timeMin=beginning_of_week, timeMax=end_of_week,
                                              singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])
        categories = defaultdict(lambda: defaultdict(lambda: datetime.timedelta(0)))
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            categories[day]["FreeTime"] = datetime.timedelta(days=1)

        for event in events:
            beg = datetime.datetime.fromisoformat(event['start']['dateTime'])
            end = datetime.datetime.fromisoformat(event['end']['dateTime'])
            cat_match = regex_category.search(event['summary'])
            if cat_match is None:
                cat_match = "Unknown"
                print("Unknown task found:")
                print(event['summary'])
            else:
                cat_match = cat_match.group(1)
            category = cat_match
            categories[beg.strftime('%A')][category] += end-beg
            categories[beg.strftime('%A')]['FreeTime'] += beg-end

        service.close()

        if not events:
            print('No upcoming events found.')
            exit(0)

        # Prints the start and name of the next 10 events
        print(" - ", end="")
        for category in list(categories.values())[0]:
            print(category, "  ", end="")
        print()

        categories_per_week = defaultdict(lambda: datetime.timedelta(0))
        for day in categories:
            print(day, " ", end="")
            for category in categories[day]:
                categories_per_week[category] += categories[day][category]
                categories[day][category] = str((categories[day][category].days * 24 * 3600 + categories[day][category].seconds)//3600)+"h"+str((categories[day][category].seconds//60)%60)+"m"

        for k,v in categories_per_week.items():
            categories_per_week[k] = str((categories_per_week[k].days * 24 * 3600 + categories_per_week[k].seconds)//3600) + "h" + str((categories_per_week[k].seconds//60)%60) + "m"

        with open('result.html', 'w') as f:
            f.write(generate_html_with_css(categories))
            f.write(dict_to_html_columns(categories_per_week))

    except HttpError as error:
        print('An error occurred: %s' % error)


## TODO: Make sure the timezone is taken into account.
def compute_actual_week_begin_and_end(timezone):
    now = datetime.datetime.now()
    start = now - datetime.timedelta(days=now.isoweekday())
    end = start + datetime.timedelta(days=6)
    return start.isoformat("T") + "Z", end.isoformat("T") + "Z"


def generate_html_with_css(data):
    # Extract the keys from the first level dictionary
    headers = list(data.keys())

    # Extract the keys from the nested dictionaries
    inner_keys = set()
    for inner_dict in data.values():
        inner_keys.update(inner_dict.keys())

    # Create the table headers
    table_html = "<thead><tr>"
    table_html += "<th></th>"  # Empty header for the first column
    for header in headers:
        table_html += f"<th>{header}</th>"
    table_html += "</tr></thead>"

    # Create the table body
    table_html += "<tbody>"
    for inner_key in sorted(inner_keys):
        table_html += "<tr>"
        table_html += f"<td class='first-column'>{inner_key}</td>"  # First column with the inner key

        # Iterate through each dictionary and retrieve the corresponding value
        for header in headers:
            inner_dict = data.get(header, {})
            value = inner_dict.get(inner_key, "")
            table_html += f"<td>{value}</td>"
        table_html += "</tr>"
    table_html += "</tbody>"

    # Combine the table headers and body
    # embed calendar
    html = '<iframe src="https://calendar.google.com/calendar/embed?height=600&wkst=2&ctz=Europe%2FZurich&bgcolor=%23ffffff&showNav=0&showTitle=0&showDate=0&mode=WEEK&showTabs=0&showPrint=0&showCalendars=0&showTz=0&src=MDA5ODYzZWUwMzNkNDY3NTE1N2EzMGI5MWRlODAxZDMwNWNiNjA2NWZiZWQ4ODFjMTI1YWY0OTVjNzBiNjA4MUBncm91cC5jYWxlbmRhci5nb29nbGUuY29t&color=%23F4511E" style="border:solid 1px #777" width="800" height="600" frameborder="0" scrolling="no"></iframe>'

    html += f"<table class='calendar-table'>{table_html}</table>"

    # Define the CSS styles
    css = """
    <style>
        .calendar-table {
            width: 50%;
            border-collapse: collapse;
            font-family: Arial, sans-serif;
        }

        .calendar-table th {
            background-color: #f8f9fa;
            padding: 8px;
            text-align: left;
        }

        .calendar-table td {
            padding: 8px;
            border-bottom: 1px solid #e9ecef;
        }

        .first-column {
            font-weight: bold;
        }
    </style>
    """

    # Combine the HTML and CSS
    full_html = f"<html><head>{css}</head><body>{html}</body></html>"

    return full_html


def dict_to_html_columns(data):
    chart_script, chart_html = chart(data)
    html = "<html>"
    html += "<head>"
    html += chart_script
    html += "<style>"
    html += ".calendar-table {"
    html += "    width: 50%;"
    html += "    border-collapse: collapse;"
    html += "    font-family: Arial, sans-serif;"
    html += "}"
    html += ""
    html += ".calendar-table td {"
    html += "    padding: 8px;"
    html += "    border-bottom: 1px solid #e9ecef;"
    html += "    text-align: left;"
    html += "}"
    html += ""
    html += ".calendar-table td:first-child {"
    html += "    width: 120px;"
    html += "    font-weight: bold;"
    html += "}"
    html += ""
    html += ".calendar-table .separator-row td {"
    html += "    border: none;"
    html += "    padding: 0;"
    html += "    height: 10px;"
    html += "}"
    html += ".row {"
    html += "display: flex;"
    html += "}"
    html += ".column {"
    html += "flex: 50%;"
    html += "}"
    html += "</style>"
    html += "</head>"
    html += "<body>"
    html += "<br><h3>Values per week</h3>"
    html += "<div class=\"row\">"
    html += "<div class=\"column\">"
    html += "<table class='calendar-table'>"
    html += "<tr class='separator-row'><td colspan='2'></td></tr>"
    for key in sorted(data.keys()):
        value = data[key]
        html += "<tr>"
        html += f"<td><strong>{key}</strong></td>"
        html += f"<td>{value}</td>"
        html += "</tr>"
    html += "</table>"
    html += "</div>"
    html += "<div class=\"column\">"
    html += chart_html
    html += "</div>"
    html += "</div>"
    html += "</body>"
    html += "</html>"
    return html

def chart(data):

    script = """
    <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
    <script type="text/javascript">
      google.charts.load('current', {'packages':['corechart']});
      google.charts.setOnLoadCallback(drawChart);

      function drawChart() {

        var data = google.visualization.arrayToDataTable([
          ['Task', 'Hours per Day'],
        """

    for key, value in data.items():
        if key == "FreeTime":
            continue
        m = re.match('^(\d+)h(\d+)m$', value)
        seconds = int(m.group(1)) * 3600 + int(m.group(2)) * 60
        script += f"['{key}', {seconds}],"

    script += """
        ]);

        var options = {
          title: 'My Daily Activities'
        };

        var chart = new google.visualization.PieChart(document.getElementById('piechart'));

        chart.draw(data, options);
      }
    </script>
    """
    html = '<div id="piechart" style="width: 900px; height: 500px;"></div>'

    return script, html


