import pandas as pd


def clean_flights(df):
    df = df.copy()

    # finding missing values

    print(df.isna().sum())
    # from this we can understand that the column airline has 41 missing values


    # finding duplicates

    print(df.duplicated().sum())

    # print(df['flight_id'].duplicated(keep=False).sum())

    # print(df['flight_id'].value_counts()[df['flight_id'].value_counts() > 1])

    # print(
    #     df[df['flight_id'].duplicated(keep=False)]
    #     .sort_values('flight_id')
    # )

    # flight_id can't be the unique identification of table because the same
    # flight_id can occur for different journeys/dates


    # Removing the duplicates

    df = df.drop_duplicates()

    print(df.duplicated().sum())
    # zero duplicates


    # finding missing values again

    print(df.isna().sum())
    # from this we can understand that the column airline has 39 missing values,
    # this says some of the rows were removed during removing the duplicates


    # print(df.loc[df['airline'].isna(), ['flight_id', 'source', 'destination']])

    # print(df['flight_id'].str[:2].value_counts())

    # print(df['airline'].value_counts())

    # print(
    #     df.groupby(df['flight_id'].str[:2])['airline']
    #     .value_counts(dropna=False)
    # )


    # filling missing airline values using flight_id prefix

    airline_mapping = {
        '6F': 'IndiGo',
        'AI': 'Air India',
        'SJ': 'SpiceJet',
        'UK': 'Vistara'
    }

    df['airline_code'] = df['flight_id'].str[:2]

    mask = (
        df['airline'].isna()
        | (df['airline'] == 'UNKNOWN')
    )

    print(mask.sum())

    df.loc[mask, 'airline'] = (
        df.loc[mask, 'airline_code']
        .map(airline_mapping)
    )

    print(df['airline'].isna().sum())
    # 0

    print((df['airline'] == 'UNKNOWN').sum())
    # 0

    print(df['airline'].value_counts())


    # removing temporary column

    df.drop(columns='airline_code', inplace=True)


    # checking flight_id format

    print(df['flight_id'].str[:2].value_counts())

    print(df['flight_id'].str.len().value_counts())


    # checking flight_id collisions

    collision_ids = (
        df['flight_id']
        [df['flight_id'].duplicated(keep=False)]
        .unique()
    )

    print(
        "Colliding flight_id values:",
        list(collision_ids)
    )

    # flight_id is not unique because the same flight_id can represent
    # different journeys.
    # Therefore, the duplicate flight_id values are not removed or renamed.
    # A separate unique flight key will be created later in SQL.


    # checking departure time, arrival time and duration

    print(
        df[
            ['departure_time', 'arrival_time', 'duration']
        ].head(10)
    )


    # calculating duration using departure and arrival timestamps

    df['calculated_duration'] = (
        df['arrival_time']
        - df['departure_time']
    )

    print(df['duration'].dtype)


    # converting duration from datetime.time to pandas Timedelta

    df['duration'] = df['duration'].apply(
        lambda x: pd.Timedelta(
            hours=x.hour,
            minutes=x.minute,
            seconds=x.second
        )
    )


    # comparing given duration with calculated duration

    # timestamps contain milliseconds while the given duration
    # contains only seconds, so calculated duration is rounded to seconds

    df['calculated_duration_rounded'] = (
        df['calculated_duration']
        .dt.round('s')
    )

    mismatch = (
        df['duration']
        != df['calculated_duration_rounded']
    )

    print(mismatch.sum())

    print(
        df.loc[
            mismatch,
            [
                'flight_id',
                'airline',
                'source',
                'destination',
                'duration',
                'calculated_duration_rounded'
            ]
        ]
    )


    # checking for flights where arrival time is before departure time

    invalid_time = (
        df['arrival_time']
        < df['departure_time']
    )

    print(
        "Invalid time records:",
        invalid_time.sum()
    )


    # correcting overnight/cross-day flights

    df.loc[invalid_time, 'arrival_time'] = (
        df.loc[invalid_time, 'arrival_time']
        + pd.Timedelta(days=1)
    )


    # recalculating duration after correcting overnight flights

    df['calculated_duration'] = (
        df['arrival_time']
        - df['departure_time']
    )

    df['calculated_duration_rounded'] = (
        df['calculated_duration']
        .dt.round('s')
    )


    # validating duration again

    print(
        (
            df['duration']
            != df['calculated_duration_rounded']
        ).sum()
    )
    # 0


    # checking source and destination for missing values

    print(
        df[
            ['source', 'destination']
        ].isna().sum()
    )


    # checking source values

    print(
        df['source'].value_counts(dropna=False)
    )


    # checking destination values

    print(
        df['destination'].value_counts(dropna=False)
    )


    # checking whether source and destination are the same

    print(
        (df['source'] == df['destination']).sum()
    )
    # 0


    # checking duration after cleaning

    print(
        df[
            ['duration', 'calculated_duration']
        ].head()
    )

    print(
        (
            df['duration']
            != df['calculated_duration_rounded']
        ).sum()
    )
    # 0


    # removing temporary columns

    df.drop(
        columns=[
            'calculated_duration',
            'calculated_duration_rounded'
        ],
        inplace=True
    )


    # checking final shape

    print(df.shape)
    # (1005, 7)


    # converting duration to a plain HH:MM:SS string before saving
    # pandas Timedelta can be stored by Excel as a fraction of a day.
    # Converting it to HH:MM:SS ensures the duration is preserved
    # correctly when the file is read again.

    df['duration'] = df['duration'].apply(
        lambda td: str(td).split(' ')[-1]
    )

    print(df['duration'].head())

    return df
