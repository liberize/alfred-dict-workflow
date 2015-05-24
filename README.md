# Alfred 查词扩展

多功能、快速、易用的 Alfred 查词扩展。

## 简介

* 支持的词典：
    * 系统词典，支持朗道、牛津词典
    * 有道在线词典
    * 爱词霸在线词典
    * 百度在线词典
    * 必应在线词典
* 支持英汉、汉英互查
* 支持音标，默认显示美式音标
* 使用系统 TTS 引擎发音
* 可快速复制释义
* 可使用快捷键进行词典切换
* 缓存查询结果，方便下次查询
* 支持快捷键取词

## 截图

![screenshot](https://github.com/liberize/alfred-dict-workflow/raw/master/screenshot.gif)

## 查词用法

关键词为 `dict`，默认使用系统词典，使用以下格式指定词典：

    dict {word} @ {dict}

词典代号及切换快捷键：

词典      | 代号        | 快捷键
-------- | ----------- | ---------
系统     | sys, system  | `⌘` `↩`
有道     | yd, youdao   |  `⌥` `↩`
爱词霸   | cb, iciba     | `⌃` `↩`
百度     | bd, baidu    | `⇧` `↩`
必应     | by, bing     | `fn` `↩`

## 内部命令

使用以下格式执行内部命令：

    dict :{command}

命令     | 参数    | 功能
------- | ------ | ---------------------------------
clean   | 无      | 清除缓存
sysdict | o 或 l  | 设置系统词典，牛津(o)或朗道(l)
defact  | v 或 p  | 设置默认操作，查看完整释义(v)或发音(p)

例如，系统词典默认使用朗道词典，如果想切换为牛津词典，请输入
    
    dict :sysdict o

修改或更新之后，如果想立即生效，请清空缓存：

    dict :clean

## 其他

朗道词典非系统内置，请先[下载](http://pan.baidu.com/s/1qWx4mV6)，然后复制到 `~/Library/Dictionaries/` 目录.

由于必应词典没有提供 API，只能通过解析 HTML 得到，因此速度可能稍慢。

## 联系我

<liberize@gmail.com>
