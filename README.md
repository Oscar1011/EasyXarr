# EasyXarr
此分支精简版只支持通知功能

# 使用说明
修改Setting_NotifyOnly.Sample.yml配置文件， 映射到 /app/config/Setting.yml

- 一键启动命令



      docker run -d -p 8000:8000 --name=easy_xarr --add-host=api.themoviedb.org:13.224.161.90 --add-host=api.themoviedb.org:13.35.67.86 -v /docker/config/Setting.yml:/app/config/Setting.yml oscar1011/easy_xarr:notify_only

- composer配置



      version: "3.8"
      services:
        easy_xarr:
          image: oscar1011/easy_xarr:notify_only
          container_name: easy_xarr
          network_mode: "bridge"
          ports:
            - "8000:8000"
          volumes:
            - /docker/config/Setting.yml:/app/config/Setting.yml
          extra_hosts:
            - "api.themoviedb.org:13.224.161.90"
            - "api.themoviedb.org:13.35.67.86"


# Sonarr/Radarr WebHook
支持 sonarr/radarr 的下载通知 webhook，链接格式如下，apikey对应配置文件中的WxHostApiKey, type为sonarr或radarr

    http(s)://xxx.xxx.xxx:port/XarrNotify?apikey={}&type={}
如
    
    http://192.168.1.2:8989/XarrNotify?apikey=X5h*oF734F7n@$&type=sonarr


# 效果预览
![basic](https://gitee.com/oscar1011/raw/raw/master/easyxarr/20220711204250.png)

# 交流
[tg群](https://t.me/+6o1Wo7ktTR4yYWU1)

# 开源许可
本项目使用 [GPL-3.0](https://choosealicense.com/licenses/gpl-3.0/) 作为开源许可证。

# 鸣谢
 部分代码使用了 [SeaBot_WX 项目](https://github.com/B1ue1nWh1te/SeaBot_WX)
