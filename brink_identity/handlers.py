from datetime import datetime, timedelta

import jwt
from brink.decorators import require_request_model
from brink.exceptions import HTTPNotFound, HTTPBadRequest, HTTPUnauthorized

from brink_identity.models import Identity


@require_request_model(Identity)
async def handle_auth_identity(request, identity):
    """
    Handler for identity authentication. The request is expected to contain at
    least a partial JSON representation of an Identity model object. The
    required fields are username and password.
    """
    if not await identity.authenticate():
        raise HTTPUnauthorized(text="Incorrect username or password")

    exp = datetime.utcnow() + timedelta(days=1)
    token = jwt.encode({"id": identity.id, "exp": exp},
                       "secret", algorithm="HS256")
    res = {
        "token": token.decode("utf-8"),
        "expires": exp,
        "identity": identity
    }

    return 200, {"data": res}


async def handle_list_identities(request):
    """
    Handler for listing identities.
    """
    users = await Identity.all().as_list()
    return 200, {"data": users}


@require_request_model(Identity)
async def handle_create_identity(request, identity):
    """
    Handler for creating an Identity. The request is expected to contain a full
    JSON representation of an Identity model object. Usernames are unique, thus
    a unique new username is required.
    """
    if not await identity.username_available():
        raise HTTPBadRequest(text="username is already taken")

    await identity.save()
    return 201, {"data": identity}


async def handle_get_identity(request):
    """
    Handler for getting a single identity by id.
    """
    id = request.match_info["id"]
    identity = await Identity.get(id)

    if not identity:
        raise HTTPNotFound()

    return 200, {"data": identity}


@require_request_model(Identity)
async def handle_update_identity(request, identity):
    """
    Handler for updating an Identity. The request is expected to contain at
    least a partial JSON representation of the Identity model object.
    """
    id = request.match_info["id"]
    identity.id = id
    await identity.save()
    return 200, {"data": identity}


async def handle_delete_identity(request):
    """
    Handler for deleting an Identity with a given id.
    """
    id = request.match_info["id"]
    await Identity.get(id).delete()
    return 204, None
