from googleapiclient.discovery import build
import json
from tqdm import tqdm

# API 정보 입력
api_key = 'YOUR_API_KEY'  # Google API key https://console.cloud.google.com
channel_id = 'UCy2WX3w5UyYFHBDHyWFKNUQ'  # 채널 ID 입력
youtube = build('youtube', 'v3', developerKey=api_key)

# 채널의 모든 동영상 ID를 가져오는 함수
def get_channel_videos(channel_id):
    # get Uploads playlist id
    res = youtube.channels().list(
        id=channel_id, 
        part='contentDetails').execute()
    playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    
    videos = []
    next_page_token = None

    while True:
        res = youtube.playlistItems().list(
            playlistId=playlist_id, 
            part='snippet', 
            maxResults=50,
            pageToken=next_page_token).execute()
        videos += res['items']
        next_page_token = res.get('nextPageToken')

        if next_page_token is None:
            break

    return videos

# {'kind': 'youtube#playlistItem', 'etag': '21ocaaawE3Np0EGX3Q-nIDwB2Fk', 'id': 'VVV5MldYM3c1VXlZRkhCREh5V0ZLTlVRLlltbXBJREZZaVNv', 'snippet': {'publishedAt': '2024-03-08T00:00:14Z', 'channelId': 'UCy2WX3w5UyYFHBDHyWFKNUQ', 'title': '살 힘들게 빼지 말고, 이거 드세요! 심지어 맛도 있어...', 'description': '무조건 살 빠지는...\n\n\n이 남자의 cook 네이버 카페(이 남자의 식구들) : https://cafe.naver.com/tmc09\n\n\n+++ 계량 : 밥스푼, 티스푼, 계량컵(200ml)+++\n두부 1모(500g)\n양배추 200g\n청양고추 1개\n소금 1/2작은스푼\n양조간장 1스푼\n들기름 1스푼\n통깨 1스푼\n후추가루 3꼬집\n\n\n#다이어트요리\n#두부요리\n#양배추요리\n#볶음밥\n#두부볶음', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/YmmpIDFYiSo/default.jpg', 'width': 120, 'height': 90}, 'medium': {'url': 'https://i.ytimg.com/vi/YmmpIDFYiSo/mqdefault.jpg', 'width': 320, 'height': 180}, 'high': {'url': 'https://i.ytimg.com/vi/YmmpIDFYiSo/hqdefault.jpg', 'width': 480, 'height': 360}, 'standard': {'url': 'https://i.ytimg.com/vi/YmmpIDFYiSo/sddefault.jpg', 'width': 640, 'height': 480}, 'maxres': {'url': 'https://i.ytimg.com/vi/YmmpIDFYiSo/maxresdefault.jpg', 'width': 1280, 'height': 720}}, 'channelTitle': '이 남자의 cook', 'playlistId': 'UUy2WX3w5UyYFHBDHyWFKNUQ', 'position': 0, 'resourceId': {'kind': 'youtube#video', 'videoId': 'YmmpIDFYiSo'}, 'videoOwnerChannelTitle': '이 남자의 cook', 'videoOwnerChannelId': 'UCy2WX3w5UyYFHBDHyWFKNUQ'}}

# 채널의 모든 동영상 설명 가져오기
def get_videos_descriptions(channel_id):
    videos = get_channel_videos(channel_id)
    videos_descriptions = []

    for video in tqdm(videos):
        video_id = video['snippet']['resourceId']['videoId']
        video_title = video['snippet']['title']
        video_description = video['snippet']['description']
        thumbnails = video['snippet']['thumbnails']
        channel_title = video['snippet']['channelTitle']
        # channel_id = video['snippet']['resourceId']['videoOwnerChannelId']

        videos_descriptions.append({
            'video_id': video_id,
            'title': video_title,
            'description': video_description,
            'thumbnails': thumbnails,
            'channel_title': channel_title,
            'channel_id': channel_id,
        })

    return videos_descriptions

# 메인 실행 부분
if __name__ == '__main__':
    videos_descriptions = get_videos_descriptions(channel_id)
    # print(json.dumps(videos_descriptions, indent=4, ensure_ascii=False))

    # JSON 파일로 저장
    with open(f'data/{channel_id}.json', 'w', encoding='utf-8') as file:
        json.dump(videos_descriptions, file, ensure_ascii=False, indent=4)
