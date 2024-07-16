import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import yt_log
import os
from logging import getLogger, INFO

logger = getLogger(__name__)
logger = yt_log.init_log(logger)
logger.setLevel(INFO)

class YoutubeService:
    def __init__(self, client_secrets_file):
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        self.api_service_name = "youtube"
        self.api_version = "v3"
        self.client_secrets_file = client_secrets_file

        scopes = [
            "https://www.googleapis.com/auth/youtube.readonly",
            "https://www.googleapis.com/auth/youtube.force-ssl",
        ]

        # Get credentials and create an API client
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes
        )

        credentials = flow.run_local_server(open_browser=False)
        self.youtube = googleapiclient.discovery.build(
            self.api_service_name, self.api_version, credentials=credentials
        )

    # 指定されたプレイリストから登録されている動画の情報を取得する

    def get_videos_from_playlist(self, playlistid, maxResults=50):
        # 取得したjsonからitemsのみ取り出して返す
        collection = []
        nextPageToken = ""
        while nextPageToken is not None:
            if nextPageToken == "":
                request = self.youtube.playlistItems().list(
                    part="snippet,contentDetails",
                    playlistId=playlistid,
                    maxResults=maxResults,
                )
            else:
                request = self.youtube.playlistItems().list(
                    part="snippet,contentDetails",
                    playlistId=playlistid,
                    pageToken=nextPageToken,
                    maxResults=maxResults,
                )
            response = request.execute()
            nextPageToken = (
                response["nextPageToken"] if "nextPageToken" in response else None
            )

            collection += response["items"]

            logger.info("retrieving... %s vides" % len(collection))
        return collection

    # insert vides to playlist
    def insert_videos_to_playlist(self, playlistid, videos, order=False):

        # 挿入の重複を避けるために、すでに登録されている動画を取得する
        stored_videos = [
            i["snippet"]["resourceId"]["videoId"]
            for i in self.get_videos_from_playlist(playlistid)
        ]
        position = len(stored_videos)
        # videosを追加する（stored_videosになかったら）
        for i in videos:
            if i in stored_videos:
                # すでに登録されている動画はスキップ
                logger.info("{} is already stored".format(i))
                continue
            logger.info("inserting videoid=%s" % i)
            snippet = {
                "playlistId": playlistid,
                "resourceId": {"kind": "youtube#video", "videoId": i},
            }
            if order:
                snippet["position"] = position
            logger.info(snippet)
            request = self.youtube.playlistItems().insert(
                part="snippet", body={"snippet": snippet}
            )
            try:
                request.execute()
            except googleapiclient.errors.HttpError as e:
                if "Video not found" in e._get_reason():
                    logger.error(e._get_reason())
                    continue
                if "Precondition check failed." in e._get_reason():
                    # 「動画を再生できません」の動画
                    logger.error(e._get_reason())
                    continue
                logger.error(e)
                exit(1)

            logger.info("next position is %s" % position)
            position += 1

    # create playlist
    def create_playlist(self, title, description, status="private"):
        request = self.youtube.playlists().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title,
                    "description": description,
                },
                "status": {
                    "privacyStatus": status,
                },
            },
        )
        response = request.execute()
        return response["id"]

    # delete playlist
    def delete_playlist(self, playlistid):
        request = self.youtube.playlists().delete(id=playlistid)
        response = request.execute()
        return response

    # list playlists
    def list_playlists(self, mine=True, maxResults=50):
        request = self.youtube.playlists().list(
            part="snippet,contentDetails", mine=True, maxResults=maxResults
        )
        response = request.execute()
        return response

    def get_video_by_id(self, id):
        request = self.youtube.videos().list(
            part="snippet,contentDetails,statistics", id=id
        )
        response = request.execute()
        return response

    def get_subscriptions(self, mine=True):
        request = self.youtube.subscriptions().list(
            part="snippet,contentDetails", mine=mine
        )
        return request.execute()

    # ユーザー名からチャンネル情報を取得する
    def get_channel_list_by_username(self, username):
        request = self.youtube.channels().list(
            part="snippet,contentDetails,statistics",
            forUsername=username,
        )
        response = request.execute()
        return response
