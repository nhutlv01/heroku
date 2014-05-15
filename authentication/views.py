from command import Command
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
import uuid, hashlib
from django.utils.crypto import constant_time_compare
from rest_framework import status
from rest_framework.decorators import api_view


UNUSABLE_PASSWORD = '!'  # This will never be a valid hash
ALLOWEDCHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)



def get_hexdigest(algorithm, salt, raw_password):
    """
    Returns a string of the hexdigest of the given plaintext password and salt
    using the given algorithm ('md5', 'sha1' or 'crypt').
    """
    raw_password, salt =raw_password.encode('utf-8'), salt.encode('utf-8')
    if algorithm == 'crypt':
        try:
            import crypt
        except ImportError:
            raise ValueError(
                '"crypt" password algorithm not supported in this environment')
        return crypt.crypt(raw_password, salt)

    if algorithm == 'md5':
        return hashlib.md5(salt + raw_password).hexdigest()
    elif algorithm == 'sha1':
        return hashlib.sha1(salt + raw_password).hexdigest()
    raise ValueError("Got unknown password algorithm type in password.")


def get_random_string(length=12, allowed_chars=ALLOWEDCHARS):
    """
    Returns a random string of length characters from the set of a-z, A-Z, 0-9
    for use as a salt.

    The default length of 12 with the a-z, A-Z, 0-9 character set returns
    a 71-bit salt. log_2((26+26+10)^12) =~ 71 bits
    """
    import random
    try:
        random = random.SystemRandom()
    except NotImplementedError:
        pass
    return ''.join([random.choice(allowed_chars) for i in range(length)])


def check_password(raw_password, enc_password):
    """
    Returns a boolean of whether the raw_password was correct. Handles
    encryption formats behind the scenes.
    """
    parts = enc_password.split('$')
    if len(parts) != 3:
        return False
    algo, salt, hsh = parts
    return constant_time_compare(hsh, get_hexdigest(algo, salt, raw_password))


def is_password_usable(encoded_password):
    return (encoded_password is not None
            and encoded_password != UNUSABLE_PASSWORD)


def make_password(algo, raw_password):
    """
    Produce a new password string in this format: algorithm$salt$hash
    """
    if raw_password is None:
        return UNUSABLE_PASSWORD
    salt = get_random_string()
    hsh = get_hexdigest(algo, salt, raw_password)
    return '%s$%s$%s' % (algo, salt, hsh)

@api_view(['POST'])
def login(request):
    if request.method == 'POST':
        c = Command()
        username = request.POST.__getitem__('username')
        password = request.POST.__getitem__('password')
        user = c.getUserByUsername(username)
        if(user):
            if check_password(password, user[0]['password']):
                request.session['user_id'] = user[0]['id']
                return JSONResponse(dict(meta = {'code':200}, data = {'user_id':user[0]['id']}))
            else:
                return JSONResponse(dict(meta = {'code':400, 'message':'Password failed'}), status = status.HTTP_404_NOT_FOUND)
        else:
            return JSONResponse(dict(meta = {'code':400, 'message':'User not found'}), status = status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def logout(request):
    if request.method == 'POST':
        if 'user_id' in request.session:
            del request.session['user_id']
            return JSONResponse(dict(meta = {'code':200}, data = 'null'))
        else:
            return JSONResponse(dict(meta = {'code':401, 'message':'Unauthorized'}), status = status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def signup(request):
    if request.method == 'POST':
        username = request.POST.__getitem__('username')
        password = request.POST.__getitem__('password')
        encrypted_password = make_password('sha1', password)
        email = request.POST.__getitem__('email')
        c = Command()

        if c.getUserByUsername(username):
            return JSONResponse(dict(meta = {'code':400, 'message':'This user is already in use.'}))

        if c.emailExist(email):
            return JSONResponse(dict(meta = {'code':400, 'message':'This email is already in use.'}))

        user_id = c.signup(username,encrypted_password, email)
        request.session['user_id'] = user_id
        return JSONResponse(dict(meta = {'code':200}, data = {'user_id':user_id}))


@api_view(['PUT'])
def changePassword(request):
    if request.method == 'PUT':
        if 'user_id' in request.session:
            user_id = request.session['user_id']
            new_password = request.DATA['new_password']
            encrypted_password = make_password('sha1', new_password)
            c = Command(user_id)
            c.sql.changePassword(user_id, encrypted_password)
            return JSONResponse(dict(meta = {'code':200}, data = 'null'), status = status.HTTP_200_OK)
        else:
            return JSONResponse(dict(meta = {'code':401, 'message':'Unauthorized'}), status = status.HTTP_401_UNAUTHORIZED)
