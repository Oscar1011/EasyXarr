import sys

import tmdbsimple as tmdb
import yaml
from Pusher import PushToEnterpriseWechat as Push
import Logger

try:
    Logger.info("[TMDB 初始化]正在加载配置")
    with open("config/Setting.yml", "r", encoding="utf-8") as f:
        Setting = yaml.safe_load(f)
        tmdb_key = Setting["Others"]["TMDBApiKey"]
        tmdb.API_KEY = tmdb_key
        image_server = Setting["Others"]["ImageServer"]
        wxhost = Setting["Others"]["WxHost"]

    Logger.success("[TMDB 初始化]配置加载完成")
except Exception:
    ExceptionInformation = sys.exc_info()
    Text = f'[TMDB 初始化异常]异常信息为:{ExceptionInformation}'
    Logger.error(Text)


def movies_now_playing():
    movies = tmdb.Movies()
    Logger.info(movies.now_playing(language='zh'))
    _push_movies(movies.results)


def movies_popular():
    movies = tmdb.Movies()
    Logger.info(movies.popular(language='zh'))
    _push_movies(movies.results)


def movies_latest():
    movies = tmdb.Movies()
    Logger.info(movies.latest(language='zh'))
    _push_movies(movies.results)


def movies_top_rated():
    movies = tmdb.Movies()
    Logger.info(movies.top_rated(language='zh'))
    _push_movies(movies.results)


def movies_upcoming():
    movies = tmdb.Movies()
    Logger.info(movies.upcoming(language='zh'))
    _push_movies(movies.results)


def _push_movies(movies):
    moviesinfo = []
    for movie in movies:
        if image_server:
            picurl = f'{image_server}/api?url=https://image.tmdb.org/t/p/original/{movie["backdrop_path"]}&width=1068&height=455&format=webp'
        else:
            picurl = f'https://image.tmdb.org/t/p/original/{movie["backdrop_path"]}'
        info = {'title': movie['title'],
                'url': f'{wxhost}/addMovie?tmdbId={movie["id"]}',
                'picurl': picurl,
                'overview': movie['overview']}
        moviesinfo.append(info)
    if len(moviesinfo) > 8:
        push_search_result(moviesinfo[0:8])
    else:
        push_search_result(moviesinfo)


def _push_tv(tmdb_tv):
    tv_info = []
    for tv in tmdb_tv:
        id_info = tmdb.TV(tv["id"]).external_ids(language='zh')
        if image_server:
            picurl = f'{image_server}/api?url=https://image.tmdb.org/t/p/original/{tv["backdrop_path"]}&width=1068&height=455&format=webp'
        else:
            picurl = f'https://image.tmdb.org/t/p/original/{tv["backdrop_path"]}'
        info = {'title': tv['name'],
                'url': f'{wxhost}/addSeries?tvdbId={id_info["tvdb_id"]}',
                'picurl': picurl,
                'overview': tv['overview']}
        tv_info.append(info)
    if len(tv_info) > 8:
        push_search_result(tv_info[0:8])
    else:
        push_search_result(tv_info)


def tv_airing_today():
    tv = tmdb.TV()
    Logger.info(tv.airing_today(language='zh'))
    _push_tv(tv.results)


def tv_popular():
    tv = tmdb.TV()
    Logger.info(tv.popular(language='zh'))
    _push_tv(tv.results)


def tv_latest():
    tv = tmdb.TV()
    Logger.info(tv.latest(language='zh'))
    _push_tv(tv.results)


def tv_top_rated():
    tv = tmdb.TV()
    Logger.info(tv.top_rated(language='zh'))
    _push_tv(tv.results)


def tv_on_the_air():
    tv = tmdb.TV()
    Logger.info(tv.on_the_air(language='zh'))
    _push_tv(tv.results)



def push_search_result(info):
    try:
        Data = []
        if not info or len(info) <= 0:
            return
        elif len(info) == 1:
            Temp = {
                'title': f'{info[0]["title"]}',
                'url': info[0]["url"],
                'picurl': info[0]["picurl"],
                'description': f'介绍：{info[0]["overview"]}',
            }
            Data.append(Temp)
        else:
            for i in range(len(info)):
                Temp = {
                    'title': f'{i + 1}. {info[i]["title"]}',
                    'url': info[i]["url"],
                    'picurl': info[i]["picurl"]
                }
                Data.append(Temp)
        Push("image_text", Articles=Data)

    except Exception:
        ExceptionInformation = sys.exc_info()
        Text = f'[Sonarr]推送,异常信息为:{ExceptionInformation}'
        Logger.error(Text)
        return


def getTMDBInfo(type):
    func = TMBD_FUNC_LIST.get(type, None)
    if func:
        func()


TMBD_FUNC_LIST = {
    'movies_now_playing': movies_now_playing,
    'movies_popular': movies_popular,
    'movies_latest': movies_latest,
    'movies_top_rated': movies_top_rated,
    'movies_upcoming': movies_upcoming,
    'tv_airing_today': tv_airing_today,
    'tv_popular': tv_popular,
    'tv_latest': tv_latest,
    'tv_top_rated': tv_top_rated,
    'tv_on_the_air': tv_on_the_air,
}