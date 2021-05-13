import asyncio
from copy import deepcopy
from typing import Dict
from typing import List

import asyncpg
from guillotina import configure
from guillotina.component import get_utility
from guillotina.contrib.catalog.pg import sqlq
from guillotina.db.factory import PostgresqlDatabaseManager
from guillotina.db.factory import _convert_dsn
from guillotina.db.interfaces import IDatabaseManager
from guillotina.event import notify
from guillotina.events import DatabaseInitializedEvent
from guillotina.interfaces import IApplication
from guillotina.interfaces import IDatabase
from guillotina.interfaces import IDatabaseConfigurationFactory
from guillotina.utils import apply_coroutine


app_settings = {}


@configure.adapter(
    for_=IApplication, provides=IDatabaseManager, name="prefixed-table"  # noqa: N801
)
class PrefixedDatabaseManager(PostgresqlDatabaseManager):
    _connection_managers = {}  # shared on all instances
    _locks: Dict[str, asyncio.Lock] = {}  # also shared

    def _get_lock(self, storage_id: str):
        if storage_id not in self._locks:
            self._locks[storage_id] = asyncio.Lock()
        return self._locks[storage_id]

    def get_dsn(self, name: str = None) -> str:
        if isinstance(self.config["dsn"], str):
            return self.config["dsn"]
        else:
            return _convert_dsn(self.config["dsn"])

    async def get_pool(self) -> asyncpg.pool.Pool:
        """
        Get connection pool for storage and cache it on the app object
        """
        pool_name = f'_pool_{self.config["storage_id"]}'
        if getattr(self.app, pool_name, None) is None:
            dsn = self.get_dsn()
            async with self._get_lock(self.config["storage_id"]):
                # check again after lock
                if getattr(self.app, pool_name, None) is None:
                    setattr(
                        self.app,
                        pool_name,
                        await asyncpg.create_pool(
                            dsn=dsn,
                            max_size=5,
                            min_size=0,
                            statement_cache_size=0,
                            max_inactive_connection_lifetime=60,
                        ),
                    )
        return getattr(self.app, pool_name)

    async def get_names(self) -> List[str]:
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            result = await conn.fetch(
                """
SELECT table_name FROM information_schema.tables WHERE table_schema='public'
"""
            )
            return [
                item["table_name"].replace("_objects", "")
                for item in result
                if item["table_name"].endswith("_objects")
            ]

    async def create(self, name: str) -> bool:
        # creates db here...
        db = await self.get_database(name)
        return db is not None

    async def delete(self, name: str) -> bool:
        if name in self.app:
            await self.app[name].finalize()
            del self.app[name]

        pool = await self.get_pool()
        async with pool.acquire() as conn:
            for table_name in ("blobs", "objects"):
                await conn.execute(
                    "DROP TABLE IF EXISTS {}_{}".format(sqlq(name), sqlq(table_name))
                )
            return True

    async def get_database(self, name: str) -> IDatabase:
        if name not in self.app:
            config = deepcopy(self.config)
            config.update(
                {
                    "dsn": self.get_dsn(name),
                    "objects_table_name": name + "_objects",
                    "blobs_table_name": name + "_blobs",
                }
            )
            async with self._get_lock(self.config["storage_id"]):
                if self.config["storage_id"] in self._connection_managers:
                    config["connection_manager"] = self._connection_managers[
                        self.config["storage_id"]
                    ]
                factory = get_utility(
                    IDatabaseConfigurationFactory, name=config["storage"]
                )
                self.app[name] = await apply_coroutine(factory, name, config)
                self.app[name].__storage_id__ = self.config["storage_id"]

                if self.config["storage_id"] not in self._connection_managers:
                    storage = self.app[name].storage
                    self._connection_managers[
                        self.config["storage_id"]
                    ] = storage.connection_manager
                    self._connection_managers[
                        self.config["storage_id"]
                    ]._closable = False
                await notify(DatabaseInitializedEvent(self.app[name]))

        return self.app[name]

    async def exists(self, name: str) -> bool:
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            result = await conn.fetch(
                """
select * FROM information_schema.tables
WHERE table_schema='public' and table_name = '{}_objects'
        """.format(
                    sqlq(name)
                )
            )
            return len(result) > 0


def includeme(root):
    """"""
    pass
