"""
@Author         :  liuwei
@Version        :  0.0.1
------------------------------------
@File           :  settings.py.py
@Description    :  
@CreateTime     :  2020/3/14 19:48
"""
SUGGEST_SETTINGS = {
    "index": {
        "analysis": {
            "filter": {
                "_pattern": {
                    "type": "pattern_capture",
                    "preserve_original": "1",
                    "patterns": ["([0-9])", "([a-z])"]
                },
                "full_pinyin": {
                    "keep_first_letter": "false",
                    "keep_none_chinese_in_first_letter": "false",
                    "type": "pinyin",
                    "keep_original": "false",
                    "keep_full_pinyin": "true"
                },
                "prefix_pinyin": {
                    "keep_first_letter": "true",
                    "none_chinese_pinyin_tokenize": "false",
                    "type": "pinyin",
                    "keep_original": "false",
                    "keep_full_pinyin": "false"
                }
            },
            "analyzer": {
                "full_pinyin_analyzer": {
                    "filter": ["lowercase", "full_pinyin"],
                    "tokenizer": "standard"
                },
                "prefix_pinyin_analyzer": {
                    "filter": ["lowercase", "prefix_pinyin"],
                    "tokenizer": "standard"
                }
            }
        }
    }
}