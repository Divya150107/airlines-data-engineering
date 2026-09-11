import pandas as pd


def clean_passengers(df):
    passengers = df

    # aadhaar_id is an all-digit column, so pandas infers it as int64 by default and
    # silently drops leading zeros (e.g. '056413953767' -> 56413953767, 11 digits).
    # The source .xlsx cells are already text with the leading zero intact (checked directly
    # with openpyxl), so forcing dtype=str here is a lossless fix, not a workaround.


    # finding missing values

    print(passengers.isna().sum())
    # from this we can understand that the column last_name has 10 missing values


    # finding duplicates

    print(passengers.duplicated().sum())
    # 0 exact duplicate rows


    # checking duplicate passenger_id

    print(
        passengers['passenger_id']
        .duplicated(keep=False)
        .sum()
    )

    # print(
    #     passengers['passenger_id']
    #     .value_counts()[
    #         passengers['passenger_id'].value_counts() > 1
    #     ]
    # )

    # print(
    #     passengers[
    #         passengers['passenger_id'].duplicated(keep=False)
    #     ].sort_values('passenger_id')
    # )

    # passenger_id should uniquely identify a passenger,
    # but some passenger_ids appear more than once with different
    # passenger information


    # checking whether duplicate passenger_id rows are exact duplicates

    duplicate_rows = passengers[
        passengers['passenger_id'].duplicated(keep=False)
    ]

    print(
        duplicate_rows.duplicated(keep=False).sum()
    )
    # 0 exact duplicate rows among duplicated passenger IDs


    # Removing duplicate passenger_id records

    passengers_clean = passengers.drop_duplicates(
        subset=['passenger_id'],
        keep='first'
    ).copy()

    print(
        passengers_clean['passenger_id']
        .duplicated()
        .sum()
    )
    # 0 duplicate passenger_ids


    print(
        passengers_clean.shape
    )
    # (1000, 9)


    # finding missing values again

    print(passengers_clean.isna().sum())


    # filling missing last names

    passengers_clean['last_name'] = (
        passengers_clean['last_name']
        .fillna('UNKNOWN')
    )

    print(
        passengers_clean['last_name'].isna().sum()
    )
    # 0


    # checking age values

    print(passengers_clean['age'].describe())


    # checking for invalid age values

    invalid_age = (
        (passengers_clean['age'] < 0)
        | (passengers_clean['age'] > 120)
    )

    print(
        "Invalid age values:",
        invalid_age.sum()
    )
    # 0


    # checking age with date of birth

    # The dataset follows the rule:
    # age = 2026 - year of birth

    passengers_clean['age_by_year'] = (
        2026
        - passengers_clean['date_of_birth'].dt.year
    )

    age_mismatch = (
        passengers_clean['age']
        != passengers_clean['age_by_year']
    )

    print(
        "Age mismatches:",
        age_mismatch.sum()
    )
    # 0


    # checking mismatched age records if any

    print(
        passengers_clean.loc[
            age_mismatch,
            [
                'passenger_id',
                'age',
                'date_of_birth',
                'age_by_year'
            ]
        ]
    )


    # removing temporary column

    passengers_clean.drop(
        columns='age_by_year',
        inplace=True
    )


    # checking gender values

    print(
        passengers_clean['gender']
        .value_counts(dropna=False)
    )


    # checking email values

    email_pattern = r'^[^@\s]+@[^@\s]+\.[^@\s]+$'

    invalid_email = (
        passengers_clean['email'].notna()
        & ~passengers_clean['email'].str.match(
            email_pattern,
            na=False
        )
    )

    print(
        "Invalid email values:",
        invalid_email.sum()
    )


    # checking phone values

    phone_digits = (
        passengers_clean['phone']
        .astype(str)
        .str.replace(r'\D', '', regex=True)
    )

    invalid_phone = (
        passengers_clean['phone'].notna()
        & (phone_digits.str.len() != 12)
    )

    print(
        "Invalid phone values:",
        invalid_phone.sum()
    )


    # converting aadhaar_id to string

    # Aadhaar is an identification value and not a numerical value,
    # so it should be stored as a string

    passengers_clean['aadhaar_id'] = (
        passengers_clean['aadhaar_id']
        .astype('string')
    )


    # checking aadhaar_id format

    aadhaar_digits = (
        passengers_clean['aadhaar_id']
        .str.replace(r'\D', '', regex=True)
    )

    invalid_aadhaar = (
        passengers_clean['aadhaar_id'].notna()
        & (aadhaar_digits.str.len() != 12)
    )

    print(
        "Invalid Aadhaar values:",
        invalid_aadhaar.sum()
    )


    # checking passenger_id format

    invalid_passenger_id = (
        ~passengers_clean['passenger_id']
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


    # checking first_name and last_name

    print(
        passengers_clean[
            ['first_name', 'last_name']
        ].head(10)
    )


    # checking for missing values after cleaning

    print(
        passengers_clean.isna().sum()
    )


    # checking duplicate passenger_ids after cleaning

    print(
        passengers_clean['passenger_id']
        .duplicated()
        .sum()
    )
    # 0


    # checking exact duplicate rows after cleaning

    print(
        passengers_clean.duplicated().sum()
    )
    # 0


    # checking final shape

    print(
        passengers_clean.shape
    )
    # (1000, 9)

    return passengers_clean
