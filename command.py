from sql import sql

class Command:
    def __init__(self, user_id = None):
        self.sql = sql()
        if(user_id):
            self.user_id = user_id
            self.shard_id = user_id % 2000


    ############################   Photo   ##############################
    def getPhoto(self, photo_id):
        """
        Get information, comments, likes and information of who are commented and liked ont his photo
        """

        photo_info = self.sql.getPhoto(photo_id)
        if len(photo_info) == 0:
            return dict(meta = {'code':400, 'message':'The photo_id provided is not found'})
        else:
            photo_info[0]['id'] = str(photo_info[0]['id'])
            photo_info[0]['create_time'] = str(photo_info[0]['create_time'])

            owner = self.sql.getUserInfo(photo_info[0]['user_id'])
            owner[0]['id'] = str(owner[0]['id'])

            comments = self.sql.getAllComment(photo_id)
            commenter_info = []
            for comment in comments:
                commenter_info.append(self.sql.getUserInfo(comment['user_id']))

            liker_info = self.getLike(photo_id)

            del photo_info[0]['user_id']
            photo_info[0]['user'] = owner[0]

            photo_info[0]['comments'] = {'data':comments, 'count':len(comments)}
            for i in range(0, len(comments)):
                del photo_info[0]['comments']['data'][i]['user_id']
                photo_info[0]['comments']['data'][i]['from'] = commenter_info[0][0]

            photo_info[0]['likes'] = {'data':liker_info, 'count':len(liker_info)}
            return photo_info[0]

    def postPhoto(self, caption, low_url, hight_url, thumnail_url):
        """
        Add new photo and feeds to all follower of this user
        """
        shard_id = self.user_id % 2000
        photo_id = self.sql.getNewID(shard_id)[0]['next_id']
        self.sql.addPhoto(shard_id, photo_id, self.user_id, caption, low_url, hight_url, thumnail_url)
        self.sql.addFeed(self.user_id, photo_id)
        self.sql.addFeedToFollower(self.user_id, photo_id)
        return dict(meta = {'code':200}, data = 'null')


    def deletePhoto(self, photo_id):
        """
        Delete photo and all feed of follower associated with this photo
        """

        photo_info = self.sql.getPhoto(photo_id)
        if len(photo_info) == 0:
            return dict(meta = {'code':400, 'message':'The photo_id provided is not found'})
        if(self.user_id == photo_info[0]['user_id']):
            self.sql.deleteAllFeedOfPhoto(self.user_id, photo_id)
            self.sql.deleteFeed(self.shard_id, self.user_id, photo_id)
            self.sql.deleteAllComment(photo_id)
            self.sql.deleteLikeOfPhoto(photo_id)
            self.sql.deletePhoto(photo_id)
            return dict(meta = {'code':200}, data = 'null')
        else:
            return dict(meta = {'code':401, 'message':'You are not owner of this photo'})


    ############################   Like   ##############################
    def getLike(self, photo_id):
        likers = self.sql.whoLikeThisPhoto(photo_id)
        liker_info = []
        for liker in likers:
            liker_info.append(self.sql.getUserInfo(liker['user_id'])[0])
        return liker_info


    def postLike(self, photo_id):
        photo_info = self.sql.getPhoto(photo_id)
        isLike = self.sql.checkLike(photo_id, self.user_id)
        if len(isLike) == 1:
            return dict(meta = {'code':400, 'message':'You was liked this photo'})
        self.sql.likePhoto(photo_id, self.user_id)
        return dict(meta = {'code':200}, data = 'null')


    def deleteLike(self, photo_id):
        isLike = self.sql.checkLike(photo_id, self.user_id)
        if len(isLike) == 0:
            return dict(meta = {'code':400, 'message':'You was not liked this photo'})
        self.sql.unlikePhoto(photo_id, self.user_id)
        return dict(meta = {'code':200}, data = 'null')


    ############################   Comment   ##############################

    def getComment(self, photo_id):
        photo_info = self.sql.getPhoto(photo_id)
        if len(photo_info) == 0:
            return dict(meta = {'code':400, 'message':'The photo_id provided is not found'})
        else:
            result = self.sql.getAllComment(photo_id)
            for i in range(0, len(result)):
                result[i]['id'] = str(result[i]['id'])
                result[i]['user_id'] = str(result[i]['user_id'])
                result[i]['create_time'] = str(result[i]['create_time'])
            return dict(meta = {'code':200}, data = result)

    def postComment(self, photo_id, text):
        photo_info = self.sql.getPhoto(photo_id)
        if len(photo_info) == 0:
            return {'Error':'Photo not found'}
        else:
            self.sql.addComment(self.user_id, photo_id, text)
            return {'code': 200, 'data': 'success'}


    def deleteComment(self, comment_id):
        comment = self.sql.getComment(int(comment_id))
        if comment[0]['user_id'] == self.user_id:
            self.sql.deleteComment(comment_id)
            return dict(meta = {'code':200}, data = 'null')
        else:
            return dict(meta = {'code':401, 'message':'You are not owner of this comment'})

    ############################   Feed   ##############################
    #Feed GET
    def getFeed(self, count, min_id):
        feeds = self.sql.getFeedOfUser(self.user_id, int(count), int(min_id))
        list_photo_info = []
        for i in range(0, len(feeds)):
            photo_id = feeds[i]['photo_id']
            list_photo_info.append(self.getPhoto(photo_id))
        result = dict(meta = {'code':200}, data = list_photo_info)
        return result


    ############################   User   ##############################
    #User info GET
    def getUserInfo(self, user_id):
        result = self.sql.getUserInfo(user_id)
        if len(result) == 0:
            return dict(meta = {'code':400, 'message':'User not found'})
        else:
            return dict(mega = {'code':200}, data = result)
    #User GET
    #GET user by username
    def getUserByUsername(self, username):
        return self.sql.getUserByUsername(username)

    #User Search
    def searchUser(self, name):
        result = self.sql.searchUser(name)
        return dict(meta = {'code':200}, data = result)

    #User change password
    def changePassword(self, user_id, username, old_password, password, repeat_password):
        pass

    #User change infomation
    def changeUserInfo(self, full_name, email, sex):
        self.sql.changeUserInfo(self.user_id, full_name, email, sex)

    #User change profile_picture
    def changeProfilePicture(self, url):
        self.sql.changeProfilePicture(self.user_id, url)

    def emailExist(self, email):
        result = self.sql.getEmail(email)
        if result:
            return True
        else:
            return False
    ############################   Follow   ##############################
    #Follow GET
    def getFollow(self, user_id):
        #Who are user_id follow
        users = self.sql.getFollow(user_id)
        result = []
        for user in users:
            user_info = self.sql.getUserInfo(user['target_id'])
            result.append(user_info[0])
        return dict(meta = {'code':200}, data = result)

    #Follow by GET
    def getFollowBy(self, user_id):
        #Who are user_id follow-by
        users = self.sql.thisUserFollowBy(user_id)
        result = []
        for user in users:
            user_info = self.sql.getUserInfo(user['user_id'])
            result.append(user_info[0])
        return dict(meta = {'code':200}, data = result)


    ############################   Relationship   ##############################
    #Relationship GET
    def getRelationship(self, target_id):
        #Am i follow this target_id
        if self.sql.checkFollow(self.user_id, target_id):
            return dict(meta = {'code':200}, data = {'follow':'yes'})
        else:
            return dict(meta = {'code':200}, data = {'follow':'no'})

    def postRelationship(self, target_id):
        #Follow target_id
        self.sql.addFollow(self.user_id, target_id)
        return dict(meta = {'code':200}, data = {'follow':'yes'})

    def deleteRelatiohship(self, target_id):
        self.sql.deleteFollow(self.user_id, target_id)
        return dict(meta = {'code':200}, data = {'follow':'no'})

    ############################   Authentication   ##############################
    #Authentication
    def login(self, username, password):
        id = self.sql.checkLogin(username, password)
        return id[0]['id']

    def signup(self, username, password, email):
        self.sql.addUser(username, password, email)
        id = self.sql.checkLogin(username, password)
        return id[0]['id']


