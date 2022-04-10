from datetime import datetime

import tmdbsimple as tmdb

import Logger
from Config import WXHOST_APIKEY, WXHOST, TMDB_KEY, TV_PREFER_LANGUAGE, TV_PREFER_GENRE_ID, MOVIES_PREFER_LANGUAGE, \
    MOVIES_PREFER_GENRE_ID
from Pusher import push_image_text
from Radarr import Radarr
from Sonarr import Sonarr

tmdb.API_KEY = TMDB_KEY

TV = 1
MOVIE = 2

def movies_now_playing():
    movies = tmdb.Movies()
    _push_movies(get_list(movies.now_playing, MOVIE))


def movies_popular():
    movies = tmdb.Movies()
    _push_movies(get_list(movies.popular, MOVIE))


def movies_latest():
    movies = tmdb.Movies()
    _push_movies(get_list(movies.latest, MOVIE))


def movies_top_rated():
    movies = tmdb.Movies()
    _push_movies(get_list(movies.top_rated, MOVIE))


def movies_upcoming():
    movies = tmdb.Movies()
    _push_movies(get_list(movies.upcoming, MOVIE))


def movies_discover():
    discover = tmdb.Discover()
    discover.movie()


def get_list(fun, type: int):
    prefer_language = None
    prefer_genre_id = None
    if type == TV:
        prefer_language = TV_PREFER_LANGUAGE
        prefer_genre_id = TV_PREFER_GENRE_ID
    elif type == MOVIE:
        prefer_language = MOVIES_PREFER_LANGUAGE
        prefer_genre_id = MOVIES_PREFER_GENRE_ID

    results = []
    tmdb_list = fun(language='zh')
    Logger.info(tmdb_list)
    results.extend(filter_list(tmdb_list['results'], prefer_language, prefer_genre_id))
    if len(results) >= 8:
        return results
    for i in range(1, tmdb_list['total_pages']):
        tmdb_list = fun(language='zh', page=i + 1)
        Logger.info(tmdb_list)
        results.extend(filter_list(tmdb_list['results'], prefer_language, prefer_genre_id))
        if len(results) >= 8:
            return results


def filter_list(tmdb_list, prefer_language, prefer_genre_id):
    if prefer_language and len(prefer_language) > 0:
        lambda_filter = lambda x: x['original_language'] in prefer_language
        tmplist = filter(lambda_filter, tmdb_list)
        tmdb_list = list(tmplist)
    if prefer_genre_id and len(prefer_genre_id) > 0:
        lambda_filter = lambda x: not set(x['genre_ids']).isdisjoint(prefer_genre_id)
        tmplist = filter(lambda_filter, tmdb_list)
        tmdb_list = list(tmplist)
    return tmdb_list


def _push_movies(movies):
    moviesinfo = []
    radarr = Radarr()
    for i in range(len(movies)):
        if i == 0 and movies[i]["backdrop_path"] != 'None':
            picurl = f'https://image.tmdb.org/t/p/original/{movies[i]["backdrop_path"]}'
        else:
            picurl = f'https://image.tmdb.org/t/p/original/{movies[i]["poster_path"]}'
        info = {
            'title': f"{movies[i]['title']}\n🔸{movies[i]['vote_average'] if movies[i]['vote_count'] > 10 else '暂无评'}分 {'| ✅已入库' if radarr.is_exist(tmdb_id=movies[i]['id']) else '| ❎未入库'}",
            'url': f"{WXHOST}/addMovie?apikey={WXHOST_APIKEY}&tmdbId={movies[i]['id']}",
            'picurl': picurl,
            'message': movies[i]['overview']}
        moviesinfo.append(info)
        if len(moviesinfo) >= 8:
            break
    if len(moviesinfo) > 8:
        push_image_text(moviesinfo[0:8])
    else:
        push_image_text(moviesinfo)
    Radarr._last_search_time = datetime.now()


def _push_tv(tmdb_tv):
    tv_info = []
    sonarr = Sonarr()
    for i in range(len(tmdb_tv)):
        id_info = tmdb.TV(tmdb_tv[i]["id"]).external_ids(language='zh')
        if id_info.get('tvdb_id'):
            if i == 0 and tmdb_tv[i]["backdrop_path"] != 'None':
                picurl = f'https://image.tmdb.org/t/p/original/{tmdb_tv[i]["backdrop_path"]}'
            else:
                picurl = f'https://image.tmdb.org/t/p/original/{tmdb_tv[i]["poster_path"]}'
            info = {
                'title': f"{tmdb_tv[i]['name']}\n🔸{tmdb_tv[i]['vote_average'] if tmdb_tv[i]['vote_count'] > 10 else '暂无评'}分 {'| ✅已入库' if sonarr.is_exist(tvdb_id=id_info['tvdb_id']) else '| ❎未入库'}",
                'url': f'{WXHOST}/addSeries?apikey={WXHOST_APIKEY}&tvdbId={id_info["tvdb_id"]}',
                'picurl': picurl,
                'message': tmdb_tv[i]['overview']}
            tv_info.append(info)

        if len(tv_info) >= 8:
            break
    if len(tv_info) > 8:
        push_image_text(tv_info[0:8])
    else:
        push_image_text(tv_info)
    Sonarr._last_search_time = datetime.now()


def tv_airing_today():
    tv = tmdb.TV()
    _push_tv(get_list(tv.airing_today, TV))


def tv_popular():
    tv = tmdb.TV()
    _push_tv(get_list(tv.popular, TV))


def tv_latest():
    tv = tmdb.TV()
    _push_tv(get_list(tv.latest, TV))


def tv_top_rated():
    tv = tmdb.TV()
    _push_tv(get_list(tv.top_rated, TV))


def tv_on_the_air():
    tv = tmdb.TV()
    _push_tv(get_list(tv.on_the_air, TV))


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
