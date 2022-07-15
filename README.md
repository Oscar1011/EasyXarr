# EasyXarr
用于企业微信交互式的服务，简单控制Sonarr，Radarr

# 使用说明
修改Setting.Sample.yml配置文件， 映射到 /app/config/Setting.yml

- 一键启动命令



      docker run -d -p 8000:8000 --name=easy_xarr --add-host=api.themoviedb.org:13.224.161.90 --add-host=api.themoviedb.org:13.35.67.86 -v /docker/config/Setting.yml:/app/config/Setting.yml oscar1011/easy_xarr:main

- composer配置



      version: "3.8"
      services:
        easy_xarr:
          image: oscar1011/easy_xarr:main
          container_name: easy_xarr
          network_mode: "bridge"
          ports:
            - "8000:8000"
          volumes:
            - /docker/config/Setting.yml:/app/config/Setting.yml
          extra_hosts:
            - "api.themoviedb.org:13.224.161.90"
            - "api.themoviedb.org:13.35.67.86"

开启企业微信应用的api接收消息，获取的Token与EncodingAESKey 填入Setting.yml中重启 easy_xarr 服务。再在api接收消息配置界面点击保存。

菜单功能请前往 [企业微信菜单控制台](https://open.work.weixin.qq.com/wwopen/devtool/interface?doc_id=10786) 配置，
参考 Menu.json 提交，请勿修改 key 部分内容

一切就绪后，企业微信中发送

    电视剧/s+空格+电视剧名称 如：电视剧 开端
or

    电影/m+空格+电影名称 如：m 星球大战

即会返回搜索到的内容，点击即可添加到 sonarr/radarr 中。

菜单返回的内容点击也会自动添加。

# Sonarr/Radarr WebHook
支持 sonarr/radarr 的下载通知 webhook，链接格式如下，apikey对应配置文件中的WxHostApiKey, type为sonarr或radarr

    http(s)://xxx.xxx.xxx:port/XarrNotify?apikey={}&type={}
如
    
    http://192.168.1.2:8989/XarrNotify?apikey=X5h*oF734F7n@$&type=sonarr


# 效果预览
![basic](https://gitee.com/oscar1011/raw/raw/master/easyxarr/20220410144708.jpg)
![basic](https://gitee.com/oscar1011/raw/raw/master/easyxarr/20220410144718.jpg) 

# 交流
[tg群](https://t.me/+6o1Wo7ktTR4yYWU1)

# 开源许可
本项目使用 [GPL-3.0](https://choosealicense.com/licenses/gpl-3.0/) 作为开源许可证。

# 鸣谢
 部分代码使用了 [SeaBot_WX 项目](https://github.com/B1ue1nWh1te/SeaBot_WX)
