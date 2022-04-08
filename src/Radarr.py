import sys
import threading

import yaml
from arrapi import RadarrAPI

import tmdbsimple as tmdb
import Logger

from Pusher import PushToEnterpriseWechat as Push


class Radarr:
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
        with Radarr._lock:
            if not Radarr._init_flag:
                self.load_config()
                Radarr._init_flag = True

    def load_config(self):
        try:
            Logger.info("[Radarr初始化]正在加载配置")
            with open("config/Setting.yml", "r", encoding="utf-8") as f:
                Setting = yaml.safe_load(f)

            self._radarr = RadarrAPI(Setting["Radarr"]["Host"], Setting["Radarr"]["ApiKey"])
            self._root_dir = Setting["Radarr"]["RootDir"]
            self._quality_profile_id = Setting["Radarr"]["QualityProfileId"]
            self._monitored = Setting["Radarr"]["Monitored"]
            self._search = Setting["Radarr"]["Search"]
            self._minimum_availability = Setting["Radarr"]["MinimumAvailability"]

            self._image_server = Setting["Others"]["ImageServer"]
            self._proxy = Setting["Others"]["Proxy"]
            self._tmdb_key = Setting["Others"]["TMDBApiKey"]
            self._wxhost = Setting["Others"]["WxHost"]

            Logger.success("[Radarr初始化]配置加载完成")
        except Exception:
            ExceptionInformation = sys.exc_info()
            Text = f'[Radarr初始化异常]异常信息为:{ExceptionInformation}'
            Logger.error(Text)

    @staticmethod
    def add_movie(tmdbId):
        Radarr()._add_movies_internal(tmdbId)

    @staticmethod
    def search(name):
        Radarr()._search_internal(name)

    def _add_movies_internal(self, tmdbId: int):
        if self._is_running:
            Logger.warning("Radarr正在搜索或添加电影")
            Push(Message='Radarr正在搜索或添加电影')
            return
        self._is_running = True
        radarr_movies = self._radarr.get_movie(tmdb_id=tmdbId)
        try:
            if radarr_movies:
                if radarr_movies.added.year < 1990:
                    radarr_movies.add(self._root_dir, self._quality_profile_id, self._monitored, self._search,
                                      self._minimum_availability)
                    Logger.success('添加成功')
                    Push(Message='添加成功')
                    return
            Push(Message='添加失败')
        except Exception:
            ExceptionInformation = sys.exc_info()
            Text = f'[Radarr] 添加电影异常,异常信息为:{ExceptionInformation}'
            Push(Message='添加失败')
            Logger.error(Text)
        finally:
            self._is_running = False

    def _search_internal(self, name: str):
        if self._is_running:
            Logger.warning("Radarr正在搜索或添加电影")
            Push(Message='Radarr正在搜索或添加电影')
            return
        self._is_running = True
        try:
            radarr_movies = self._radarr.search_movies(name)
            Logger.info(radarr_movies)
            find_series = []
            if radarr_movies and len(radarr_movies) >= 1:
                for movies in radarr_movies:
                    tmdb_movies = self.find_tmdb_by_imdb(movies.imdbId)
                    Logger.info(tmdb_movies)
                    if tmdb_movies and len(tmdb_movies) >= 1:
                        if self._image_server:
                            picurl = f'{self._image_server}/api?url={self.get_remote_url(movies.images)}&width=1068&height=455&format=webp'
                        else:
                            picurl = f'{self.get_remote_url(movies.images)}'
                        movies = {'title': tmdb_movies[0]['title'],
                                'url': f'{self._wxhost}/addMovie?tmdbId={movies.tmdbId}',
                                'picurl': picurl,
                                'overview': tmdb_movies[0]['overview']}


                        find_series.append(movies)
                        Logger.info(movies)
                self.push_search_result(find_series)

            return ''
        except Exception:
            ExceptionInformation = sys.exc_info()
            Text = f'[Radarr]运行异常,异常信息为:{ExceptionInformation}'
            Logger.error(Text)
            return ''
        finally:
            self._is_running = False

    def find_tmdb_by_imdb(self, imdb_id):
        tmdb.API_KEY = self._tmdb_key
        external_source = 'imdb_id'
        find = tmdb.Find(imdb_id)
        Logger.info(find.info(external_source=external_source, language='zh'))
        return find.movie_results

    def get_remote_url(self, images):
        url = ''
        for image in images:
            if image.coverType == 'fanart':
                url = image.remoteUrl
        Logger.info(url)
        return url

    def push_search_result(self, movies_info):
        try:
            Data = []
            if not movies_info or len(movies_info) <= 0:
                Push(Message='未搜索到电影')
                return
            elif len(movies_info) == 1:
                Temp = {
                    'title': f'{movies_info[0]["title"]}',
                    'url': movies_info[0]["url"],
                    'picurl': movies_info[0]["picurl"],
                    'description': f'介绍：{movies_info[0]["overview"]}',
                }
                Data.append(Temp)
            else:
                for i in range(len(movies_info)):
                    Temp = {
                        'title': f'{i + 1}. {movies_info[i]["title"]}',
                        'url': movies_info[0]["url"],
                        'picurl': movies_info[0]["picurl"],
                        'description': f'介绍：{movies_info[0]["overview"]}',
                    }
                    Data.append(Temp)
            Push("image_text", Articles=Data)

        except Exception:
            ExceptionInformation = sys.exc_info()
            Text = f'[Radarr]推送,异常信息为:{ExceptionInformation}'
            Logger.error(Text)
            return
