import yt_service as yt

service = yt.YoutubeService("secret.json")


def test_insert_videos_to_playlist():

    id = service.create_playlist("test", "test")

    videos = ["QHz1Rs6lZHQ"]
    service.insert_videos_to_playlist(id, videos)

    result = service.get_videos_from_playlist(id)
    assert result[0]["contentDetails"]["videoId"] == "QHz1Rs6lZHQ"

    service.delete_playlist(id)
