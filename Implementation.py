import urllib.request
import json
import codecs
from twitchAPI.twitch import Twitch

class YouTuber:

    global GOOGLE_API
    global YouTubeName
    global PlaylistID
    global data
    global videosData
    global oldVideosData
    global userID
    global liveId
    global reader
    isID = False

    def __init__(self, GOOGLE_API_KEY, User, isID = False):

        self.reader = codecs.getreader('utf-8')

        self.GOOGLE_API = GOOGLE_API_KEY
        self.YouTubeName = User
        self.isID = isID

        if not self.isID:
            self.userID = self.getUserID()

        self.PlaylistID = self.setPlaylistID()
        self.data = self.getPlaylistData()
        self.videosData = self.getVideosData(self.data)

    def getUserID(self):

        if self.isID: return self.YouTubeName

        data = json.load(self.reader(urllib.request.urlopen('https://www.googleapis.com/youtube/v3/channels?part=id&forUsername={}&key={}'.format(
            self.YouTubeName, self.GOOGLE_API))))
        return data['items'][0]['id']

    def isUserLive(self):
        data = json.load(self.reader(urllib.request.urlopen('https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={}&type=video&eventType=live&key={}'.format(self.getUserID(), self.GOOGLE_API))))
        if len(data['items']) == 0:
            return False
        if not len(data['items']) == 0:
            self.liveId = self.getUserLiveData()
        return True

    def getUserLiveData(self):
        data = json.load(self.reader(urllib.request.urlopen('https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={}&type=video&eventType=live&key={}'.format(self.getUserID(), self.GOOGLE_API))))
        self.liveId = data['items'][0]['id']['videoId']
        return data['items'][0]['id']['videoId']

    def setPlaylistID(self):
        if self.isID:
            data = json.load(self.reader(urllib.request.urlopen('https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={}&key={}'.format(self.YouTubeName, self.GOOGLE_API))))
            return data['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        data = json.load(self.reader(urllib.request.urlopen('https://www.googleapis.com/youtube/v3/channels?part=contentDetails&forUsername={}&key={}'.format(self.YouTubeName, self.GOOGLE_API))))
        return data['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    def getPlaylistData(self):
        data = json.load(self.reader(urllib.request.urlopen('https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=5&playlistId={}&key={}'.format(self.PlaylistID, self.GOOGLE_API))))
        return data

    def getVideosNrInPlaylist(self):
        i = 0
        for item in self.data['items']:
            i += 1
        return i

    def getVideosData(self, data):
        videosNr = 0
        for item in data['items']:
            videosNr += 1
        videosTitles = []
        videosLinks  = []
        i = 0
        while i < videosNr:
            videosTitles.append(data['items'][i]['snippet']['title'])
            videosLinks.append(data['items'][i]['snippet']['resourceId']['videoId'])
            i += 1
        videosData = []
        for item in videosTitles:
            tempList = []
            tempList.append(item)
            tempList.append(videosLinks[videosTitles.index(item)])
            videosData.append(tempList)
        return videosData

    def getVideoLink(self, videoID):
        return 'https://www.youtube.com/watch?v={}'.format(videoID)

    def update(self):
        self.oldVideosData = self.videosData
        self.data = self.getPlaylistData()
        self.videosData = self.getVideosData(self.data)
        return self.videosData

    def isNewVideo(self):
        if not self.oldVideosData:
            return False
        if (self.oldVideosData[0][0] == self.videosData[0][0]) and (self.oldVideosData[0][1] == self.videosData[0][1]):
            return False
        return True

class Streamer:

    global TWITCH_APP_ID
    global TWITCH_SECRET
    global StreamerName
    global StreamerID
    isID = False

    def __init__(self, TWITCH_APP_ID, TWITCH_SECRET, User, isID = False):

        self.reader = codecs.getreader('utf-8')
        self.TWITCH_APP_ID = TWITCH_APP_ID
        self.TWITCH_SECRET = TWITCH_SECRET
        self.twitch = Twitch(self.TWITCH_APP_ID, self.TWITCH_SECRET)

        self.StreamerName = User
        self.isID = isID
        self.LOCK = False

        if not self.isID:
            self.StreamerID = self.getUserID()




    def getUserID(self):

        if self.isID: return self.StreamerName

        self.twitch.authenticate_app([])
        data = self.twitch.get_users(logins=[self.StreamerName])
        return data['data'][0]['id']


    def isStreaming(self):

        data = self.twitch.get_streams(user_id=self.StreamerID)
        if len(data['data']) != 0:
            if data['data'][0]['type'] == 'live':
                return True
        return False

    def getStreamLink(self): return 'https://www.twitch.tv/' + str(self.StreamerName.lower())

    def lock(self): self.LOCK = True

    def unlock(self): self.LOCK = False

    def lockStatus(self): return self.LOCK

    def getGame(self):

        if self.isStreaming():
            data = self.twitch.get_streams(user_id=self.StreamerID)
            game = data['data'][0]['game_name']
            return game
        return False

    def getViewers(self):

        if self.isStreaming():
            data = self.twitch.get_streams(user_id=self.StreamerID)
            viewers = data['data'][0]['viewer_count']
            return viewers
        return False

    def getTitle(self):

        if self.isStreaming():
            data = self.twitch.get_streams(user_id=self.StreamerID)
            title = data['data'][0]['title']
            return  title
        return False

    def getThumbnail(self):

        if self.isStreaming():
            data = self.twitch.get_streams(user_id=self.StreamerID)
            thumbnail = data['data'][0]['thumbnail_url']
            thumbnail = thumbnail.format(width='1920', height='1080')
            return thumbnail
        return False

    def getProfilePicture(self):

        data = self.twitch.get_users(logins=self.StreamerName)
        picture = data['data'][0]['profile_image_url']
        return picture

    def getStreamerName(self):
        return self.StreamerName
