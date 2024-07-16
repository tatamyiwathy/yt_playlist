# yt_playlist
Get Videos from Playlist / Insert Videos to Playlist

----
出来ること：
- 指定したプレイリストから動画リストを取得する
- 指定したプレイリストに一つ以上の動画を挿入する


動作させるにはGoogle Cloud Consoleでプロジェクトを作成する必要があります。
詳しくは["YouTube Data API の概要"](https://developers.google.com/youtube/v3/getting-started?hl=ja)を確認してください

## インストール

```
$ pip install -r requirements.txt
```


## 使い方

### プレイリストから動画リストを取得する


```--playlistid```で指定したプレイリストから動画リストを取得します。```-o```オプションでファイルへ出力します。

```
$ python yt_playlist.py secret.json -p --playlist PLAYLISTID [-o output.json]
```


### プレイリストへ動画を挿入する

```--playlistid```で指定したプレイリストへ一つ以上の動画を挿入します。挿入位置を固定したいときは```--order```オプションを使用します。（その場合プレイリストの「デフォルトの動画表示順序」が「Youtube内で手動で並べ替え」になっている必要があります）
```
$ python yt_playlist.py -i --playlistid PLAYLISTID -f videos.json　[--order]
```

### 注記

Youtube Data APIへのアクセス割り当てはデフォルトで10000/日あります。
プレイリストへの動画挿入は50消費しますので200個の動画を挿入すると割り当てをすべて消費します。
つまり挿入したい動画が200個以上あると1日では挿入できないことになります。

yt_playlistでは動画挿入時にあらかじめ既存の動画を収集して同じ動画の挿入をしないようにしています。
そのため１日では終わらない挿入も後日挿入時に前回の続きから挿入することになります。

