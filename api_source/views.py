from command import Command
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from rest_framework import status
from rest_framework.decorators import api_view

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

@api_view(['DELETE','GET'])
def getOrDeletePhoto(request, photo_id):
    """
    For get or delete method
    """
    if request.method == 'GET':
        c = Command()
        result = c.getPhoto(int(photo_id))
        if 'id' in result:
            result = dict(meta = {'code':200}, data = [result])
        return JSONResponse(result)

    ###################################################
    elif request.method == 'DELETE':
        if 'user_id' in request.session:
            user_id = request.session['user_id']
            c = Command(user_id)
            result = c.deletePhoto(int(photo_id))
            return JSONResponse(result)
        else:
            return JSONResponse(dict(meta = {'code':401, 'message':'Authentication required'}), status = status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def postPhoto(request):
    """
    For post method
    """
    if request.method == 'POST':
        if 'user_id' in request.session:
            user_id = request.session['user_id']
            caption = request.POST.__getitem__('caption')
            low_url = request.POST.__getitem__('low_url')
            hight_url = request.POST.__getitem__('hight_url')
            thumnail_url = request.POST.__getitem__('thumnail_url')
            c = Command(user_id)
            result = c.postPhoto(caption, low_url, hight_url, thumnail_url)
            return JSONResponse(result)
        else:
            return JSONResponse(dict(meta = {'code':401, 'message':'Authentication required'}), status = status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def getFeed(request):
    """
    For get feed of user
    """
    if request.method == 'GET':
        if 'user_id' in request.session:
            count = request.GET.__getitem__('count')
            min_id = request.GET.__getitem__('min_id')
            user_id = request.session['user_id']
            c = Command(user_id)
            result = c.getFeed(count, min_id)
            return JSONResponse(result)
        else:
            return JSONResponse(dict(meta = {'code':401, 'message':'Authentication required'}), status = status.HTTP_401_UNAUTHORIZED)



@api_view(['GET', 'POST', 'DELETE'])
def likeAction(request, photo_id):
    """
    GET method is get list of users who likes this photo
    POST is like this photo
    DELETE is unlike this photo
    """
    if request.method == 'GET':
        c = Command()
        result = c.getLike(int(photo_id))
        result = dict(meta = {'code':200}, data = result)
        return JSONResponse(result)

    if request.method == 'POST':
        if 'user_id' in request.session:
            user_id = request.session['user_id']
            c = Command(user_id)
            result = c.postLike(int(photo_id))
            return JSONResponse(result)
        else:
            return JSONResponse(dict(meta = {'code':401, 'message':'Authentication required'}), status = status.HTTP_401_UNAUTHORIZED)

    if request.method == 'DELETE':
        if 'user_id' in request.session:
            user_id = request.session['user_id']
            c = Command(user_id)
            result = c.deleteLike(int(photo_id))
            return JSONResponse(result)
        else:
            return JSONResponse(dict(meta = {'code':401, 'message':'Authentication required'}), status = status.HTTP_401_UNAUTHORIZED)


@api_view(['GET', 'POST'])
def getOrPostComment(request, photo_id):
    """
    Get or Post comment
    """
    if request.method == 'GET':
        c = Command()
        result = c.getComment(int(photo_id))
        return JSONResponse(result)

    if request.method == 'POST':
        if 'user_id' in request.session:
            user_id = request.session['user_id']
            text = request.POST['text']
            c = Command(user_id)
            result = c.postComment(int(photo_id), text)
            return JSONResponse(result)
        else:
            return JSONResponse(dict(meta = {'code':401, 'message':'Authentication required'}), status = status.HTTP_401_UNAUTHORIZED)


@api_view (['DELETE'])
def deleteComment(request, photo_id, comment_id):
    """
    Delete comment
    """
    if request.method == 'DELETE':
        if 'user_id' in request.session:
            user_id = request.session['user_id']
            c = Command(user_id)
            result = c.deleteComment(int(comment_id))
            return JSONResponse(result)
        else:
             return JSONResponse(dict(meta = {'code':401, 'message':'Authentication required'}), status = status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def getUser(request, user_id):
    if request.method == 'GET':
        c = Command()
        result = c.getUserInfo(int(user_id))
        return JSONResponse(result)

@api_view(['GET'])
def searchUser(request):
    if request.method == 'GET':
        name = request.GET['name']
        c = Command()
        result = c.searchUser(name)
        return JSONResponse(result)


@api_view(['GET'])
def follow(request, user_id):
    c = Command()
    result = c.getFollow(int(user_id))
    return JSONResponse(result)

@api_view(['GET'])
def followBy(request, user_id):
    c = Command()
    result = c.getFollowBy(int(user_id))
    return JSONResponse(result)

@api_view(['GET', 'POST', 'DELETE'])
def relationShipAction(request, target_id):
    if request.method == 'GET':
        if 'user_id' in request.session:
            user_id = request.session['user_id']
            c = Command(user_id)
            result = c.getRelationship(int(target_id))
            return JSONResponse(result)
        else:
            return JSONResponse(dict(meta = {'code':401, 'message':'Authentication required'}), status = status.HTTP_401_UNAUTHORIZED)

    if request.method == 'POST':
        if 'user_id' in request.session:
            user_id = request.session['user_id']
            c = Command(user_id)
            result = c.postRelationship(int(target_id))
            return JSONResponse(result)
        else:
            return JSONResponse(dict(meta = {'code':401, 'message':'Authentication required'}), status = status.HTTP_401_UNAUTHORIZED)

    if request.method == 'DELETE':
        if 'user_id' in request.session:
            user_id = request.session['user_id']
            c = Command(user_id)
            result = c.deleteRelatiohship(int(target_id))
            return JSONResponse(result)
        else:
            return JSONResponse(dict(meta = {'code':401, 'message':'Authentication required'}), status = status.HTTP_401_UNAUTHORIZED)
