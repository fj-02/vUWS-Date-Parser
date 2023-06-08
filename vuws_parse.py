from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime
import io, sys, re

# Gotten from vUWS site
SUBJECT_NAME_ID = "crumb_1"
PAGE_TITLE_ID = "pageTitleText"
PAGE_TITLE_NAME = "My Grades"
GRADES_TABLE_ID = "grades_wrapper"
GRADE_ROW_CLASS = "cell gradable"

def open_html():
	file_name = input("Enter HTML file name: ")
	if not file_name.endswith(".html"):
		print("Not a HTML file")
		exit(1)
	try:
		file = open(file_name, "r")
		return file
	except FileNotFoundError:
		print("File not found")
		exit(1)

def parse_file(file: io.TextIOWrapper) -> list:
	soup = BeautifulSoup(file.read(), "html.parser")

	subject_name = soup.find(id=SUBJECT_NAME_ID)
	if subject_name is None:
		print("Unable to find subject name")
		exit(2)
	subject_name = subject_name.string.strip()

	page_title = soup.find(id=PAGE_TITLE_ID).contents[1].string
	if page_title is None or page_title != PAGE_TITLE_NAME:
		print("HTML is not on My Grades")
		exit(3)

	grades_table = soup.find(id=GRADES_TABLE_ID).find_all(role="row")
	events = list()
	for grade in grades_table:
		grade_item = grade.find("div", class_=GRADE_ROW_CLASS)
		grade_name = grade_item.contents[1].string
		grade_due_date = grade_item.find("div", class_="activityType")

		if grade_due_date is None: # Some don't include Due date so ignore
			print(f"Skipped {grade_name} (No due date)", file=sys.stderr)
			continue

		grade_due_date = grade_due_date.string.strip()[5:] # Remove 'Due: '
		grade_category = grade_item.find("div", class_="itemCat")
		grade_category = "(No Description)" if grade_category is None else grade_category.string

		events.append(dict(name=grade_name, due_date=grade_due_date, desc=grade_category))

	return subject_name, events

def safe_file_name(name):
	name = re.sub(r'[<>:"/\\|?*]', "", name)
	name = name.strip()
	name = name[:255]
	return name

def gen_dates(subject_name: str, events: list):
	cal = Calendar()
	for event in events:
		cal_event = Event()
		cal_event.name = subject_name

		due_date = datetime.strptime(event["due_date"], "%d/%m/%Y")
		due_date = due_date.replace(year=datetime.now().year) # Force it to be current year
		due_date = due_date.strftime("%Y/%m/%d")
		cal_event.begin = due_date
		cal_event.make_all_day()

		cal_event.location = "vUWS"

		cal_event.description = f"{event['name']} - {event['desc']}"

		cal.events.add(cal_event)

	file_name = f"{safe_file_name(subject_name)}.ics"
	with open(file_name, "w") as file:
		file.writelines(cal.serialize_iter())
	print(f"{file_name} saved")

if __name__ == "__main__":
	try:
		file = open_html()
		subject_name, events = parse_file(file)
		file.close()
		gen_dates(subject_name, events)
	except KeyboardInterrupt:
		print("\nExiting")