DEFAULT_ROLES_PERMISSIONS = {
    'roles': [
        {
            'name': 'Super Admin',
            'is_admin': True,
            'is_default': True
        },
        {
            'name': 'Admin',
            'is_admin': True,
            'is_default': True
        },
    ],
    'permissions': {
        # 'Agents': {
        #     'description': '',
        #     'actions': {'api_create': False, 'api_read': False, 'api_edit': False, 'api_delete': False}
        # },
        'Processes': {
            'description': '',
            'actions': {'api_create': False, 'api_read': False, 'api_edit': False, 'api_delete': False}
        },
        'ActivityLogs': {
            'description': '',
            'actions': {'api_create': False, 'api_read': False, 'api_edit': False, 'api_delete': False}
        },
    },
    'content_types': {
        'ActivityLogs': {'app_label': 'processes', 'model': 'activitylogs'},
        'Processes': {'app_label': 'processes', 'model': 'process'},
    }
}
