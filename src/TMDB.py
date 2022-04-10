import tmdbsimple as tmdb

import Logger
from Config import WXHOST_APIKEY, WXHOST, TMDB_KEY, PREFER_LANGUAGE, PREFER_GENRE_ID
from Pusher import push_image_text
from Radarr import Radarr
from Sonarr import Sonarr

tmdb.API_KEY = TMDB_KEY


def movies_now_playing():
    movies = tmdb.Movies()
    _push_movies(get_list(movies.now_playing))


def movies_popular():
    movies = tmdb.Movies()
    _push_movies(get_list(movies.popular))


def movies_latest():
    movies = tmdb.Movies()
    _push_movies(get_list(movies.latest))


def movies_top_rated():
    movies = tmdb.Movies()
    _push_movies(get_list(movies.top_rated))


def movies_upcoming():
    movies = tmdb.Movies()
    _push_movies(get_list(movies.upcoming))


def movies_discover():
    discover = tmdb.Discover()
    discover.movie()


def get_list(fun):
    result_movies = []
    movies = fun(language='zh')
    Logger.info(movies)
    result_movies.extend(filter_list(movies['results']))
    if len(result_movies) >= 8:
        return result_movies
    for i in range(1, movies['total_pages']):
        movies = fun(language='zh', page=i + 1)
        Logger.info(movies)
        result_movies.extend(filter_list(movies['results']))
        if len(result_movies) >= 8:
            return result_movies


def filter_list(tmdb_list):
    if PREFER_LANGUAGE and len(PREFER_LANGUAGE) > 0:
        lambda_filter = lambda x: x['original_language'] in PREFER_LANGUAGE
        tmplist = filter(lambda_filter, tmdb_list)
        tmdb_list = list(tmplist)
    if PREFER_GENRE_ID and len(PREFER_GENRE_ID) > 0:
        lambda_filter = lambda x: not set(x['genre_ids']).isdisjoint(PREFER_GENRE_ID)
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


def tv_airing_today():
    tv = tmdb.TV()
    _push_tv(get_list(tv.airing_today))


def tv_popular():
    tv = tmdb.TV()
    _push_tv(get_list(tv.popular))


def tv_latest():
    tv = tmdb.TV()
    _push_tv(get_list(tv.latest))


def tv_top_rated():
    tv = tmdb.TV()
    _push_tv(get_list(tv.top_rated))


def tv_on_the_air():
    tv = tmdb.TV()
    _push_tv(get_list(tv.on_the_air))


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
