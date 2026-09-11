import pandas as pd


def clean_bookings(df):
    bookings = df

    # finding missing values

    print(bookings.isna().sum())


    # finding duplicates

    print(bookings.duplicated().sum())


    # checking duplicate booking_id

    print(
        bookings['booking_id']
        .duplicated(keep=False)
        .sum()
    )

    # print(
    #     bookings['booking_id'].value_counts()[
    #         bookings['booking_id'].value_counts() > 1
    #     ]
    # )

    # print(
    #     bookings[
    #         bookings['booking_id'].duplicated(keep=False)
    #     ].sort_values('booking_id')
    # )

    # booking_id should uniquely identify each booking


    # Removing duplicate booking records

    bookings_clean = bookings.drop_duplicates(
        subset=['booking_id'],
        keep='first'
    ).copy()

    print(
        bookings_clean['booking_id']
        .duplicated()
        .sum()
    )
    # 0 duplicate booking_ids


    # finding missing values again

    print(bookings_clean.isna().sum())


    # checking booking_id format

    print(
        bookings_clean['booking_id'].head()
    )

    invalid_booking_id = (
        ~bookings_clean['booking_id']
        .astype(str)
        .str.match(
            r'^B\d+$',
            na=False
        )
    )

    print(
        "Invalid booking_id values:",
        invalid_booking_id.sum()
    )


    # checking passenger_id format

    invalid_passenger_id = (
        ~bookings_clean['passenger_id']
        .astype(str)
        .str.match(
            r'^P\d+$',
            na=False
        )
    )

    print(
        "Invalid passenger_id values:",
        invalid_passenger_id.sum()
    )


    # checking flight_id format

    invalid_flight_id = (
        ~bookings_clean['flight_id']
        .astype(str)
        .str.match(
            r'^(6F|AI|SJ|UK)\d+$',
            na=False
        )
    )

    print(
        "Invalid flight_id values:",
        invalid_flight_id.sum()
    )


    # checking booking_date

    print(
        bookings_clean['booking_date'].dtype
    )

    print(
        bookings_clean['booking_date'].head(10)
    )


    # checking booking dates

    print(
        bookings_clean['booking_date'].describe()
    )


    # checking status values

    print(
        bookings_clean['status']
        .value_counts(dropna=False)
    )


    # checking passport numbers

    print(
        bookings_clean['passport_number'].head(10)
    )


    # checking seat numbers

    print(
        bookings_clean['seat_number']
        .value_counts(dropna=False)
    )


    # checking emergency contact name

    print(
        bookings_clean['emergency_contact_name']
        .head(10)
    )


    # checking emergency contact phone

    print(
        bookings_clean['emergency_contact_phone']
        .head(10)
    )


    # converting passport_number to string

    # passport_number is an identification value and not a numerical value,
    # so it should be stored as a string

    bookings_clean['passport_number'] = (
        bookings_clean['passport_number']
        .astype('string')
    )


    # converting seat_number to string

    bookings_clean['seat_number'] = (
        bookings_clean['seat_number']
        .astype('string')
    )


    # converting emergency contact phone to string

    bookings_clean['emergency_contact_phone'] = (
        bookings_clean['emergency_contact_phone']
        .astype('string')
    )


    # checking final missing values

    print(
        bookings_clean.isna().sum()
    )


    # checking duplicate booking_ids after cleaning

    print(
        bookings_clean['booking_id']
        .duplicated()
        .sum()
    )
    # 0


    # checking exact duplicate rows after cleaning

    print(
        bookings_clean.duplicated().sum()
    )
    # 0


    # checking final shape

    print(
        bookings_clean.shape
    )

    return bookings_clean
