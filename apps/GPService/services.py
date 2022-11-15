from datetime import datetime

def check_meeting_slot_time(starting_time, ending_time):
    start_time = datetime.strptime(starting_time.isoformat(), "%H:%M:%S")
    end_time = datetime.strptime(ending_time.isoformat(), "%H:%M:%S")
    delta = end_time - start_time
    seconds = delta.total_seconds()
    minutes = seconds / 60
    if minutes == 15:
        return True
    else:
        return False
