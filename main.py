import sqlite3
import os
from datetime import datetime
import pygame
import time

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




def get_column_description(db_path, column_number):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Execute the query to fetch the description and prayer status based on column number
    cursor.execute("SELECT description, prayer FROM column_legend WHERE column = ?", (column_number,))
    
    # Fetch the result
    result = cursor.fetchone()
    
    # Close the connection
    conn.close()
    
    # Return the description and prayer status if found, otherwise return None and False
    if result:
        description, prayer_status = result
        return description, bool(prayer_status)
    else:
        return None, False

if __name__ == "__main__":

    # Ask the user which prayers to play the mp3 file for
    prayers_to_play = {
        "Fajr": False,
        "Sunrise": False,
        "Dhur": False,
        "Asr": False,
        "Maghrib": False,
        "Isha": False
    }

    for prayer in prayers_to_play.keys():
        response = input(f"Do you want to play the mp3 for {prayer}? (yes/no): ").strip().lower()
        if response == "yes":
            prayers_to_play[prayer] = True

    # Map prayer times to their names
    prayer_names = ["Fajr", "Sunrise", "Dhur", "Asr", "Maghrib", "Isha"]


    db_path = os.path.join(os.path.dirname(__file__), 'prayertimes.sqlite')
    # Get the current date and time
    while True:
       
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
                seconds_to_prayer = abs(diff.total_seconds())
                print(f"Seconds to prayer: {seconds_to_prayer}")

                break
            else :
                print(f"Seconds to prayer: {diff.total_seconds()}")
        
        if current_prayer_time:
            current_prayer_name = prayer_names[prayer_times_list.index(current_prayer_time)]
            if prayers_to_play[current_prayer_name]:
                print(f"Current prayer time: {current_prayer_time} ({current_prayer_name})")
                # Initialize pygame mixer
                pygame.mixer.init()

                # Load the athan.mp3 file
                pygame.mixer.music.load(os.path.join(os.path.dirname(__file__), 'athan.mp3'))

                # Play the athan.mp3 file
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
            else:
                print(f"Current prayer time: {current_prayer_time} ({current_prayer_name}), but mp3 is not set to play.")
        else:
            print("No current prayer time found.")
        time.sleep(1)
        