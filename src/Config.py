import sys
import Logger
import yaml

try:
    Logger.info("[主程序初始化]正在加载配置")
    with open("config/Setting.yml", "r", encoding="utf-8") as f:
        Setting = yaml.safe_load(f)

    Host = Setting["Service"]["Host"]
    Port = Setting["Service"]["Port"]

    QWX_Token = Setting["EnterpriseWechat"]["Token"]
    QWX_EncodingAESKey = Setting["EnterpriseWechat"]["EncodingAESKey"]
    CorpID = Setting["EnterpriseWechat"]["CorpID"]
    CorpSecret = Setting["EnterpriseWechat"]["CorpSecret"]
    AgentID = Setting["EnterpriseWechat"]["AgentID"]
    Manager = Setting["EnterpriseWechat"]["ManagerID"]
    TokenApi = Setting["EnterpriseWechat"]["TokenApi"]
    PushApi = Setting["EnterpriseWechat"]["PushApi"]
    PushTitle = Setting["EnterpriseWechat"]["PushTitle"]

    IMAGE_SERVER = Setting["Others"]["ImageServer"]
    WXHOST = Setting["Others"]["WxHost"]
    WXHOST_APIKEY = Setting["Others"]["WxHostApiKey"]
    TMDB_KEY = Setting["Others"]["TMDBApiKey"]

    TV_PREFER_LANGUAGE = Setting["TMDB"]["TVPreferLanguage"]
    TV_PREFER_GENRE_ID = Setting["TMDB"]["TVPreferGenreId"]
    MOVIES_PREFER_LANGUAGE = Setting["TMDB"]["MoviesPreferLanguage"]
    MOVIES_PREFER_GENRE_ID = Setting["TMDB"]["MoviesPreferGenreId"]
    Logger.success("[主程序初始化]配置加载完成")
except Exception:
    ExceptionInformation = sys.exc_info()
    Text = f'[主程序初始化异常]异常信息为:{ExceptionInformation}'
    Logger.error(Text)
    sys.exit(0)