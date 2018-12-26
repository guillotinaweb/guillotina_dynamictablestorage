from guillotina import testing


def base_settings_configurator(settings):
    if 'applications' in settings:
        settings['applications'].append('guillotina_dynamictablestorage')
    else:
        settings['applications'] = ['guillotina_dynamictablestorage']

    settings["storages"]['db']['type'] = 'prefixed-table'


testing.configure_with(base_settings_configurator)
