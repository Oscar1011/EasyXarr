# EasyXarr
用于企业微信交互式的服务，简单控制Sonarr，Radarr

# 使用说明
修改Setting.Sample.yml配置文件， 映射到 /app/config/Setting.yml
企业微信中发送

    电视剧+空格+电视剧名称
or

    电影+空格+电影名称

即会返回搜索到的内容，点击即可添加到 sonarr/radarr 中。

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

菜单功能请打开 https://open.work.weixin.qq.com/wwopen/devtool/interface?doc_id=10786

参考 Menu.json 提交，请勿修改 key 部分内容

说明暂不够完善。有空继续补充
