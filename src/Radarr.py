import logging
import sys
import threading
from datetime import datetime

import tmdbsimple as tmdb
import yaml
from arrapi import RadarrAPI

import Logger
from Config import IMAGE_SERVER, WXHOST, WXHOST_APIKEY, TMDB_KEY
from Pusher import push_image_text
from Pusher import push_to_enterprise_wechat as Push


class Radarr:
    _instance = None
    _lock = threading.Lock()
    _init_flag = False
    _is_running = False
    _last_search_time = datetime.now()
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

    def is_exist(self, tmdb_id=None, imdb_id=None):
        try:
            movie = self._radarr.get_movie(tmdb_id=tmdb_id, imdb_id=imdb_id)
            if movie.id is not None:
                return True
        except Exception as e:
            logging.exception(e)
            return False
        return False

    def _add_movies_internal(self, tmdbId: int):
        if self._is_running:
            Push(Message='Radarr正在搜索或添加电影')
            return
        self._is_running = True
        try:
            interval = datetime.now() - self._last_search_time
            if interval.total_seconds() > 1800:
                Logger.error('距上次搜索间隔时间太久，请重新搜索后尝试添加')
                Push(Message='🛑距上次搜索间隔时间太久，请重新搜索后尝试添加')
                return
            radarr_movies = self._radarr.get_movie(tmdb_id=tmdbId)
            if radarr_movies:
                movie = self.find_movie_by_tmdb(tmdbId)
                if radarr_movies.id is None:
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
            found_movies = []
            if radarr_movies and len(radarr_movies) >= 1:
                for movies in radarr_movies:
                    tmdb_movies = self.find_movie_by_imdb(movies.imdbId)
                    Logger.info(tmdb_movies)
                    if tmdb_movies and len(tmdb_movies) >= 1:
                        if tmdb_movies[0]["backdrop_path"] != 'None':
                            picurl = f'https://image.tmdb.org/t/p/original/{tmdb_movies[0]["backdrop_path"]}'
                        elif IMAGE_SERVER:
                            picurl = f'{IMAGE_SERVER}/api?url={self.get_remote_url(movies.images)}&width=1068&height=455&format=webp'
                        else:
                            picurl = f'{self.get_remote_url(movies.images)}'

                        info = {
                            'title': f"{tmdb_movies[0]['title']}\n🔸{tmdb_movies[0]['vote_average'] if tmdb_movies[0]['vote_count'] > 10 else '暂无评'}分 {'| ✅已入库' if movies.id is None else '| ❎未入库'}",
                            'url': f'{WXHOST}/addMovie?apikey={WXHOST_APIKEY}&tmdbId={movies.tmdbId}',
                            'picurl': picurl,
                            'message': tmdb_movies[0]['overview']}
                        found_movies.append(info)
                        Logger.info(info)
                        if len(found_movies) >= 8:
                            break
                push_image_text(found_movies)
                self._last_search_time = datetime.now()
            else:
                Push(Message=f'未搜索到电影【{name}】')
            return ''
        except Exception:
            ExceptionInformation = sys.exc_info()
            Text = f'[Radarr]运行异常,异常信息为:{ExceptionInformation}'
            Push(Message=f'搜索【{name}】时出现异常，请查看日志检查错误')
            Logger.error(Text)
        finally:
            self._is_running = False

    def find_movie_by_tmdb(self, tmdb_id):
        tmdb.API_KEY = TMDB_KEY
        info = tmdb.Movies(tmdb_id).info(language='zh')
        Logger.info(info)
        return info

    def find_movie_by_imdb(self, imdb_id):
        tmdb.API_KEY = TMDB_KEY
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
