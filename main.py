import streamlit as st
import pandas as pd

# Set page title
st.set_page_config(page_title="Lines Picked - CSV Parser")

st.title("Lines Picked")

# File uploader for CSV files
uploadFile = st.file_uploader("Upload a CSV file", type="csv")

if uploadFile:
    # Load CSV with semicolon delimiter
    dataFrame = pd.read_csv(uploadFile, delimiter=";")

    # Clean column names
    dataFrame.columns = dataFrame.columns.str.strip().str.replace('"', '')

    # Combine date and time into one datetime column
    dataFrame['Pick DateTime'] = pd.to_datetime(
        dataFrame['Pick Date'] + ' ' + dataFrame['Pick Time'],
        format='%m/%d/%Y %H:%M:%S'
    )

    # Get list of unique pick dates
    uniqueDates = dataFrame['Pick Date'].unique()

    # Shift filter function
    def filterByShift(shift, dateFilter=None):
        if shift == 'Dayshift':
            # 07:00 to 19:00 on a given day
            if dateFilter:
                shiftData = dataFrame[
                    (dataFrame['Pick Date'] == dateFilter) &
                    (dataFrame['Pick DateTime'].dt.hour >= 7) &
                    (dataFrame['Pick DateTime'].dt.hour < 19)
                ]
            else:
                shiftData = dataFrame[
                    (dataFrame['Pick DateTime'].dt.hour >= 7) &
                    (dataFrame['Pick DateTime'].dt.hour < 19)
                ]
            return shiftData

        elif shift == 'Nightshift':
            # 19:00 current day to 07:00 next day
            if not dateFilter:
                return pd.DataFrame()

            nightStart = pd.to_datetime(dateFilter + ' 19:00:00')
            nightEnd = nightStart + pd.Timedelta(hours=12)

            morningStart = pd.to_datetime(dateFilter + ' 00:00:00')
            morningEnd = pd.to_datetime(dateFilter + ' 07:00:00')

            morningOffPickers = dataFrame[
                (dataFrame['Pick DateTime'] >= morningStart) &
                (dataFrame['Pick DateTime'] < morningEnd)
            ]['Picked By'].unique()

            shiftData = dataFrame[
                (dataFrame['Pick DateTime'] >= nightStart) &
                (dataFrame['Pick DateTime'] < nightEnd) &
                (~dataFrame['Picked By'].isin(morningOffPickers))
            ]

            return shiftData

    # Shift selection buttons
    dayshiftButton = st.button("Show Dayshift (07:00 to 19:00)")
    nightshiftButton = st.button("Show Nightshift (19:00 to 07:00)")

    # Dayshift output
    if dayshiftButton:
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
            st.error('"Picked By" column not found in filtered data.')

    # Nightshift output
    if nightshiftButton:
        dateFilter = uniqueDates[0]
        filteredData = filterByShift('Nightshift', dateFilter)

        st.subheader(f"Nightshift Data (19:00 {dateFilter} to 07:00 next day)")

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
            st.error('"Picked By" column not found in filtered data.')

else:
    print("Upload a CSV file to begin.")
