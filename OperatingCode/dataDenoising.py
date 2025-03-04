import pandas as pd
from pathlib import Path
import re

# Hard-coded output directory
OUTPUT_DIRECTORY = # Replace this with the full path to your desired output directory


# Function to extract the date from a filename
def extract_date_from_filename(filename):
    # Match YYYY-MM-DD or YYYYMMDD formats
    match = re.search(r'\d{4}-\d{2}-\d{2}|\d{8}', filename)
    if match:
        date_str = match.group(0)
        return date_str.replace("-", "")  # Remove hyphens if present (to normalize format)
    return "unknown_date"

# Function to process a single file
def process_file(filepath, grouped_directory, summed_directory):
    try:
        # Load the data from the CSV file
        df = pd.read_csv(filepath)

        # Ensure required columns exist
        required_columns = {'hostname', 'start_time', 'end_time', 'time_elapsed'}
        if not required_columns.issubset(df.columns):
            print(f"Skipping file {filepath}: Missing required columns.")
            return

        # Convert `start_time` and `end_time` to datetime.time objects
        df['start_time'] = pd.to_datetime(df['start_time'], format='%H:%M:%S').dt.time
        df['end_time'] = pd.to_datetime(df['end_time'], format='%H:%M:%S').dt.time

        # Sort the data by `start_time`
        df = df.sort_values(by=['start_time'])

        # Set time_tolerance to 2 seconds
        time_tolerance = pd.Timedelta(seconds=2)

        # Create an event group based on similarity between `end_time` and the next `start_time`
        event_group = [0]
        for i in range(1, len(df)):
            time_gap = pd.Timestamp.combine(pd.Timestamp.today(), df['start_time'].iloc[i]) - \
                       pd.Timestamp.combine(pd.Timestamp.today(), df['end_time'].iloc[i-1])
            if time_gap <= time_tolerance:
                event_group.append(event_group[-1])
            else:
                event_group.append(event_group[-1] + 1)

        df['event_group'] = event_group

        # Save the grouped data
        grouped_filepath = grouped_directory / f"{filepath.stem}_timesGrouped.csv"
        df.to_csv(grouped_filepath, index=False)
        print(f"Grouped file saved to: {grouped_filepath}")

        # Generate and save aggregated data
        aggregated = df.groupby('event_group').agg(
            hostname=('hostname', 'first'),
            date=('date', 'first'),
            start_time=('start_time', 'first'),
            end_time=('end_time', 'last'),
            time_elapsed=('time_elapsed', 'sum')
        ).reset_index(drop=True)

        summed_filepath = summed_directory / f"{filepath.stem}_timesSummed.csv"
        aggregated.to_csv(summed_filepath, index=False)
        print(f"Summed file saved to: {summed_filepath}")

    except Exception as e:
        print(f"Error processing file {filepath}: {e}")

# Main script
if __name__ == "__main__":
    # Prompt for the input directory
    input_directory = input("Enter the directory containing data files: ").strip()

    try:
        # Resolve input directory
        input_directory = Path(input_directory).resolve()

        # Ensure the input directory exists
        if not input_directory.exists() or not input_directory.is_dir():
            print("The specified input directory does not exist or is not valid.")
        else:
            # Process files one by one
            for filepath in input_directory.iterdir():
                if filepath.is_file() and filepath.suffix.lower() == ".csv":
                    print(f"Processing file: {filepath}")

                    # Extract date from filename
                    date_part = extract_date_from_filename(filepath.name)
                    if date_part == "unknown_date":
                        print(f"Warning: Could not extract date from {filepath.name}. Skipping file.")
                        continue

                    # Create output directories for this specific date
                    grouped_directory = OUTPUT_DIRECTORY / f"{date_part}_timesGrouped"
                    summed_directory = OUTPUT_DIRECTORY / f"{date_part}_timesSummed"

                    # Create directories
                    grouped_directory.mkdir(parents=True, exist_ok=True)
                    summed_directory.mkdir(parents=True, exist_ok=True)

                    # Process the file
                    process_file(filepath, grouped_directory, summed_directory)

            print("\nAll files processed successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")
