import sys
import threading

import yaml
from arrapi import SonarrAPI

import tmdbsimple as tmdb
import Logger

from Pusher import PushToEnterpriseWechat as Push


class Sonarr:
    _instance = None
    _lock = threading.Lock()
    _init_flag = False
    _is_running = False
    _last_search_time = 0
    _status = '未运行'

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        with Sonarr._lock:
            if not Sonarr._init_flag:
                self.load_config()
                Sonarr._init_flag = True

    def load_config(self):
        try:
            Logger.info("[Sonarr初始化]正在加载配置")
            with open("config/Setting.yml", "r", encoding="utf-8") as f:
                Setting = yaml.safe_load(f)

            self._sonarr = SonarrAPI(Setting["Sonarr"]["Host"], Setting["Sonarr"]["ApiKey"])
            self._root_dir = Setting["Sonarr"]["RootDir"]
            self._language_profile_id = Setting["Sonarr"]["LanguageProfileId"]
            self._quality_profile_id = Setting["Sonarr"]["QualityProfileId"]
            self._season_folder = Setting["Sonarr"]["SeasonFolder"]
            self._monitored = Setting["Sonarr"]["Monitored"]
            self._search_for_missing_episodes = Setting["Sonarr"]["SearchForMissingEpisodes"]
            self._unmet_search = Setting["Sonarr"]["UnmetSearch"]
            self._series_type = Setting["Sonarr"]["SeriesType"]

            self._tag = Setting["Sonarr"]["Tag"]

            self._image_server = Setting["Others"]["ImageServer"]
            self._proxy = Setting["Others"]["Proxy"]
            self._tmdb_key = Setting["Others"]["TMDBApiKey"]
            self._wxhost = Setting["Others"]["WxHost"]

            Logger.success("[Sonarr初始化]配置加载完成")
        except Exception:
            ExceptionInformation = sys.exc_info()
            Text = f'[Sonarr初始化异常]异常信息为:{ExceptionInformation}'
            Logger.error(Text)

    @staticmethod
    def add_series(tvdbId):
        Sonarr()._add_series_internal(tvdbId)

    @staticmethod
    def search(name):
        Sonarr()._search_internal(name)

    def _add_series_internal(self, tvdbId: int):
        if self._is_running:
            Logger.warning("Sonarr正在搜索或添加剧集")
            Push(Message='Sonarr正在搜索或添加剧集')
            return
        self._is_running = True
        try:
            sonarr_series = self._sonarr.get_series(tvdb_id=tvdbId)
            if sonarr_series:
                if sonarr_series.added.year < 1990:
                    sonarr_series.add(self._root_dir, self._quality_profile_id, self._language_profile_id,
                                      self._monitored, self._season_folder, self._search_for_missing_episodes,
                                      self._unmet_search, self._series_type, self._tag)
                    Logger.success('添加成功')
                    Push(Message='👏添加成功')
                    return
            Push(Message='添加失败')
        except Exception:
            ExceptionInformation = sys.exc_info()
            Text = f'[sonarr] 添加剧集异常,异常信息为:{ExceptionInformation}'
            Push(Message='添加失败')
            Logger.error(Text)
        finally:
            self._is_running = False

    def _search_internal(self, name: str):
        if self._is_running:
            Logger.warning("Sonarr正在搜索或添加剧集")
            Push(Message='Sonarr正在搜索或添加剧集')
            return
        self._is_running = True
        try:
            sonarr_series = self._sonarr.search_series(name)
            Logger.info(sonarr_series)
            find_series = []
            if sonarr_series and len(sonarr_series) >= 1:
                for series in sonarr_series:
                    tmdb_series = self.find_tmdb_by_imdb(series.imdbId)
                    Logger.info(tmdb_series)
                    if tmdb_series and len(tmdb_series) >= 1:
                        if tmdb_series[0]["backdrop_path"] != 'None':
                            picurl = f'https://image.tmdb.org/t/p/original/{tmdb_series[0]["backdrop_path"]}'
                        elif self._image_server:
                            picurl = f'{self._image_server}/api?url={self.get_remote_url(series.images)}&width=1068&height=455&format=webp'
                        else:
                            picurl = f'{self.get_remote_url(series.images)}'
                        series = {'title': tmdb_series[0]['name'],
                                  'picurl': picurl,
                                  'url': f'{self._wxhost}/addSeries?tvdbId={series.tvdbId}',
                                  'overview': tmdb_series[0]['overview']}
                        find_series.append(series)
                        Logger.info(series)
                self.push_search_result(find_series)

            return ''
        except Exception:
            ExceptionInformation = sys.exc_info()
            Text = f'[sonarr]运行异常,异常信息为:{ExceptionInformation}'
            Logger.error(Text)
            return ''
        finally:
            self._is_running = False

    def find_tmdb_by_imdb(self, imdb_id):
        tmdb.API_KEY = self._tmdb_key
        external_source = 'imdb_id'
        find = tmdb.Find(imdb_id)
        Logger.info(find.info(external_source=external_source, language='zh'))
        return find.tv_results

    def get_remote_url(self, images):
        url = ''
        for image in images:
            if image.coverType == 'fanart':
                url = image.remoteUrl
        Logger.info(url)
        return url

    def push_search_result(self, series_info):
        try:
            Data = []
            if not series_info or len(series_info) <= 0:
                Push(Message='未搜索到剧集')
                return
            elif len(series_info) == 1:
                Temp = {
                    'title': f'{series_info[0]["title"]}',
                    'url': series_info[0]["url"],
                    'picurl': series_info[0]["picurl"],
                    'description': f'介绍：{series_info[0]["overview"]}',
                }
                Data.append(Temp)
            else:
                for i in range(len(series_info)):
                    Temp = {
                        'title': f'{i + 1}. {series_info[i]["title"]}',
                        'url': series_info[i]["url"],
                        'picurl': series_info[i]["picurl"]
                    }
                    Data.append(Temp)
            Push("image_text", Articles=Data)

        except Exception:
            ExceptionInformation = sys.exc_info()
            Text = f'[Sonarr]推送,异常信息为:{ExceptionInformation}'
            Logger.error(Text)
            return
