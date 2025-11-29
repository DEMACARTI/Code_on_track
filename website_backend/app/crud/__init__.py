"""
CRUD operations for the application.
"""
from . import user, item, engrave, vendor, event  # noqa

# Import all CRUD operations to make them available from the package
from .user import (  # noqa
    get_user,
    get_user_by_email,
    get_user_by_username,
    get_users,
    create_user,
    update_user,
    delete_user,
    authenticate_user,
)

from .vendor import (  # noqa
    create_vendor,
    get_vendor,
    get_vendor_by_name,
    list_vendors,
    update_vendor,
    delete_vendor,
)

from .item import (  # noqa
    get_item,
    get_item_by_uid,
    get_items,
    create_item,
    update_item,
    update_item_status,
    delete_item,
)

from .engrave import (  # noqa
    get_engrave_job,
    get_engrave_jobs,
    create_engrave_job,
    update_engrave_job,
    delete_engrave_job,
    upsert_engrave_job,
)

from .event import (  # noqa
    create_event,
    get_event,
    get_events,
    update_event,
    delete_event,
)
