CREATE TABLE wrestlers (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    real_name VARCHAR,
    height VARCHAR,
    weight VARCHAR,
    debut TIMESTAMP,
    retirement TIMESTAMP,
    is_active BOOLEAN,
    years_active INTEGER
);
