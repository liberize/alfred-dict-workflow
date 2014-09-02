# API 例子

详细解释请参照官方文档。

## 有道

URL: <http://fanyi.youdao.com/openapi.do>

方式：`GET`

参数：

* `keyfrom`: "awf-Chinese-Dict"
* `key`: "19965805"
* `version`: "1.1"
* `type`: "data"
* `doctype`: "json"
* `q`: "test"

数据：

```json
{
    "translation": ["测试"],
    "basic": {
        "us-phonetic": "tɛst",
        "phonetic": "test",
        "uk-phonetic": "test",
        "explains": ["n. 试验；检验", "vt. 试验；测试", "vi. 试验；测试", "n. (Test)人名；(英)特斯特"]
    },
    "query": "test",
    "errorCode": 0,
    "web": [{
        "value": ["测试", "试验", "检验"],
        "key": "test"
    }, {
        "value": ["测试工程师", "测试员", "软件测试工程师"],
        "key": "Test Engineer"
    }, {
        "value": ["硬度试验", "硬度测试", "硬度实验"],
        "key": "hardness test"
    }]
}
```

## 爱词霸

URL: <http://dict-co.iciba.com/api/dictionary.php>

方式：`GET`

参数：

* `key`: "E93A321FB1995DF5EC118B51ABAF8DC7",
* `type`: "json",
* `w`: "test"

数据：

```json
{
    "word_name": "test",
    "is_CRI": "1",
    "exchange": {
        "word_pl": ["tests"],
        "word_third": ["tests"],
        "word_past": ["tested"],
        "word_done": ["tested"],
        "word_ing": ["testing"],
        "word_er": "",
        "word_est": ""
    },
    "symbols": [{
        "ph_en": "test",
        "ph_am": "test",
        "ph_other": "",
        "ph_en_mp3": "http:\/\/res.iciba.com\/resource\/amp3\/oxford\/0\/72\/b8\/72b81c9d32113317d5c83a1bd78d85ac.mp3",
        "ph_am_mp3": "http:\/\/res.iciba.com\/resource\/amp3\/1\/0\/09\/8f\/098f6bcd4621d373cade4e832627b4f6.mp3",
        "ph_tts_mp3": "http:\/\/res-tts.iciba.com\/0\/9\/8\/098f6bcd4621d373cade4e832627b4f6.mp3",
        "parts": [{
            "part": "n.",
            "means": ["\u8bd5\u9a8c", "\u8003\u9a8c", "\u6d4b\u9a8c", "\u5316\u9a8c"]
        }, {
            "part": "vt.",
            "means": ["\u6d4b\u9a8c", "\u8003\u67e5", "\u8003\u9a8c", "\u52d8\u63a2"]
        }, {
            "part": "vi.",
            "means": ["\u53d7\u8bd5\u9a8c", "\u53d7\u6d4b\u9a8c", "\u53d7\u8003\u9a8c", "\u6d4b\u5f97\u7ed3\u679c"]
        }]
    }]
}
```

## 百度

URL: <http://openapi.baidu.com/public/2.0/translate/dict/simple>

方式: `GET`

参数：

* `client_id`: "Gh4UZOrtK9cUba2MW4SuTS3T",
* `q`: "test"
* `from`: "en"
* `to`: "zh"

数据：

```json
{
    "errno": 0,
    "data": {
        "word_name": "test",
        "symbols": [{
            "ph_am": "test",
            "ph_en": "test",
            "parts": [{
                "part": "n.",
                "means": ["\u8bd5\u9a8c", "\u8003\u9a8c", "\u6d4b\u9a8c", "\u5316\u9a8c"]
            }, {
                "part": "vt.",
                "means": ["\u6d4b\u9a8c", "\u8003\u67e5", "\u8003\u9a8c", "\u52d8\u63a2"]
            }, {
                "part": "vi.",
                "means": ["\u53d7\u8bd5\u9a8c", "\u53d7\u6d4b\u9a8c", "\u53d7\u8003\u9a8c", "\u6d4b\u5f97\u7ed3\u679c"]
            }]
        }]
    },
    "to": "zh",
    "from": "en"
}
```
