from django.db import connection
import calendar
import time

shard_name = "test"

class sql:

    def shard(self, user_id):
        #Return Shard ID with user_id
        return user_id % 2000

    def __init__(self):
        self.cursor = connection.cursor()

    def __del__(self):
        self.cursor.close()

    def dictfetchall(self):
        "Returns all rows from a cursor as a dict"
        desc = self.cursor.description
        return [
            dict(zip([col[0] for col in desc], row))
            for row in self.cursor.fetchall()
        ]

    def getNewID(self, shard_id):
        #Call next_id() function of Shard ID and return it's ID
        self.cursor.execute("SELECT %s%s.next_id()" %(shard_name, shard_id))
        return self.dictfetchall()

    #--Likes

    def likePhoto(self, photo_id, user_id):
        #User_id likes photo_id
        shard_id = (photo_id >> 10) & 8191
        self.cursor.execute("INSERT INTO %s%s.likes(user_id, photo_id) VALUES(%d, %d);" %(shard_name, shard_id, user_id, photo_id))

    def unlikePhoto(self, photo_id, user_id):
        #User_id unlikes photo_id
        shard_id = (photo_id >> 10) & 8191
        self.cursor.execute("DELETE FROM %s%s.likes WHERE user_id = %d AND photo_id = %d;" %(shard_name, shard_id, user_id, photo_id))

    def deleteLikeOfPhoto(self, photo_id):
        shard_id = (photo_id >> 10) & 8191
        self.cursor.execute("DELETE FROM %s%s.likes WHERE photo_id = %d" %(shard_name, shard_id, photo_id))

    def whoLikeThisPhoto(self, photo_id):
        #Return list about who like this photo with photo_id
        shard_id = (photo_id >> 10) & 8191
        self.cursor.execute("SELECT user_id FROM %s%s.likes WHERE photo_id = %d" %(shard_name, shard_id, photo_id))
        return self.dictfetchall()

    def checkLike(self, photo_id, user_id):
        shard_id = (photo_id >> 10) & 8191
        self.cursor.execute("SELECT user_id FROM %s%s.likes WHERE user_id = %d AND photo_id = %d" %(shard_name, shard_id, user_id, photo_id))
        return self.dictfetchall()
    #--Comments


    def getAllComment(self, photo_id):
        #Get all comments on photo
        shard_id = (photo_id >> 10) & 8191
        self.cursor.execute("SELECT id, user_id, text, create_time FROM %s%s.comments WHERE photo_id = %d" %(shard_name, shard_id, photo_id))
        return self.dictfetchall()

    def deleteComment(self, comment_id):
        #Delete comment with comment_id
        shard_id = (comment_id >> 10) & 8191
        self.cursor.execute("DELETE FROM %s%s.comments WHERE id = %d" %(shard_name, shard_id, comment_id))

    def deleteAllComment(self, photo_id):
        #Delete all comments of photo_id
        shard_id = (photo_id >> 10) & 8191
        self.cursor.execute("DELETE FROM %s%s.comments WHERE photo_id = %d" %(shard_name, shard_id, photo_id))

    def addComment(self, user_id, photo_id, text):
        #Add comment to photo_id
        shard_id = (photo_id >> 10) & 8191
        now = calendar.timegm(time.gmtime())
        self.cursor.execute("INSERT INTO %s%s.comments(user_id, photo_id, text, create_time) VALUES(%d, %d, '%s', %d)" %(shard_name, shard_id, user_id, photo_id, text, now))

    def getComment(self, comment_id):
        shard_id = (comment_id >> 10) & 8191
        self.cursor.execute("SELECT * from %s%s.comments WHERE id = %d" %(shard_name, shard_id, comment_id))
        return self.dictfetchall()

    #--Users
    def getUserInfo(self, user_id):
        #Get basic infomation of user
        self.cursor.execute("SELECT username, full_name, id, profile_picture FROM users WHERE id = %d" %(user_id))
        return self.dictfetchall()

    def addUser(self, user_name, password, email):
        now = calendar.timegm(time.gmtime())
        self.cursor.execute("INSERT INTO users(username, password, email, create_time) VALUES('%s', '%s', '%s', %d)" %(user_name, password, email, now))

    def getUserByUsername(self, username):
        #Get all infomations of a user
        self.cursor.execute("SELECT * FROM users WHERE username = '%s'" %(username))
        return self.dictfetchall()

    def searchUser(self, name):
        #Search user with name
        self.cursor.execute("SELECT id, username, full_name, profile_picture FROM users WHERE full_name LIKE '%%%s%%'" %(name))
        return self.dictfetchall()

    def changePassword(self, user_id, new_password):
        self.cursor.execute("UPDATE users SET password = '%s' WHERE id = %d" %(new_password, user_id))

    def changeUserInfo(self, user_id, full_name, email, sex):
        #Change basic infomations of user
        self.cursor.execute("UPDATE users SET full_name = %s, email = %s, sex = %s WHERE user_id = %d" %(full_name, email, sex, user_id))

    def changeProfilePicture(self, user_id, url):
        self.cursor.execute("UPDATE users SET profile_picture = %s WHERE user_id = %d" %(url, user_id))

    def checkLogin(self, username, password):
        self.cursor.execute("SELECT id FROM users WHERE username = '%s' AND password = '%s'" %(username, password))
        return self.dictfetchall()

    def getEmail(self, email):
        self.cursor.execute("SELECT email FROM users WHERE email = '%s'" %(email))
        return self.dictfetchall()

    #--Photos
    def getPhoto(self, photo_id):
        #Get photo information
        shard_id = (photo_id >> 10) & 8191
        if shard_id > 2000:
            return
        self.cursor.execute("SELECT * FROM %s%s.photos WHERE id = %d" %(shard_name, shard_id, photo_id))
        return self.dictfetchall()

    def addPhoto(self, shard_id, photo_id, user_id, caption, low_url, hight_url, thumnail_url):
        #Add new photo
        now = calendar.timegm(time.gmtime())
        self.cursor.execute("INSERT INTO %s%s.photos(id, user_id, caption, low_resolution, hight_resolution, thumnail, create_time)\
            VALUES(%d, %d, '%s', '%s', '%s', '%s', %d)" %(shard_name, shard_id, photo_id, user_id, caption, low_url, hight_url, thumnail_url, now))

    def deletePhoto(self, photo_id):
        #Delete photo with photo_id
        shard_id = (photo_id >> 10) & 8191
        self.cursor.execute("DELETE FROM %s%s.photos WHERE id = %d" %(shard_name, shard_id, photo_id))

    #--Feeds
    def addFeed(self, user_id, photo_id):
        #Add new feed
        shard_id = user_id % 2000
        self.cursor.execute("INSERT INTO %s%s.feeds(user_id, photo_id) VALUES(%d, %d)" %(shard_name, shard_id, user_id, photo_id))

    def addFeedToFollower(self, user_id, photo_id):
        #Add feed to follower
        follower_list = self.thisUserFollowBy(user_id)
        for follower in follower_list:
            shard_id = self.shard(follower['user_id'])
            self.addFeed(follower['user_id'], photo_id)

    def getFeedOfUser(self, user_id, count,  min_id):
        shard_id = self.shard(user_id)
        if min_id == 0:
            self.cursor.execute("SELECT * FROM %s%s.feeds WHERE user_id = %d ORDER BY photo_id DESC LIMIT(%d)" %(shard_name, shard_id, user_id, count))
        else:
            self.cursor.execute("SELECT * FROM %s%s.feeds WHERE user_id = %d AND photo_id < %d ORDER BY photo_id DESC LIMIT(%d)" %(shard_name, shard_id, user_id, min_id, count))
        return self.dictfetchall()

    def deleteFeed(self, shard_id, user_id, photo_id):
        #Delete feed
        self.cursor.execute("DELETE FROM %s%s.feeds WHERE user_id = %d AND photo_id = %d" %(shard_name, shard_id, user_id, photo_id))

    def deleteAllFeedOfPhoto(self, user_id, photo_id):
        follower_list = self.thisUserFollowBy(user_id)
        for follower in follower_list:
            shard_id = self.shard(follower['user_id'])
            self.deleteFeed(shard_id, follower['user_id'], photo_id)

    #--Follows
    #When user add new photo, add photo_id to all follower
    def getFollow(self, user_id):
        #Who are this user follows
        self.cursor.execute("SELECT target_id FROM follows WHERE user_id = %d" %(user_id))
        return  self.dictfetchall()
    #
    def thisUserFollowBy(self, user_id):
        #Who are this user follow-by
        self.cursor.execute("SELECT user_id FROM follows WHERE target_id = %d" %(user_id))
        return self.dictfetchall()

    def addFollow(self, user_id, target_id):
        #Add new follow
        self.cursor.execute("INSERT INTO follows(user_id, target_id) VALUES(%d, %d)" %(user_id, target_id))

    def deleteFollow(self, user_id, target_id):
        #Delete follow
        self.cursor.execute("DELETE FROM follows WHERE user_id = %d AND target_id = %d" %(user_id, target_id))

    def checkFollow(self, user_id, target_id):
        #Check if user_id follow target_id
        self.cursor.execute("SELECT target_id FROM follows WHERE user_id = %d AND target_id = %d" %(user_id, target_id))
        return self.dictfetchall()







