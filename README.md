# EasyXarr
用于企业微信交互式的服务，简单控制Sonarr，Radarr

# 使用说明
修改Setting.Sample.yml配置文件， 映射到 /app/config/Setting.yml

    version: "3.8"
    services:
      easy_xarr:
        image: oscar1011/easy_xarr
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

    电视剧+空格+电视剧名称
or

    电影+空格+电影名称

即会返回搜索到的内容，点击即可添加到 sonarr/radarr 中。

菜单返回的内容点击也会自动添加。

# 效果预览
![basic](https://gitee.com/oscar1011/raw/raw/master/easyxarr/c9bfba2e983c2a37b05a9d948c5c5a6.jpg)
![basic](https://gitee.com/oscar1011/raw/raw/master/easyxarr/f0c832f0ed47bf45add370d179e273c.jpg) 



# 鸣谢
 部分代码使用了 [SeaBot_WX 项目](https://github.com/B1ue1nWh1te/SeaBot_WX)
