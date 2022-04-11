import logging
import sys
import threading
from datetime import datetime

import tmdbsimple as tmdb
import yaml
from arrapi import SonarrAPI

import Logger
from Config import IMAGE_SERVER, WXHOST, WXHOST_APIKEY, TMDB_KEY
from Pusher import push_image_text
from Pusher import push_to_enterprise_wechat as Push


class Sonarr:
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
        with Sonarr._lock:
            if not Sonarr._init_flag:
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
                    Logger.success("[Sonarr初始化]配置加载完成")
                except Exception:
                    ExceptionInformation = sys.exc_info()
                    Text = f'[Sonarr初始化异常]异常信息为:{ExceptionInformation}'
                    Logger.error(Text)
                Sonarr._init_flag = True

    @staticmethod
    def add_series(tvdbId=None, tmdbId=None):
        Sonarr()._add_series_internal(tvdbId, tmdbId)

    @staticmethod
    def search(name):
        Sonarr()._search_internal(name)

    def get_all_series(self):
        return self._sonarr.all_series()

    def is_exist(self, tvdb_id=None):
        try:
            series = self._sonarr.get_series(tvdb_id=tvdb_id)
            if series.id is not None:
                return True
        except Exception as e:
            logging.exception(e)
            return False
        return False

    def _add_series_internal(self, tvdbId: int, tmdbId: int = None):
        if self._is_running:
            Push(Message='Sonarr正在搜索或添加剧集')
            return
        self._is_running = True
        try:
            interval = datetime.now() - self._last_search_time
            if interval.total_seconds() > 1800:
                Logger.error('距上次搜索间隔时间太久，请重新搜索后尝试添加')
                Push(Message='🛑距上次搜索间隔时间太久，请重新搜索后尝试添加')
                return
            if tmdbId:
                tmdb.API_KEY = TMDB_KEY
                id_info = tmdb.TV(tmdbId).external_ids(language='zh')
                if id_info.get('tvdb_id'):
                    tvdbId = id_info.get('tvdb_id')
            sonarr_series = self._sonarr.get_series(tvdb_id=tvdbId)
            if sonarr_series:
                tv = self.find_tv_by_tvdb(tvdbId)
                if sonarr_series.id is None:
                    sonarr_series.add(self._root_dir, self._quality_profile_id, self._language_profile_id,
                                      self._monitored, self._season_folder, self._search_for_missing_episodes,
                                      self._unmet_search, self._series_type, self._tag)
                    Logger.success(f'添加【{tv[0]["name"]}】成功')
                    Push(Message=f'👏添加【{tv[0]["name"]}】成功')
                else:
                    Push(Message=f'🛑【{tv[0]["name"]}】已在Sonarr，请勿重复添加')
            else:
                Push(Message=f'🛑Sonarr未检索到该剧集 tvdbId={tvdbId}')
        except Exception:
            ExceptionInformation = sys.exc_info()
            Text = f'[sonarr] 添加剧集异常,异常信息为:{ExceptionInformation}'
            Push(Message=f'添加 tvdbId={tvdbId} 失败')
            Logger.error(Text)
        finally:
            self._is_running = False

    def _search_internal(self, name: str):
        if self._is_running:
            Push(Message='Sonarr正在搜索或添加剧集')
            return
        self._is_running = True
        try:
            sonarr_series = self._sonarr.search_series(name)
            Logger.info(sonarr_series)
            found_series = []
            if sonarr_series and len(sonarr_series) >= 1:
                for series in sonarr_series:
                    tmdb_series = self.find_tv_by_imdb(series.imdbId)
                    Logger.info(tmdb_series)
                    if tmdb_series and len(tmdb_series) >= 1:
                        if tmdb_series[0]["backdrop_path"] != 'None':
                            picurl = f'https://image.tmdb.org/t/p/original/{tmdb_series[0]["backdrop_path"]}'
                        elif IMAGE_SERVER:
                            picurl = f'{IMAGE_SERVER}/api?url={self.get_remote_url(series.images)}&width=1068&height=455&format=webp'
                        else:
                            picurl = f'{self.get_remote_url(series.images)}'
                        series = {
                            'title': f"{tmdb_series[0]['name']}\n🔸{tmdb_series[0]['vote_average'] if tmdb_series[0]['vote_count'] > 10 else '暂无评'}分 {'| ✅已入库' if series.id is None else '| ❎未入库'}",
                            'picurl': picurl,
                            'url': f'{WXHOST}/addSeries?apikey={WXHOST_APIKEY}&tvdbId={series.tvdbId}',
                            'message': tmdb_series[0]['overview']}
                        found_series.append(series)
                        Logger.info(series)
                        if len(found_series) >= 8:
                            break
                push_image_text(found_series)
                self._last_search_time = datetime.now()
            else:
                Push(Message=f'未搜索到电视剧【{name}】')
        except Exception:
            ExceptionInformation = sys.exc_info()
            Text = f'[sonarr]运行异常,异常信息为:{ExceptionInformation}'
            Push(Message=f'搜索【{name}】时出现异常，请查看日志检查错误')
            Logger.error(Text)
        finally:
            self._is_running = False

    def find_tv_by_tvdb(self, tvdb_id):
        tmdb.API_KEY = TMDB_KEY
        external_source = 'tvdb_id'
        find = tmdb.Find(tvdb_id)
        Logger.info(find.info(external_source=external_source, language='zh'))
        return find.tv_results

    def find_tv_by_imdb(self, imdb_id):
        tmdb.API_KEY = TMDB_KEY
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
