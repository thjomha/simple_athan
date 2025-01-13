import sqlite3
import os
from datetime import datetime
def display_first_5_records(db_path):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Execute the query to fetch the first 5 records from the times table
    cursor.execute("SELECT * FROM times LIMIT 5")
    
    # Fetch all the results
    records = cursor.fetchall()
    
    # Display the records
    for record in records:
        print(record)
    
    # Close the connection
    conn.close()
def get_prayer_times_by_date(db_path, current_date):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Extract month and day from the current date
    month = current_date.month
    day = current_date.day
    
    # Execute the query to fetch the record based on month and day
    cursor.execute("SELECT * FROM times WHERE month = ? AND day = ?", (month, day))
    
    # Fetch the result
    record = cursor.fetchone()
    
    # Display the record
    if record:
        print(record)
        return record;
    else:
        print("No record found for the given date.")
    
    # Close the connection
    conn.close()
if __name__ == "__main__":
    db_path = os.path.join(os.path.dirname(__file__), 'prayertimes.sqlite')
    # Get the current date and time
    current_date = datetime.now()
    prayer_times = get_prayer_times_by_date(db_path, current_date)

    # Extract the prayer time from the record (assuming it's in the 2nd to 7th positions)
    prayer_times_list = prayer_times[2:8]
    
    # Get the current time
    current_time = current_date.time()
    
    # Calculate the difference between current time and each prayer time
    time_differences = []
    for prayer_time_str in prayer_times_list:
        prayer_time = datetime.strptime(prayer_time_str, '%I:%M %p').time()
        difference = datetime.combine(current_date, prayer_time) - datetime.combine(current_date, current_time)
        time_differences.append(difference)
    # Find the current prayer time (less than 1 minute past)
    current_prayer_time = None
    for i, diff in enumerate(time_differences):
        if diff.total_seconds() > -60 and diff.total_seconds() <= 0:
            current_prayer_time = prayer_times_list[i]
            break
    
    if current_prayer_time:
        print(f"Current prayer time: {current_prayer_time}")
    else:
        print("No current prayer time found.")
    # Display the time differences
    for i, diff in enumerate(time_differences):
        print(f"Time difference for prayer {i+1}: {diff}")
