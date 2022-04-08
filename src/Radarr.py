import sys
import threading

import yaml
from arrapi import RadarrAPI

import tmdbsimple as tmdb
import Logger

from Pusher import push_to_enterprise_wechat as Push
from Pusher import push_search_result


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
                    self._tag = Setting["Radarr"]["Tag"]

                    self._image_server = Setting["Others"]["ImageServer"]
                    self._proxy = Setting["Others"]["Proxy"]
                    self._tmdb_key = Setting["Others"]["TMDBApiKey"]
                    self._wxhost = Setting["Others"]["WxHost"]
                    self._wxhost_apikey = Setting["Others"]["WxHostApiKey"]

                    Logger.success("[Radarr初始化]配置加载完成")
                except Exception:
                    ExceptionInformation = sys.exc_info()
                    Text = f'[Radarr初始化异常]异常信息为:{ExceptionInformation}'
                    Logger.error(Text)
                Radarr._init_flag = True

    @staticmethod
    def add_movie(tmdbId):
        Radarr()._add_movies_internal(tmdbId)

    @staticmethod
    def search(name):
        Radarr()._search_internal(name)

    def _add_movies_internal(self, tmdbId: int):
        if self._is_running:
            Push(Message='Radarr正在搜索或添加电影')
            return
        self._is_running = True
        try:
            radarr_movies = self._radarr.get_movie(tmdb_id=tmdbId)
            if radarr_movies:
                movie = self.find_movie_by_tmdb(tmdbId)
                if radarr_movies.added.year < 1990:
                    radarr_movies.add(self._root_dir, self._quality_profile_id, self._monitored, self._search,
                                      self._minimum_availability, self._tag)
                    Push(Message=f'👏添加【{movie["title"]}】成功')
                else:
                    Push(Message=f'🛑【{movie["title"]}】已在Radarr，请勿重复添加')
            else:
                Push(Message=f'Radarr未检索到该剧集 tmdb_id={tmdbId}')
        except Exception:
            ExceptionInformation = sys.exc_info()
            Text = f'[Radarr] 添加电影异常,异常信息为:{ExceptionInformation}'
            Push(Message=f'🛑添加 tmdb_id={tmdbId} 失败')
            Logger.error(Text)
        finally:
            self._is_running = False

    def _search_internal(self, name: str):
        if self._is_running:
            Push(Message='Radarr正在搜索或添加电影')
            return
        self._is_running = True
        try:
            radarr_movies = self._radarr.search_movies(name)
            Logger.info(radarr_movies)
            find_series = []
            if radarr_movies and len(radarr_movies) >= 1:
                for movies in radarr_movies:
                    tmdb_movies = self.find_movie_by_imdb(movies.imdbId)
                    Logger.info(tmdb_movies)
                    if tmdb_movies and len(tmdb_movies) >= 1:
                        if tmdb_movies[0]["backdrop_path"] != 'None':
                            picurl = f'https://image.tmdb.org/t/p/original/{tmdb_movies[0]["backdrop_path"]}'
                        elif self._image_server:
                            picurl = f'{self._image_server}/api?url={self.get_remote_url(movies.images)}&width=1068&height=455&format=webp'
                        else:
                            picurl = f'{self.get_remote_url(movies.images)}'
                        movies = {'title': tmdb_movies[0]['title'],
                                  'url': f'{self._wxhost}/addMovie?apikey={self._wxhost_apikey}&tmdbId={movies.tmdbId}',
                                  'picurl': picurl,
                                  'overview': tmdb_movies[0]['overview']}
                        find_series.append(movies)
                        Logger.info(movies)
                push_search_result(find_series)

            return ''
        except Exception:
            ExceptionInformation = sys.exc_info()
            Text = f'[Radarr]运行异常,异常信息为:{ExceptionInformation}'
            Logger.error(Text)
        finally:
            self._is_running = False

    def find_movie_by_tmdb(self, tmdb_id):
        tmdb.API_KEY = self._tmdb_key
        info = tmdb.Movies(tmdb_id).info(language='zh')
        Logger.info(info)
        return info

    def find_movie_by_imdb(self, imdb_id):
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
