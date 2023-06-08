# vUWS Date Parser
Get an importable calendar file of assessment dates for a subject on vUWS.

Dates are extracted from the 'My Grades' section of a subject

## Install dependencies
```sh
pip install -r requirements.txt
```
## How to use
1. On vUWS go to a subject and visit the 'My Grades' section.
2. Right click and download the page as a HTML file.
3. Run the script: `python vuws_parse.py`
4. Input the name of the HTML file.
5. The script will output a `.ics` file, import that to your calendar.
6. Done!