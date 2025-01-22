import sqlite3
import os
from datetime import datetime
import pygame
import time
import psutil

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
    # Check if the script is already running
    script_name = os.path.basename(__file__)
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        if proc.info['name'] == 'python' or proc.info['name'] == 'python3':
            if len(proc.info['cmdline']) > 1 and script_name in proc.info['cmdline'][1]:
                if proc.info['pid'] != os.getpid():
                    print("Script is already running. Exiting.")
                    exit()
    db_path = os.path.join(os.path.dirname(__file__), 'prayertimes.sqlite')
    # Ask the user which prayers to play the mp3 file for
    prayers_to_play = {}

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Execute the query to fetch the prayer names and their announce status
    cursor.execute("SELECT prayer, announce, audio FROM column_legend")
    
    # Fetch all the results
    records = cursor.fetchall()
    
    # Update the prayers_to_play dictionary based on the announce status
    for record in records:
        prayer, announce, audio = record
        prayers_to_play[prayer] = (bool(announce), audio)
    
    # Close the connection
    conn.close()
    


    
    # Get the current date and time       
    current_date = datetime.now()
    prayer_times = get_prayer_times_by_date(db_path, current_date)

    # Extract the prayer time from the record (assuming it's in the 2nd to 7th positions)
    prayer_times_list = prayer_times[2:8]
    
    # Get the current time
    current_time = current_date.time()
    current_prayer_time = None
    # Calculate the difference between current time and each prayer time
    time_differences = []
    for prayer_time_str in prayer_times_list:
        prayer_time = datetime.strptime(prayer_time_str, '%I:%M %p').time()
        difference = datetime.combine(current_date, prayer_time) - datetime.combine(current_date, current_time)
        time_differences.append(difference)
    # Display the prayers for the day with time differences to the nearest second
    for prayer_name, prayer_time_str, time_diff in zip(prayers_to_play.keys(), prayer_times_list, time_differences):
        # Convert time difference to total seconds
        total_seconds = int(time_diff.total_seconds())
        # Calculate hours, minutes, and seconds
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        play_status, audio_file = prayers_to_play[prayer_name]
        play_status_str = "Yes" if play_status else "No"
        # Find the current prayer time (less than 1 minute past)
        if play_status and abs(total_seconds) <= 60:
            current_prayer_time = (prayer_name, audio_file)
        print(f"{prayer_name:<10} | {prayer_time_str:<8} | {total_seconds:>5} seconds | Play: {play_status_str:<3} | Audio: {audio_file}")
    
    if current_prayer_time:
        current_prayer_audio = current_prayer_time[1]
        current_prayer_name  = current_prayer_time[0]
        if prayers_to_play[current_prayer_name]:
            print(f"Current prayer time: {current_prayer_name} ({current_prayer_audio})")
            # Initialize pygame mixer
            pygame.mixer.init()

            # Load the athan.mp3 file
            athan_path = os.path.join(os.path.dirname(__file__), current_prayer_audio)
            athan_sound = pygame.mixer.Sound(athan_path)
            pygame.mixer.music.load(athan_path)

            # Play the athan.mp3 file
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
                # Get the current position of the audio file
                current_position = pygame.mixer.music.get_pos() / 1000  # Convert milliseconds to seconds
                # Calculate the remaining time and progress percentage
                remaining_time = athan_sound.get_length() - current_position
                progress_percentage = (current_position / athan_sound.get_length()) * 100
                
                # Calculate minutes and seconds for remaining time
                minutes, seconds = divmod(int(remaining_time), 60)
                
                # Create a visual representation of the progress bar
                progress_bar_length = 50  # Length of the progress bar in characters
                filled_length = int(progress_bar_length * progress_percentage // 100)
                bar = '█' * filled_length + '-' * (progress_bar_length - filled_length)
                
                # Print the progress bar and remaining time
                print(f"Time remaining: {minutes}:{seconds:02d} | Progress: |{bar}|", end='\r')
        else:
            print(f"Current prayer time: {current_prayer_time} ({current_prayer_name}), but mp3 is not set to play.")
    else:
        print("No current prayer time found.")
    time.sleep(1)
        