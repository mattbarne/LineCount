import streamlit as st
import pandas as pd

st.title("Lines Picked")

uploadFile = st.file_uploader("Upload a CSV file", type="csv")

if uploadFile:
    # Read the uploaded CSV
    dataFrame = pd.read_csv(uploadFile, delimiter=";")

    # Clean column names and "Picked By" column
    dataFrame.columns = dataFrame.columns.str.strip().str.replace('"', '')

    # Combine "Pick Date" and "Pick Time" into one datetime column
    dataFrame['Pick DateTime'] = pd.to_datetime(dataFrame['Pick Date'] + ' ' + dataFrame['Pick Time'], format='%m/%d/%Y %H:%M:%S')

    # Get the distinct dates in the data
    uniqueDates = dataFrame['Pick Date'].unique()

    # Define a function to filter by Day Shift or Night Shift
    def filterByShift(shift, dateFilter=None):
        if shift == 'Dayshift':
            # Day shift: 07:00 to 19:00
            if dateFilter:
                shiftData = dataFrame[(dataFrame['Pick Date'] == dateFilter) & 
                                       (dataFrame['Pick DateTime'].dt.hour >= 7) & 
                                       (dataFrame['Pick DateTime'].dt.hour < 19)]
            else:
                shiftData = dataFrame[(dataFrame['Pick DateTime'].dt.hour >= 7) & 
                                       (dataFrame['Pick DateTime'].dt.hour < 19)]
        elif shift == 'Nightshift':
            # Night shift: 19:00 to 07:00 (crosses midnight)
            if dateFilter:
                shiftData = dataFrame[(dataFrame['Pick Date'] == dateFilter) & 
                                       ((dataFrame['Pick DateTime'].dt.hour >= 19) | 
                                        (dataFrame['Pick DateTime'].dt.hour < 7))]
            else:
                shiftData = dataFrame[((dataFrame['Pick DateTime'].dt.hour >= 19) | 
                                       (dataFrame['Pick DateTime'].dt.hour < 7))]
        return shiftData

    # Create buttons for Dayshift and Nightshift selection
    dayshiftButton = st.button("Show Dayshift (07:00 to 19:00)")
    nightshiftButton = st.button("Show Nightshift (19:00 to 07:00)")

    # Display the filtered data based on button selection
    if dayshiftButton:
        if len(uniqueDates) == 1:
            dateFilter = uniqueDates[0]
        else:
            dateFilter = uniqueDates[0]

        filteredData = filterByShift('Dayshift', dateFilter)
        st.subheader(f"Dayshift Data (07:00 to 19:00) for {dateFilter}")

        if 'Picked By' in filteredData.columns:
            filteredData['Picked By'] = filteredData['Picked By'].astype(str).str.strip().str.replace('"', '')
            pickedCount = filteredData['Picked By'].value_counts().reset_index()
            pickedCount.columns = ['Picked By', 'Total Picked']

            countSorted = pickedCount.sort_values(by='Total Picked', ascending=False)

            totalPicked = countSorted['Total Picked'].sum()
            summaryRow = pd.DataFrame([{'Picked By': 'Total', 'Total Picked': totalPicked}])
            countSorted = pd.concat([countSorted, summaryRow], ignore_index=True)

            st.dataframe(countSorted)
        else:
            st.error('"Picked by" column not found in filtered data.')

    if nightshiftButton:
        filteredData = filterByShift('Nightshift')
        st.subheader(f"Nightshift Data (19:00 to 07:00)")

        if 'Picked By' in filteredData.columns:
            filteredData['Picked By'] = filteredData['Picked By'].astype(str).str.strip().str.replace('"', '')
            pickedCount = filteredData['Picked By'].value_counts().reset_index()
            pickedCount.columns = ['Picked By', 'Total Picked']

            countSorted = pickedCount.sort_values(by='Total Picked', ascending=False)

            totalPicked = countSorted['Total Picked'].sum()
            summaryRow = pd.DataFrame([{'Picked By': 'Total', 'Total Picked': totalPicked}])
            countSorted = pd.concat([countSorted, summaryRow], ignore_index=True)

            st.dataframe(countSorted)
        else:
            st.error('"Picked by" column not found in filtered data.')

else:
    print("Upload a CSV file to begin.")
