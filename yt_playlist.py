# -*- coding: utf-8 -*-

# Sample Python code for youtube.subscriptions.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/code-samples#python

import argparse
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import json
import os

import yt_log
import yt_service as yt

from logging import getLogger, INFO

logger = getLogger(__name__)
logger.setLevel(INFO)
yt_log.init_log(logger)


def main():
    # args parser
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "secretfile",
        help="specify a secret file.",
    )
    parser.add_argument(
        "-p",
        "--playlist",
        action="store_true",
        help="get videos property from playlist. need --playlistid option to specify a playlist id.",
    )
    parser.add_argument(
        "-c",
        "--check",
        action="store_true",
        help="check playlist whether video is exist or not.  need -f option to specify a file name.",
    )
    parser.add_argument(
        "-i",
        "--insert",
        action="store_true",
        help="insert videos to playlist. need --playlistid option to specify a playlist id. "
        "need -f option to specify a json file with videos listed. "
        "json file must be in the format obtained with the --playlist option ",
    )
    parser.add_argument(
        "-C",
        "--createplaylist",
        action="store_true",
        help="create a new playlist. need --titile and --description option to specify a title and a description.",
    )
    parser.add_argument(
        "-D",
        "--deleteplaylist",
        action="store_true",
        help="delete a playlist. need --playlistid option to specify a playlist id.",
    )
    parser.add_argument(
        "-L",
        "--listplaylists",
        action="store_true",
        help="list playlists. need --playlistid option to specify a playlist id. ",
    )

    parser.add_argument("--playlistid", help="specify a playlist id")
    parser.add_argument("-o", "--output", help="specify a output file name")
    parser.add_argument("-f", "--file", help="specify a input file name")
    parser.add_argument("--title", help="specify a title", default="Enter a title")
    parser.add_argument(
        "--description", help="specify a title", default="Enter a description"
    )
    parser.add_argument(
        "--mine", action="store_true", help="specify a whather mine or not."
    )
    parser.add_argument("--maxResults", help="specify a max results.", default=50)
    parser.add_argument(
        "--order",
        action="store_true",
        help="specify whether keep order in playlist.",
    )

    args = parser.parse_args()

    try:
        service = yt.YoutubeService(args.secretfile)
    except OSError as e:
        logger.error(e)
        exit(1)

    if args.playlist:
        # get_videos_from_playlist

        try:
            videos = service.get_videos_from_playlist(args.playlistid)
        except googleapiclient.errors.HttpError as e:
            logger.error(e._get_reason())
            exit(1)

        json_dump = json.dumps(videos, ensure_ascii=False, indent=4)
        if args.output is not None:
            with open(args.output, "w") as f:
                f.write(json_dump)
        else:
            # stdoutに出力
            print(json_dump)

        logger.info("restieved %s items" % len(videos))

    elif args.insert:
        # insert_videos_to_playlist
        logger.info("insert videos to playlist")

        # 追加したい動画のリストをファイルから読む
        videos = []
        with open(args.file, "r") as f:
            videos = [
                i["snippet"]["resourceId"]["videoId"] for i in json.load(f)
            ]
            logger.info("insert %s videos" % len(videos))

        service.insert_videos_to_playlist(args.playlistid, videos, args.order)

    elif args.check:
        # check videos whether exist or not
        logger.info("check videos")
        videos = []
        with open(args.file, "r") as f:
            videos = [i["snippet"]["resourceId"]["videoId"] for i in json.load(f)]

        for v in videos:
            try:
                result = service.get_video_by_id(v)
                if result["items"] == []:
                    logger.info("not found video %s" % v)
            except googleapiclient.errors.HttpError as e:
                logger.error(e._get_reason())
                continue
        logger.info("finished check videos")
    elif args.createplaylist:
        # create playlist
        logger.info("create a new playlist")
        playlistid = service.create_playlist(args.title, args.description)
        logger.info("created playlistid=%s" % playlistid)
    elif args.deleteplaylist:
        # delete playlist
        logger.info("delete a playlist")
        service.delete_playlist(args.playlistid)
        logger.info("deleted playlistid=%s" % args.playlistid)
    elif args.listplaylists:
        # list playlists
        result = service.list_playlists()
        if args.output is not None:
            with open(args.output, "w") as f:
                f.write(json.dumps(result, ensure_ascii=False, indent=4))
        else:
            for i in result["items"]:
                print("{0} {1}".format(i["snippet"]["title"], i["id"]))


if __name__ == "__main__":
    main()
