import tmdbsimple as tmdb

import Logger
from Config import TMDB_KEY
from Pusher import push_image_text, push_to_enterprise_wechat


def HRS(size):
    units = ('B', 'KB', 'MB', 'GB', 'TB', 'PB')
    for i in range(len(units) - 1, -1, -1):
        if size >= 2 * (1024 ** i):
            return '%.2f' % (size / (1024 ** i)) + ' ' + units[i]


def push_msg_from_detail(detail, title_prefix=''):
    title = ''
    msg = ''
    if detail.get('title'):
        title = detail['title']
        if detail.get('seasonNumber'):
            title += ' S' + detail['seasonNumber'].zfill(2)
        if detail.get('episodeNumbers'):
            title += 'E' + detail['episodeNumbers'].zfill(2)
    if detail.get('quality'):
        msg += '视频质量：' + detail['quality']
    if detail.get('size'):
        msg += '\n视频大小：' + HRS(int(detail['size']))
    if detail.get('path'):
        msg += '\n文件路径：' + detail['path']
    if detail.get('isUpgrade'):
        msg += '\n格式升级：' + ('是' if 'True' == detail['isUpgrade'] else '否')
    if detail.get('deletedFiles'):
        msg += '\n删除文件：' + ('是' if 'True' == detail['deletedFiles'] else '否')
    if detail.get('indexer'):
        msg += '\n抓取来源：' + detail['indexer']

    info = [{'title': f'{title_prefix}{title}',
            'picurl': detail.get('backUrl', ''),
            'url': '',
            'message': msg}]
    Logger.info(info)
    push_image_text(info)


class SonarrData:
    _detail = {}

    def __init__(self, event):
        Logger.warning(event)
        self.type = 'Sonarr'
        self.type_dict = {
            "Grab": self.grab,
            "Download": self.download,
            "Rename": self.rename,
            "EpisodeDeleted": self.episode_deleted,
            "SeriesDeleted": self.series_deleted,
            "HealthIssue": self.health_issue,
            "Test": self.test
        }

        self.title_prefix = {
            "Grab": '开始下载：',
            "Download": '下载完成：',
            "Rename": '',
            "EpisodeDeleted": '文件已删除：',
            "SeriesDeleted": '剧集已删除：',
            "HealthIssue": '',
            "Test": ''
        }

        self._detail['eventType'] = event.get('eventType')

        if event.get('series'):
            self._detail['id'] = event['series'].get('id')
            self._detail['title'] = event['series'].get('title')
            self._detail['tvdbId'] = event['series'].get('tvdbId')
            self._detail['tvMazeId'] = event['series'].get('tvMazeId')
            self._detail['imdbId'] = event['series'].get('imdbId')
            self._detail['path'] = event['series'].get('path')

        if event.get('episodes'):
            season_umber = map(lambda x: str(x['seasonNumber']), event['episodes'])
            self._detail['seasonNumber'] = ','.join(set(season_umber))
            # self._detail['seasonNumber'] = event['episodes'][0].get('seasonNumber')
            episode_number = map(lambda x: str(x['episodeNumber']), event['episodes'])
            self._detail['episodeNumbers'] = ','.join(list(episode_number))
        if event.get('release'):
            self._detail['size'] = event['release'].get('size')
            self._detail['releaseGroup'] = event['release'].get('releaseGroup')
            self._detail['releaseTitle'] = event['release'].get('releaseTitle')
            self._detail['indexer'] = event['release'].get('indexer')
            self._detail['quality'] = event['release'].get('quality')
        self._detail['isUpgrade'] = event.get('isUpgrade')
        self._detail['deletedFiles'] = event.get('deletedFiles')
        if self._detail.get('imdbId'):
            tmdb.API_KEY = TMDB_KEY
            find = tmdb.Find(self._detail.get('imdbId'))
            find.info(external_source='imdb_id', language='zh')
            if len(find.tv_results) > 0:
                self._detail['title'] = find.tv_results[0]['name']
                self._detail['backUrl'] = f'https://image.tmdb.org/t/p/original/{find.tv_results[0]["backdrop_path"]}'

    def grab(self):
        push_msg_from_detail(self._detail, self.title_prefix.get(self._detail.get('eventType')))

    def download(self):
        push_msg_from_detail(self._detail, self.title_prefix.get(self._detail.get('eventType')))

    def rename(self):
        Logger.info("Rename")

    def episode_deleted(self):
        # push_msg_from_detail(self._detail, '文件已删除：')
        Logger.info("EpisodeDeleted")

    def series_deleted(self):
        # push_msg_from_detail(self._detail, '剧集已删除：')
        Logger.info("SeriesDeleted")

    def health_issue(self):
        Logger.info("HealthIssue")

    def default(self):
        Logger.info("Default")

    def test(self):
        Logger.info("test")

        push_to_enterprise_wechat(Title='Sonarr 测试', Message="Sonarr 测试数据")

    def exec(self):
        fun = self.type_dict.get(self._detail.get('eventType'), self.default())
        fun()


class RadarrData:
    _detail = {}

    def __init__(self, event):
        Logger.warning(event)
        self.type = 'Radarr'
        self.type_dict = {
            'Grab': self.grab,
            'Download': self.download,
            'Rename': self.rename,
            'HealthIssue': self.health_issue,
            'ApplicationUpdate': self.application_update,
            'Test': self.test
        }
        self.title_prefix = {
            "Grab": '开始下载：',
            "Download": '下载完成：',
            "Rename": '',
            "HealthIssue": '',
            "Test": ''
        }

        self._detail['eventType'] = event.get('eventType')
        if event.get('movie'):
            self._detail['id'] = event['movie'].get('id')
            self._detail['title'] = event['movie'].get('title')
            self._detail['tmdbId'] = event['movie'].get('tmdbId')
            self._detail['year'] = event['movie'].get('year')
            self._detail['releaseDate'] = event['movie'].get('releaseDate')
        if event.get('remoteMovie'):
            self._detail['tmdbId'] = event['remoteMovie'].get('tmdbId')
            self._detail['imdbId'] = event['remoteMovie'].get('imdbId')
            self._detail['year'] = event['remoteMovie'].get('year')
        if event.get('release'):
            self._detail['quality'] = event['release'].get('quality')
            self._detail['size'] = event['release'].get('size')
            self._detail['releaseGroup'] = event['release'].get('releaseGroup')
            self._detail['releaseTitle'] = event['release'].get('releaseTitle')
            self._detail['indexer'] = event['release'].get('indexer')
        self._detail['isUpgrade'] = event.get('isUpgrade')
        self._detail['deletedFiles'] = event.get('deletedFiles')
        if self._detail.get('imdbId'):
            tmdb.API_KEY = TMDB_KEY
            find = tmdb.Find(self._detail.get('imdbId'))
            find.info(external_source='imdb_id', language='zh')
            if len(find.movie_results) > 0:
                self._detail['title'] = find.movie_results[0]['title']
                self._detail['backUrl'] = f'https://image.tmdb.org/t/p/original/{find.movie_results[0]["backdrop_path"]}'

    def grab(self):
        push_msg_from_detail(self._detail, self.title_prefix.get(self._detail.get('eventType')))

    def download(self):
        push_msg_from_detail(self._detail, self.title_prefix.get(self._detail.get('eventType')))

    def rename(self):
        Logger.info("Rename")

    def application_update(self):
        Logger.info("ApplicationUpdate")

    def health_issue(self):
        Logger.info("HealthIssue")

    def default(self):
        Logger.info("Default")

    def test(self):
        push_to_enterprise_wechat(Title='Radarr 测试', Message="Radarr 测试数据")

    def exec(self):
        fun = self.type_dict.get(self._detail.get('eventType'), self.default())
        fun()
