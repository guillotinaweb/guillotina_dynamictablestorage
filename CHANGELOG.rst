1.1.5 (unreleased)
------------------

- Nothing changed yet.


1.1.4 (2021-05-13)
------------------

- Fix potential connection leak in connection pool


1.1.3 (2021-04-16)
------------------

- Use pool instead of open/close connection on every op


1.1.2 (2020-10-15)
------------------

- Use a lock when getting database connection to prevent
  situation where multiple database are being initialized
  simultaneously


1.1.1 (2020-03-02)
------------------

- set `__storage_id__` attributes on db instance
  [vangheem]


1.1.0 (2019-12-10)
------------------

- Fix possible sql injection
  [vangheem]


1.0.5 (2019-06-18)
------------------

- restrict req'd g


1.0.4 (2019-01-23)
------------------

- Use shared connection lock
  [vangheem]

1.0.3 (2019-01-11)
------------------

- Fix tests, fix when database is deleted
  [vangheem]


1.0.2 (2019-01-11)
------------------

- Use connection_managers instead of pool
  [vangheem]


1.0.1 (2019-01-08)
------------------

- initial