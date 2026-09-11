import pandas as pd


def clean_payments(df):
    payments = df

    # finding missing values

    print(payments.isna().sum())


    # finding duplicates

    print(payments.duplicated().sum())


    # checking duplicate payment_id

    print(
        payments['payment_id']
        .duplicated(keep=False)
        .sum()
    )

    # payment_id should uniquely identify each payment


    # Removing duplicate payment records

    payments_clean = payments.drop_duplicates(
        subset=['payment_id'],
        keep='first'
    ).copy()

    print(
        payments_clean['payment_id']
        .duplicated()
        .sum()
    )
    # 0 duplicate payment_ids


    # finding missing values again

    print(payments_clean.isna().sum())


    # checking payment_id format

    print(
        payments_clean['payment_id'].head()
    )

    invalid_payment_id = (
        ~payments_clean['payment_id']
        .astype(str)
        .str.match(
            r'^PAY\d+$',
            na=False
        )
    )

    print(
        "Invalid payment_id values:",
        invalid_payment_id.sum()
    )


    # checking booking_id format

    invalid_booking_id = (
        ~payments_clean['booking_id']
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


    # checking amount values

    print(
        payments_clean['amount'].head(20)
    )

    print(
        payments_clean['amount'].dtype
    )


    # converting amount to numeric
    # invalid values such as "INVALID" are converted to NaN

    payments_clean['amount'] = pd.to_numeric(
        payments_clean['amount'],
        errors='coerce'
    )

    print(
        payments_clean['amount'].dtype
    )


    # finding missing values after converting amount

    print(
        payments_clean['amount'].isna().sum()
    )
    # 78


    # checking amount values

    print(
        payments_clean['amount'].describe()
    )


    # checking for invalid and missing amount values
    # NaN values are not detected by <= 0, so isna() is also checked

    invalid_amount = (
        (payments_clean['amount'] <= 0)
        | payments_clean['amount'].isna()
    )

    print(
        "Invalid payment amounts:",
        invalid_amount.sum()
    )


    # checking invalid payment records

    print(
        payments_clean.loc[
            invalid_amount,
            ['payment_id', 'booking_id', 'amount']
        ]
    )


    # checking payment methods

    print(
        payments_clean['payment_method']
        .value_counts(dropna=False)
    )


    # checking unique payment methods

    print(
        payments_clean['payment_method'].unique()
    )


    # finding missing values after cleaning

    print(
        payments_clean.isna().sum()
    )


    # checking duplicate payment_ids after cleaning

    print(
        payments_clean['payment_id']
        .duplicated()
        .sum()
    )
    # 0


    # checking exact duplicate rows after cleaning

    print(
        payments_clean.duplicated().sum()
    )
    # 0


    # checking final shape

    print(
        payments_clean.shape
    )
    # (1000, 4)

    return payments_clean
