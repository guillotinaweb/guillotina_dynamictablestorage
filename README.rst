guillotina_dynamictablestorage
==============================

Dynamic storage implementation that uses tables instead of pg databases.

This allows us to reuse connection pools but still be able to separate
data to different tables.


Example configuration::

    ...
    storages:
      my-storage:
        storage: postgresql
        type: prefixed-table
        dsn: postgresql://postgres@localhost:5432/guillotina
    ...
