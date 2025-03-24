import os
import re
import chardet
from lxml import etree
import shutil
from datetime import datetime, timedelta
import time
import xml.etree.ElementTree as ET



def format_duration(seconds: float) -> str:
    """Convert duration in seconds to HH:MM:SS format."""
    duration_td = timedelta(seconds=seconds)

    hours, remainder = divmod(duration_td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return f"{hours:02}:{minutes:02}:{seconds:02}"

# Read data from the Notepad file
notepad_file_path = r"C:\Tools\Amigo Automation\list.txt"  # Replace with your actual file path
with open(notepad_file_path, "r") as notepad_file:
    lines = notepad_file.readlines()

# Iterate over each line in the Notepad file
for line in lines:
    # Split the line into parts
    parts = line.strip().split(',')

    # Extract data from parts
    folder_path = parts[0]
    input_date_str = parts[1]
    time_slot_str = parts[2]

    # Combine both into a single datetime string in the correct format
    combined_datetime_str = f"{input_date_str} {time_slot_str}"

    # Convert date and time strings to datetime objects
    try:
        # Convert to datetime object (proper format)
        input_datetime = datetime.strptime(combined_datetime_str, "%d-%m-%Y %I:%M:%S %p") ## fetching to xml as ScheduleDate
        
    except ValueError:
        print("Invalid date or time format in the Notepad file.")
        exit()

    # Iterate over each file in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(('.xml', '.txt')):
            file_path = os.path.join(folder_path, filename)
            file_name = os.path.splitext(filename)[0]
            
            # Step 2: Detect the encoding of the file using chardet
            with open(file_path, 'rb') as file:
                raw_data = file.read()
                result = chardet.detect(raw_data)
                encoding = result['encoding']
            # Read XML data
            with open(file_path, 'r', encoding=encoding) as file:
                xml_data = file.read()

            # Step 4: Remove any null characters or non-printable characters
            xml_data = re.sub(r'[\x00-\x1F\x7F]', '', xml_data)


            try:
                root = etree.fromstring(xml_data)
                file_count = len(root.findall("./file"))  ## fetching to xml as count Tag
                # Extract and sum the duration values
                total_duration = sum(float(info.get("duration", 0)) for info in root.findall(".//info"))
                formatted_duration = format_duration(total_duration)  # fetching to xml as duration  Tag
                # Calcualting End Time
                end_datetime = input_datetime + timedelta(seconds=total_duration)
                #print("<ScheduleTime>" + input_datetime.strftime("%d-%m-%Y %H:%M:%S") + "</ScheduleTime>")
                #print("<SchListPath>" + file_path + "</SchListPath>")
                #print("<schListName>" + file_name + "</schListName>")
                #print("<schListfilesCount>" + str(file_count) + "</schListfilesCount>")
                #print("<schListDuration>" + formatted_duration + "</schListDuration>")
                #print("<SchListEndTime>" + end_datetime.strftime("%d-%m-%Y %H:%M:%S") + "</SchListEndTime>")
                

                # Define the XML file path
                xml_file = r"C:\Tools\Amigo Automation\Channel1.xml"  # Change this to your actual file path

                # Read and parse the XML file
                tree = etree.parse(xml_file)
                root1 = tree.getroot()

                # Create a new Record element with an incremented ID
                new_record_id = str(len(root1.findall("Record")))  # Get the next ID
                new_record = etree.Element("Record", ID=new_record_id)

                # Add child elements
                etree.SubElement(new_record, "ScheduleTime").text = input_datetime.strftime("%d-%m-%Y %I:%M:%S %p")
                etree.SubElement(new_record, "SchListPath").text = file_path
                etree.SubElement(new_record, "schListName").text = file_name
                etree.SubElement(new_record, "schListfilesCount").text =  str(file_count)
                etree.SubElement(new_record, "schListDuration").text = formatted_duration
                etree.SubElement(new_record, "SchListEndTime").text = end_datetime.strftime("%d-%m-%Y %I:%M:%S %p")

                # Append the new record to the root element
                root1.append(new_record)

                # Write the updated XML back to the file with proper formatting
                with open(xml_file, "wb") as f:
                    tree.write(f, encoding="utf-8", xml_declaration=True, pretty_print=True)

                print(f"New record added with ID {new_record_id} and saved to {xml_file}")
                

            except etree.XMLSyntaxError as e:
                print(f"XML syntax error in file {filename}: {e}")




        input_datetime += timedelta(days=1)
        print(input_datetime)