from components import google_calendar


def get_next_event():
    gcal = google_calendar.GoogleCalendar()
    gcal.login()
    return gcal.get_next_event()
