-- creating database

CREATE DATABASE IF NOT EXISTS airlines_dw;

USE airlines_dw;


-- creating passengers table

CREATE TABLE IF NOT EXISTS passengers (
    passenger_id VARCHAR(20) PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    age INT,
    gender VARCHAR(20),
    email VARCHAR(255),
    phone VARCHAR(20),
    aadhaar_id VARCHAR(20),
    date_of_birth DATE
);


-- creating flights table

CREATE TABLE IF NOT EXISTS flights (
    flight_key INT AUTO_INCREMENT PRIMARY KEY,
    flight_id VARCHAR(20),
    airline VARCHAR(100),
    source VARCHAR(100),
    destination VARCHAR(100),
    departure_time DATETIME,
    arrival_time DATETIME,
    duration TIME
);


-- creating bookings table

CREATE TABLE IF NOT EXISTS bookings (
    booking_id VARCHAR(20) PRIMARY KEY,
    passenger_id VARCHAR(20),
    flight_id VARCHAR(20),
    booking_date DATETIME,
    status VARCHAR(50),
    passport_number VARCHAR(50),
    seat_number VARCHAR(20),
    emergency_contact_name VARCHAR(100),
    emergency_contact_phone VARCHAR(20),

    FOREIGN KEY (passenger_id)
        REFERENCES passengers(passenger_id)
);


-- creating payments table

CREATE TABLE IF NOT EXISTS payments (
    payment_id VARCHAR(20) PRIMARY KEY,
    booking_id VARCHAR(20),
    amount DECIMAL(12,2),
    payment_method VARCHAR(50),

    FOREIGN KEY (booking_id)
        REFERENCES bookings(booking_id)
);


-- checking total number of records

SELECT
    (SELECT COUNT(*) FROM passengers) AS total_passengers,
    (SELECT COUNT(*) FROM flights) AS total_flights,
    (SELECT COUNT(*) FROM bookings) AS total_bookings,
    (SELECT COUNT(*) FROM payments) AS total_payments;


-- checking bookings affected by duplicate flight IDs

SELECT
    COUNT(*) AS affected_bookings
FROM bookings b
JOIN (
    SELECT
        flight_id
    FROM flights
    GROUP BY flight_id
    HAVING COUNT(*) > 1
) d
    ON b.flight_id = d.flight_id;


-- checking the bookings for 6F250

SELECT
    b.booking_id,
    b.passenger_id,
    b.flight_id,
    f.flight_key,
    f.source,
    f.destination,
    f.departure_time,
    f.arrival_time
FROM bookings b
JOIN flights f
    ON b.flight_id = f.flight_id
WHERE b.flight_id = '6F250'
ORDER BY
    b.booking_id,
    f.flight_key;


-- creating flight mapping

CREATE OR REPLACE VIEW flight_mapping AS

SELECT
    flight_id,
    MIN(flight_key) AS flight_key
FROM flights
GROUP BY flight_id;


-- checking flight mapping

SELECT *
FROM flight_mapping
ORDER BY flight_id;


-- creating valid booking flight view
-- excluding bookings with ambiguous flight_id 6F250

CREATE OR REPLACE VIEW valid_booking_flights AS

SELECT
    b.booking_id,
    b.passenger_id,
    b.flight_id,
    fm.flight_key,
    f.airline,
    f.source,
    f.destination,
    f.departure_time,
    f.arrival_time,
    f.duration,
    b.booking_date,
    b.status,
    b.seat_number
FROM bookings b
JOIN flight_mapping fm
    ON b.flight_id = fm.flight_id
JOIN flights f
    ON fm.flight_key = f.flight_key
WHERE b.flight_id <> '6F250';


-- checking number of valid bookings

SELECT
    COUNT(*) AS valid_flight_bookings
FROM valid_booking_flights;


-- calculating total payments and revenue

SELECT
    COUNT(*) AS total_payments,
    COUNT(amount) AS payments_with_amount,
    COUNT(*) - COUNT(amount) AS payments_without_amount,
    SUM(amount) AS total_revenue
FROM payments;


-- calculating average payment amount

SELECT
    AVG(amount) AS average_payment_amount
FROM payments;


-- finding minimum and maximum payment amount

SELECT
    MIN(amount) AS minimum_payment,
    MAX(amount) AS maximum_payment
FROM payments;


-- calculating average flight duration

SELECT
    SEC_TO_TIME(
        AVG(TIME_TO_SEC(duration))
    ) AS average_flight_duration
FROM flights;


-- calculating bookings by flight

SELECT
    flight_key,
    flight_id,
    airline,
    source,
    destination,
    COUNT(booking_id) AS total_bookings
FROM valid_booking_flights
GROUP BY
    flight_key,
    flight_id,
    airline,
    source,
    destination
ORDER BY total_bookings DESC;


-- calculating route wise booking traffic

SELECT
    source,
    destination,
    COUNT(booking_id) AS total_bookings
FROM valid_booking_flights
GROUP BY
    source,
    destination
ORDER BY total_bookings DESC;


-- calculating route wise flight traffic

SELECT
    source,
    destination,
    COUNT(*) AS total_flights
FROM flights
GROUP BY
    source,
    destination
ORDER BY total_flights DESC;


-- calculating airline wise flights

SELECT
    airline,
    COUNT(*) AS total_flights
FROM flights
GROUP BY airline
ORDER BY total_flights DESC;


-- calculating airline wise bookings

SELECT
    airline,
    COUNT(booking_id) AS total_bookings
FROM valid_booking_flights
GROUP BY airline
ORDER BY total_bookings DESC;


-- calculating airline wise flights and bookings

SELECT
    f.airline,
    COUNT(DISTINCT f.flight_key) AS total_flights,
    COUNT(DISTINCT v.booking_id) AS total_bookings
FROM flights f
LEFT JOIN valid_booking_flights v
    ON f.flight_key = v.flight_key
GROUP BY f.airline
ORDER BY total_bookings DESC;


-- calculating booking status distribution

SELECT
    status,
    COUNT(*) AS total_bookings
FROM bookings
GROUP BY status
ORDER BY total_bookings DESC;


-- calculating booking status percentage

SELECT
    status,
    COUNT(*) AS total_bookings,
    ROUND(
        COUNT(*) * 100.0 /
        (SELECT COUNT(*) FROM bookings),
        2
    ) AS booking_percentage
FROM bookings
GROUP BY status
ORDER BY total_bookings DESC;


-- calculating payment method distribution

SELECT
    payment_method,
    COUNT(*) AS total_payments
FROM payments
GROUP BY payment_method
ORDER BY total_payments DESC;


-- calculating payment method revenue

SELECT
    payment_method,
    COUNT(amount) AS payments_with_amount,
    SUM(amount) AS total_revenue,
    AVG(amount) AS average_payment
FROM payments
GROUP BY payment_method
ORDER BY total_revenue DESC;


-- calculating revenue by airline

SELECT
    v.airline,
    COUNT(DISTINCT v.booking_id) AS total_bookings,
    SUM(p.amount) AS total_revenue
FROM valid_booking_flights v
JOIN payments p
    ON v.booking_id = p.booking_id
GROUP BY v.airline
ORDER BY total_revenue DESC;


-- calculating revenue by route

SELECT
    v.source,
    v.destination,
    COUNT(DISTINCT v.booking_id) AS total_bookings,
    SUM(p.amount) AS total_revenue
FROM valid_booking_flights v
JOIN payments p
    ON v.booking_id = p.booking_id
GROUP BY
    v.source,
    v.destination
ORDER BY total_revenue DESC;


-- calculating average flight duration by airline

SELECT
    airline,
    SEC_TO_TIME(
        AVG(TIME_TO_SEC(duration))
    ) AS average_flight_duration
FROM flights
GROUP BY airline
ORDER BY average_flight_duration DESC;


-- calculating average flight duration by route

SELECT
    source,
    destination,
    COUNT(*) AS total_flights,
    SEC_TO_TIME(
        AVG(TIME_TO_SEC(duration))
    ) AS average_duration
FROM flights
GROUP BY
    source,
    destination
ORDER BY average_duration DESC;


-- finding longest flights

SELECT
    flight_key,
    flight_id,
    airline,
    source,
    destination,
    duration
FROM flights
ORDER BY TIME_TO_SEC(duration) DESC
LIMIT 10;


-- finding shortest flights

SELECT
    flight_key,
    flight_id,
    airline,
    source,
    destination,
    duration
FROM flights
ORDER BY TIME_TO_SEC(duration)
LIMIT 10;


-- calculating passenger age groups

SELECT
    CASE
        WHEN age < 18 THEN 'Below 18'
        WHEN age BETWEEN 18 AND 30 THEN '18-30'
        WHEN age BETWEEN 31 AND 45 THEN '31-45'
        WHEN age BETWEEN 46 AND 60 THEN '46-60'
        ELSE '60+'
    END AS age_group,
    COUNT(*) AS total_passengers
FROM passengers
GROUP BY
    CASE
        WHEN age < 18 THEN 'Below 18'
        WHEN age BETWEEN 18 AND 30 THEN '18-30'
        WHEN age BETWEEN 31 AND 45 THEN '31-45'
        WHEN age BETWEEN 46 AND 60 THEN '46-60'
        ELSE '60+'
    END
ORDER BY total_passengers DESC;


-- calculating gender distribution

SELECT
    gender,
    COUNT(*) AS total_passengers
FROM passengers
GROUP BY gender
ORDER BY total_passengers DESC;


-- calculating bookings by date

SELECT
    DATE(booking_date) AS booking_date,
    COUNT(*) AS total_bookings
FROM bookings
GROUP BY DATE(booking_date)
ORDER BY booking_date;


-- calculating revenue by booking date

SELECT
    DATE(b.booking_date) AS booking_date,
    COUNT(DISTINCT b.booking_id) AS total_bookings,
    SUM(p.amount) AS total_revenue
FROM bookings b
JOIN payments p
    ON b.booking_id = p.booking_id
GROUP BY DATE(b.booking_date)
ORDER BY booking_date;


-- calculating bookings per passenger

SELECT
    passenger_id,
    COUNT(*) AS total_bookings
FROM bookings
GROUP BY passenger_id
ORDER BY total_bookings DESC;


-- finding top passengers by bookings

SELECT
    p.passenger_id,
    p.first_name,
    p.last_name,
    COUNT(b.booking_id) AS total_bookings
FROM passengers p
JOIN bookings b
    ON p.passenger_id = b.passenger_id
GROUP BY
    p.passenger_id,
    p.first_name,
    p.last_name
ORDER BY total_bookings DESC
LIMIT 10;


-- finding top flights by bookings

SELECT
    flight_id,
    COUNT(*) AS total_bookings
FROM bookings
WHERE flight_id <> '6F250'
GROUP BY flight_id
ORDER BY total_bookings DESC
LIMIT 10;


-- checking bookings with payment

SELECT
    COUNT(DISTINCT b.booking_id) AS total_bookings,
    COUNT(DISTINCT p.booking_id) AS bookings_with_payment,
    COUNT(DISTINCT b.booking_id)
        - COUNT(DISTINCT p.booking_id) AS bookings_without_payment
FROM bookings b
LEFT JOIN payments p
    ON b.booking_id = p.booking_id;


-- calculating number of overnight flights

SELECT
    COUNT(*) AS overnight_flights
FROM flights
WHERE DATE(departure_time) <> DATE(arrival_time);


-- finding overnight flights

SELECT
    flight_key,
    flight_id,
    airline,
    source,
    destination,
    departure_time,
    arrival_time,
    duration
FROM flights
WHERE DATE(departure_time) <> DATE(arrival_time)
ORDER BY departure_time;


-- calculating average and standard deviation of flight duration

SELECT
    AVG(TIME_TO_SEC(duration)) AS average_duration_seconds,
    STDDEV(TIME_TO_SEC(duration)) AS duration_stddev_seconds
FROM flights;


-- finding flight duration anomalies

SELECT
    flight_key,
    flight_id,
    airline,
    source,
    destination,
    duration
FROM flights
WHERE TIME_TO_SEC(duration) < (
        SELECT
            AVG(TIME_TO_SEC(duration))
            - 2 * STDDEV(TIME_TO_SEC(duration))
        FROM flights
    )
   OR TIME_TO_SEC(duration) > (
        SELECT
            AVG(TIME_TO_SEC(duration))
            + 2 * STDDEV(TIME_TO_SEC(duration))
        FROM flights
    )
ORDER BY TIME_TO_SEC(duration) DESC;


-- calculating number of flight duration anomalies

SELECT
    COUNT(*) AS duration_anomalies
FROM flights
WHERE TIME_TO_SEC(duration) < (
        SELECT
            AVG(TIME_TO_SEC(duration))
            - 2 * STDDEV(TIME_TO_SEC(duration))
        FROM flights
    )
   OR TIME_TO_SEC(duration) > (
        SELECT
            AVG(TIME_TO_SEC(duration))
            + 2 * STDDEV(TIME_TO_SEC(duration))
        FROM flights
    );


-- final KPI summary

SELECT
    (SELECT COUNT(*) FROM flights) AS total_flights,

    (SELECT COUNT(*) FROM bookings) AS total_bookings,

    (SELECT COUNT(*) FROM passengers) AS total_passengers,

    (SELECT SUM(amount) FROM payments) AS total_revenue,

    (
        SELECT SEC_TO_TIME(
            AVG(TIME_TO_SEC(duration))
        )
        FROM flights
    ) AS average_flight_duration,

    (
        SELECT COUNT(*)
        FROM bookings
        WHERE flight_id = '6F250'
    ) AS excluded_ambiguous_bookings,

    (
        SELECT COUNT(*)
        FROM flights
        WHERE TIME_TO_SEC(duration) < (
                SELECT
                    AVG(TIME_TO_SEC(duration))
                    - 2 * STDDEV(TIME_TO_SEC(duration))
                FROM flights
            )
           OR TIME_TO_SEC(duration) > (
                SELECT
                    AVG(TIME_TO_SEC(duration))
                    + 2 * STDDEV(TIME_TO_SEC(duration))
                FROM flights
            )
    ) AS duration_anomalies;