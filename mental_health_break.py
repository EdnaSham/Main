import requests, config
import os, time
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
from google.auth.transport.requests import Request
import pickle, pytz
from datetime import datetime, timedelta, timezone
from plyer import notification

# Global variable to track the last break time
last_break_time_morning = None
last_break_time_afternoon = None

def authenticate_calendar_api():
    creds = None #creds object initialization
    # The token.pickle stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                config.CLIENT_SECRET_FILE, config.SCOPES)
            creds = flow.run_local_server(port=8080)
        
        # Save the credentials for future runs
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # Build the Calendar API service: you can use "https://www.googleapis.com/calendar/v3" but The googleapiclient.discovery.build method simplifies this interaction by abstracting the low-level details like: headers,Building proper HTTP requests, handling authentication, Structuring requests and responses into Python objects, making them easier to work with, etc.
    service = googleapiclient.discovery.build('calendar', 'v3', credentials=creds)
    return service

def is_within_working_hours():
    now = datetime.now()
    start_time = now.replace(hour=9, minute=0, second=0, microsecond=0).time()
    end_time = now.replace(hour=16, minute=30, second=0, microsecond=0).time()
    current_time = now.time()
    current_day = now.weekday()

    if start_time <= current_time <= end_time and current_day < 5:
        return True
    return False

def get_calendar_events():
    service = authenticate_calendar_api()  # Authenticate and get the API service
    global last_break_time

    calendar = service.calendars().get(calendarId='primary').execute()
    user_timezone = calendar['timeZone']
    tz = pytz.timezone(user_timezone)

    current_time = datetime.now(tz)
    current_time_str = current_time.isoformat()

    time_max = current_time + timedelta(hours=1.5)
    time_max_str = time_max.isoformat()

    try:
        events_result = service.events().list(calendarId='primary', timeMin=current_time_str, timeMax=time_max_str, singleEvents=True,
        orderBy='startTime', timeZone=user_timezone).execute()
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

    events = events_result.get('items', [])

    if not events:
        print("No events were found")
        return []  # Return empty list for consistency

    for event in events:
        start_time = event['start'].get('dateTime', event['start'].get('date'))
        print(f"Title: {event['summary']} at {start_time} ({user_timezone})")
        
    return events

def is_in_meeting():
    """Check if the user is in a meeting based on the current time."""
    events = get_calendar_events()  # Fetch current events

    current_time = datetime.now()
    for event in events:
        start_time = datetime.fromisoformat(event['start'].get('dateTime'))
        end_time = datetime.fromisoformat(event['end'].get('dateTime'))
        if start_time <= current_time <= end_time:
            print(f"User is currently in a meeting: {event['summary']}")
            return True

    print("No meetings found.")
    return False

def suggest_break():
    notification.notify(
        title="Reminder: Take a Break",
        message="You've been working hard! Time to take a quick break.",
        timeout=20  # The notification will disappear after 30 seconds
    )

def check_for_break():
    global last_break_time_morning, last_break_time_afternoon
    events = get_calendar_events()  # Fetch current events
    current_time = datetime.now()

    if current_time.weekday() < 5:  # Check if it's Monday to Friday (0 = Monday, 4 = Friday)
        # Check if it's a suitable time for a break (before lunch, not during lunch)
        if datetime.strptime("09:00", "%H:%M").time() <= current_time.time() < datetime.strptime("12:00", "%H:%M").time():
            if datetime.strptime("12:00", "%H:%M").time() <= current_time.time() < datetime.strptime("13:00", "%H:%M").time():
                return False  # Don't suggest a break during lunch

            # Check if the user has been working for 1.5 hours since the last break
            if last_break_time_morning:
                time_since_last_break = current_time - last_break_time_morning
                if time_since_last_break >= timedelta(hours=1.5) and not is_in_meeting():
                    suggest_break()
                    last_break_time_morning = current_time  # Update after suggesting a break
                    return True
            else:
                # Ensure that at least 1.5 hours have passed since the start of the day
                work_start_time = datetime.strptime("09:00", "%H:%M").time()
                if current_time.time() >= (datetime.combine(current_time.date(), work_start_time) + timedelta(hours=1.5)).time():
                    if not is_in_meeting():
                        suggest_break()
                        last_break_time_morning = current_time  # Set the last break time to now
                        return True

        # Check if it's a suitable time for a break (after lunch)          
        if datetime.strptime("13:00", "%H:%M").time() <= current_time.time() < datetime.strptime("18:00", "%H:%M").time():
            # Check if the user has been working for 1.5 hours since the last break
            if last_break_time_afternoon:
                time_since_last_break = current_time - last_break_time_afternoon
                if time_since_last_break >= timedelta(hours=1.5) and not is_in_meeting():
                    suggest_break()
                    last_break_time_afternoon = current_time  # Update after suggesting a break
                    return True
            else:
                # Ensure that at least 1.5 hours have passed since the start of the day
                work_start_time = datetime.strptime("13:00", "%H:%M").time()
                if current_time.time() >= (datetime.combine(current_time.date(), work_start_time) + timedelta(hours=1.5)).time():
                    if not is_in_meeting():
                        suggest_break()
                        last_break_time_afternoon = current_time  # Set the last break time to now
                        return True

    return False


if __name__ == '__main__': #allows you to organize your Python code so that certain parts only run when the file is executed directly, not when it’s imported as a module. This is essential for making reusable modules and for running script-specific code like tests or example runs.
    
    while is_within_working_hours():
            check_for_break()
            time.sleep(10) #wait 15 min(900sec) then check back again
    