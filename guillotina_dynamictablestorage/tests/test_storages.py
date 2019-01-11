import json


async def test_get_storages(container_requester, dyn_storage):
    async with container_requester as requester:
        response, status = await requester('GET', '/@storages')
        assert status == 200
        assert response[0]['id'] == 'db'


async def test_get_storage(container_requester, dyn_storage):
    async with container_requester as requester:
        response, status = await requester('GET', '/@storages/db')
        assert status == 200
        assert response['id'] == 'db'
        assert response['databases'] == []


async def test_create_database(container_requester, dyn_storage):
    async with container_requester as requester:
        response, status = await requester(
            'POST', '/@storages/db', data=json.dumps({
                'name': 'foobar'
            }))
        assert status == 200
        response, status = await requester('GET', '/@storages/db')
        assert 'foobar' in response['databases']
        await requester('DELETE', '/@storages/db/foobar')


async def test_get_database(container_requester, dyn_storage):
    async with container_requester as requester:
        await requester('POST', '/@storages/db', data=json.dumps({
            'name': 'foobar'
        }))
        response, status = await requester('GET', '/@storages/db/foobar')
        assert status == 200
        assert response['id'] == 'foobar'
        await requester('DELETE', '/@storages/db/foobar')


async def test_delete_database(container_requester, dyn_storage):
    async with container_requester as requester:
        await requester('POST', '/@storages/db', data=json.dumps({
            'name': 'foobar'
        }))
        response, status = await requester('DELETE', '/@storages/db/foobar')
        assert status == 200
        response, status = await requester('GET', '/@storages/db')
        assert 'foobar' not in response['databases']


async def test_delete_add_and_reuse_database(container_requester, dyn_storage):
    async with container_requester as requester:
        await requester('POST', '/@storages/db', data=json.dumps({
            'name': 'foobar'
        }))
        response, status = await requester('DELETE', '/@storages/db/foobar')
        assert status == 200
        response, status = await requester('GET', '/@storages/db')
        assert 'foobar' not in response['databases']

        # test should still have pool active
        assert dyn_storage._connection_managers['db'].pool is not None

        await requester('POST', '/@storages/db', data=json.dumps({
            'name': 'foobar2'
        }))

        response, status = await requester('GET', '/@storages/db')
        assert 'foobar2' in response['databases']


async def test_storage_impl(dyn_storage):
    original_size = len(await dyn_storage.get_names())
    await dyn_storage.create('foobar')
    assert len(await dyn_storage.get_names()) == (original_size + 1)
    await dyn_storage.delete('foobar')
    assert len(await dyn_storage.get_names()) == original_size


async def test_storage_exists(dyn_storage):
    assert not await dyn_storage.exists('foobar')
    await dyn_storage.create('foobar')
    assert await dyn_storage.exists('foobar')
    await dyn_storage.delete('foobar')
    assert not await dyn_storage.exists('foobar')
