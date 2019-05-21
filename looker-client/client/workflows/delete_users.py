import logging
import os
from client.workflows import Workflow
from client.helpers import *

logger = logging.getLogger(__name__)

def register(parent, handlers):
    '''register the cli'''
    sp = parent.add_parser('delete-users', help='delete users from a text file')
    sp.add_argument('--fp', dest='fp', help='path to user text file', required=True)
    sp.add_argument('--dry-run', dest='dry_run', help='dry run, does not delete users', action='store_true')
    handlers['delete-users'] = lambda args: run(args)

def run(args):
    logger.info('delete users')

    if (not os.path.exists(args.fp)) or (not os.path.isfile(args.fp)):
        logger.error(f'missing file {args.fp}')
        exit()

    # get user id's to delete from file
    logger.info(f'reading file {args.fp}')
    with open(args.fp, 'r') as f:
        users_to_delete = list(int(u.strip()) for u in f.readlines() if u.strip())

    logger.info(f'found file users: {len(users_to_delete)}')

    auth = BearerAuth()
    auth.token

    # get all users from looker
    logger.info('retrieving looker users')
    all_api_users = {}
    page = 1
    while True:
        r = get(
            url=url('/api/3.1/users'),
            auth=auth,
            data={'fields': 'id,email', 'page': page, 'per_page': 1000}
        )
        assert r.status_code in range(200,300), r.text
        some_api_users = r.json()

        for some_user in some_api_users:
            all_api_users[int(some_user['id'])] = some_user

        page = page + 1
        if not some_api_users:
            break

    logger.info(f'found {len(all_api_users)} api users')

    for user_id in users_to_delete:
        if user_id in all_api_users:
            user_email = all_api_users[user_id].get('email')
            logger.info(f'deleting user, id: {user_id}, email: {user_email}')

            if not args.dry_run:
                r = delete(
                    url(f'/api/3.1/users/{user_id}'),
                    auth=auth
                )

                assert r.status_code in range(200, 300), f'failed to delete {user_id}, {r.text}'

                logger.info(f'deleted user, id: {user_id}, email: {user_email}')
        else:
            logger.error(f'user not found, id: {user_id}')


    logger.info('logging out')
    delete(url('/api/3.1/logout'))

Workflow(register_function=register)
