""" To Do
 - Pull info from JIRA tickets
 - Return responses that are more informative
"""

""" Change Log
date : summary of changes
    user email
        - details or references used
    
04/08/2020: Filling in an entire month, check to see if days are not filled and summarizing current entries for a date range
        - https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases

31/07/2020: Creating base classes and models for GET and POST requests
        - https://github.com/tick/tick-api/blob/master/sections/entries.md
"""
import json
from pprint import PrettyPrinter
from tickspot.settings import env
from tickspot.net.network import Entry, Project, Task, Authorize

def current_date():
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%d")

class TickSpot(Authorize):
    def __init__(self, username: str, password: str):
        super(TickSpot, self).__init__(username, password)
        self.entry = Entry(self.sub_id, self.token)
        self.task = Task(self.sub_id, self.token)
        self.project = Project(self.sub_id, self.token)
        self.pp = PrettyPrinter(indent=4)

    def list_tasks(self, project_id: int):
        self.pp.pprint(self.task.list(project_id=project_id))

    def list_projects(self):
        self.pp.pprint(self.project.list())

    def list_entries(self, project_id: int, start_date: str, end_date: str):
        self.pp.pprint(
            self.entry.list(project_id=project_id, start_date=start_date, end_date=end_date)
        )
    
    def list_entries_today(self, project_id: int):
        entries = self.entry.list(project_id=project_id, start_date=current_date(), end_date=current_date())
        self.pp.pprint(
            entries
        )
        hours = 0
        for entry in entries:
            hours += entry.get("hours")
        print(f"Hours: {hours}")

    def create_entry(self, project_id: int, task_id: int, hours: float, date: str, note: str):
        self.entry.post(
            {
                "project_id": project_id,
                "hours": hours,
                "date": date,
                "task_id": task_id,
                "notes": note,
            }
        )


def fetch(args):
    tickspot = TickSpot(
        username=env.get("TICKSPOT_USERNAME"), password=env.get("TICKSPOT_PASSWORD")
    )
    if args.category == "project":
        tickspot.list_projects()
    elif args.category == "task":
        tickspot.list_tasks(project_id=args.project)
    elif args.category == "today":
        tickspot.list_entries_today(project_id=args.project)
    else:
        raise ValueError("Only project and task are supported for list.")


def create(args):
    import holidays

    if args.vacation:
        dates = holidays.CountryHoliday(
            env.get("DATE_COUNTRY"), prov=env.get("DATE_PROVINCE"), state=env.get("DATE_STATE")
        )
        if args.date in dates:
            raise ValueError("Date occurs on a holiday.")

    tickspot = TickSpot(
        username=env.get("TICKSPOT_USERNAME"), password=env.get("TICKSPOT_PASSWORD")
    )
    tickspot.create_entry(
        project_id=args.project, task_id=args.task, hours=args.hours, date=args.date, note=None
    )

def start(args):
    import time
    import datetime
    start_time = time.time()
    if not args.project:
        raise ValueError("Require project")
    if not args.task:
        raise ValueError("Require task")
    input("Press Enter to stop")
    end_time = time.time()

    time_lapsed = end_time - start_time
    hours = time_lapsed/ 3600.0

    tickspot = TickSpot(
        username=env.get("TICKSPOT_USERNAME"), password=env.get("TICKSPOT_PASSWORD")
    )

    tickspot.create_entry(
        project_id=args.project, task_id=args.task, hours=hours, date=current_date(), note=args.message
    )
