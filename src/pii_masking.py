import pandas as pd


def mask_passengers(df):
    passengers = df

    # creating a copy for analytics
    passengers_analytics = passengers.copy()





    # masking last name to a last initial
    passengers_analytics['last_name'] = passengers_analytics['last_name'].apply(
        lambda x: (
            x[0] + '.'
            if pd.notna(x) and len(str(x)) > 0
            else x
        )
    )


    # masking email
    passengers_analytics['email'] = passengers_analytics['email'].apply(
        lambda x: (
            x[0] + '****' + x[x.index('@'):]
            if pd.notna(x) and '@' in x
            else x
        )
    )


    # masking phone number
    passengers_analytics['phone'] = passengers_analytics['phone'].apply(
        lambda x: (
            '******' + str(x)[-4:]
            if pd.notna(x)
            else x
        )
    )


    # masking Aadhaar number
    passengers_analytics['aadhaar_id'] = passengers_analytics['aadhaar_id'].apply(
        lambda x: (
            'XXXXXXXX' + str(x)[-4:]
            if pd.notna(x)
            else x
        )
    )

    return passengers_analytics


def mask_bookings(df):
    bookings = df

    # creating a copy for analytics
    bookings_analytics = bookings.copy()


    # masking passport number
    bookings_analytics['passport_number'] = bookings_analytics['passport_number'].apply(
        lambda x: (
            'XXXX' + str(x)[-4:]
            if pd.notna(x)
            else x
        )
    )


    # masking emergency contact name
    bookings_analytics['emergency_contact_name'] = 'MASKED'


    # masking emergency contact phone
    bookings_analytics['emergency_contact_phone'] = (
        bookings_analytics['emergency_contact_phone'].apply(
            lambda x: (
                '******' + str(x)[-4:]
                if pd.notna(x)
                else x
            )
        )
    )

    return bookings_analytics
