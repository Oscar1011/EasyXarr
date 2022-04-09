import tmdbsimple as tmdb

from Config import WXHOST_APIKEY, WXHOST, TMDB_KEY
from Pusher import push_image_text
import Logger

tmdb.API_KEY = TMDB_KEY


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
                'url': f'{WXHOST}/addMovie?apikey={WXHOST_APIKEY}&tmdbId={movies[i]["id"]}',
                'picurl': picurl,
                'message': movies[i]['overview']}
        moviesinfo.append(info)
    if len(moviesinfo) > 8:
        push_image_text(moviesinfo[0:8])
    else:
        push_image_text(moviesinfo)


def _push_tv(tmdb_tv):
    tv_info = []
    for i in range(len(tmdb_tv)):
        id_info = tmdb.TV(tmdb_tv[i]["id"]).external_ids(language='zh')
        if i == 0 and tmdb_tv[i]["backdrop_path"] != 'None':
            picurl = f'https://image.tmdb.org/t/p/original/{tmdb_tv[i]["backdrop_path"]}'
        else:
            picurl = f'https://image.tmdb.org/t/p/original/{tmdb_tv[i]["poster_path"]}'
        info = {'title': tmdb_tv[i]['name'],
                'url': f'{WXHOST}/addSeries?apikey={WXHOST_APIKEY}&tvdbId={id_info["tvdb_id"]}',
                'picurl': picurl,
                'message': tmdb_tv[i]['overview']}
        tv_info.append(info)
    if len(tv_info) > 8:
        push_image_text(tv_info[0:8])
    else:
        push_image_text(tv_info)


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
