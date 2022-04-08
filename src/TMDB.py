import sys

import tmdbsimple as tmdb
import yaml
from Pusher import push_search_result
import Logger

try:
    Logger.info("[TMDB 初始化]正在加载配置")
    with open("config/Setting.yml", "r", encoding="utf-8") as f:
        Setting = yaml.safe_load(f)
        tmdb_key = Setting["Others"]["TMDBApiKey"]
        tmdb.API_KEY = tmdb_key
        image_server = Setting["Others"]["ImageServer"]
        wxhost = Setting["Others"]["WxHost"]
        wxhost_apikey = Setting["Others"]["WxHostApiKey"]

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
    for i in range(len(movies)):
        "poster_path': '/iUYrQyv0p4UncFolsROm81VNbcB.jpg'"
        if i == 0 and movies[i]["backdrop_path"] != 'None':
            picurl = f'https://image.tmdb.org/t/p/original/{movies[i]["backdrop_path"]}'
        else:
            picurl = f'https://image.tmdb.org/t/p/original/{movies[i]["poster_path"]}'
        info = {'title': movies[i]['title'],
                'url': f'{wxhost}/addMovie?apikey={wxhost_apikey}&tmdbId={movies[i]["id"]}',
                'picurl': picurl,
                'overview': movies[i]['overview']}
        moviesinfo.append(info)
    if len(moviesinfo) > 8:
        push_search_result(moviesinfo[0:8])
    else:
        push_search_result(moviesinfo)


def _push_tv(tmdb_tv):
    tv_info = []
    for i in range(len(tmdb_tv)):
        id_info = tmdb.TV(tmdb_tv[i]["id"]).external_ids(language='zh')
        if i == 0 and tmdb_tv[i]["backdrop_path"] != 'None':
            picurl = f'https://image.tmdb.org/t/p/original/{tmdb_tv[i]["backdrop_path"]}'
        else:
            picurl = f'https://image.tmdb.org/t/p/original/{tmdb_tv[i]["poster_path"]}'
        info = {'title': tmdb_tv[i]['name'],
                'url': f'{wxhost}/addSeries?apikey={wxhost_apikey}&tvdbId={id_info["tvdb_id"]}',
                'picurl': picurl,
                'overview': tmdb_tv[i]['overview']}
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
