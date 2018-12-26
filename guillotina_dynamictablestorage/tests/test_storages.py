from guillotina._settings import app_settings
from guillotina.component import get_adapter
from guillotina.db.interfaces import IDatabaseManager

import json


async def test_get_storages(container_requester):
    async with container_requester as requester:
        response, status = await requester('GET', '/@storages')
        assert status == 200
        assert response[0]['id'] == 'db'


async def test_get_storage(container_requester):
    async with container_requester as requester:
        response, status = await requester('GET', '/@storages/db')
        assert status == 200
        assert response['id'] == 'db'
        assert response['databases'] == []


async def test_create_database(container_requester):
    async with container_requester as requester:
        response, status = await requester(
            'POST', '/@storages/db', data=json.dumps({
                'name': 'foobar'
            }))
        assert status == 200
        response, status = await requester('GET', '/@storages/db')
        assert 'foobar' in response['databases']
        await requester('DELETE', '/@storages/db/foobar')


async def test_get_database(container_requester):
    async with container_requester as requester:
        await requester('POST', '/@storages/db', data=json.dumps({
            'name': 'foobar'
        }))
        response, status = await requester('GET', '/@storages/db/foobar')
        assert status == 200
        assert response['id'] == 'foobar'
        await requester('DELETE', '/@storages/db/foobar')


async def test_delete_database(container_requester):
    async with container_requester as requester:
        await requester('POST', '/@storages/db', data=json.dumps({
            'name': 'foobar'
        }))
        response, status = await requester('DELETE', '/@storages/db/foobar')
        assert status == 200
        response, status = await requester('GET', '/@storages/db')
        assert 'foobar' not in response['databases']


async def test_storage_impl(db, guillotina_main):
    storages = app_settings['storages']
    storage_config = storages['db']
    factory = get_adapter(guillotina_main.root, IDatabaseManager,
                          name=storage_config['storage'],
                          args=[storage_config])
    original_size = len(await factory.get_names())
    await factory.create('foobar')
    assert len(await factory.get_names()) == (original_size + 1)
    await factory.delete('foobar')
    assert len(await factory.get_names()) == original_size


async def test_storage_exists(db, guillotina_main):
    storages = app_settings['storages']
    storage_config = storages['db']
    factory = get_adapter(guillotina_main.root, IDatabaseManager,
                          name=storage_config['storage'],
                          args=[storage_config])
    assert not await factory.exists('foobar')
    await factory.create('foobar')
    assert await factory.exists('foobar')
    await factory.delete('foobar')
    assert not await factory.exists('foobar')
