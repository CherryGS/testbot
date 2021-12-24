# testbot

重构中...

## 当前功能

### admin.plugins_global_control

功能

1. ~~自定义插件列表为其他插件提供良好的查询方法~~(官方就挺好)
2. 动态开关插件(总体上)
3. 全局ban人/群(对某插件的使用)

权限: **仅限超级管理员**

加载顺序: **最先**

特殊性

1. 不可被ban
2. 末位启动

指令

`listplugins`

列出所有插件名

`setplugin`

`-p` : 将插件状态反向

`ban`

禁止某人/群使用某插件

`-u` : qq号

`-g` : 群号(不能和qq号同时)

`-p` : 插件名(见 `listplugins` )

`unban`

同上 , 功能相反

## pokepoke

简单的戳一戳响应插件

## repeaterer

简单的复读插件
目前不支持图片(url会改变)
