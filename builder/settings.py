"""
@Author         :  liuwei
@Version        :  0.0.1
------------------------------------
@File           :  settings.py.py
@Description    :  
@CreateTime     :  2020/3/14 19:48
"""
PORTAL_SETTINGS = {
	"settings": {
		"analysis": {
			"filter": {
				"edge_ngram_filter": {
					"type": "edge_ngram",
					"min_gram": 1,
					"max_gram": 50
				},
				"pinyin_simple_filter": {
					"type": "pinyin",
					"keep_first_letter": true,
					"keep_separate_first_letter": false,
					"keep_full_pinyin": false,
					"keep_original": false,
					"limit_first_letter_length": 50,
					"lowercase": true
				},
				"pinyin_full_filter": {
					"type": "'pinyin",
					"keep_first_letter": false,
					"keep_separate_first_letter": false,
					"keep_full_pinyin": true,
					"none_chinese_pinyin_tokenize": true,
					"keep_original": false,
					"limit_first_letter_length": 50,
					"lowercase": true
				}
			},
			"analyzer": {
				"ngramIndexAnalyzer": {
					"type": "custom",
					"tokenizer": "keyword",
					"filter": ["edge_ngram_filter", "lowercase"]
				},
				"ngramSearchAnalyzer": {
					"type": "custom",
					"tokenizer": "keyword",
					"filter": ["lowercase"]
				},
				"pinyiSimpleIndexAnalyzer": {
					"tokenizer": "keyword",
					"filter": ["pinyin_simple_filter", "edge_ngram_filter", "lowercase"]
				},
				"pinyiSimpleSearchAnalyzer": {
					"tokenizer": "keyword",
					"filter": ["pinyin_simple_filter", "lowercase"]
				},
				"pinyiFullIndexAnalyzer": {
					"tokenizer": "keyword",
					"filter": ["pinyin_full_filter", "lowercase"]
				},
				"pinyiFullSearchAnalyzer": {
					"tokenizer": "keyword",
					"filter": ["pinyin_full_filter", "lowercase"]
				}
			}
		}
	},
	"mappings": {
		"properties": {
			"id": {
				"boost": 1.0,
				"index": false,
				"store": true,
				"type": "keyword"
			},
			"title": {
				"boost": 1.0,
				"index": true,
				"store": true,
				"type": "text",
				"analyzer": "ik_max_word",
				"search_analyzer": "ik_smart",
				"term_vector": "with_positions_offsets"
			},
			"url": {
				"boost": 1.0,
				"index": true,
				"store": true,
				"type": "text",
				"analyzer": "ik_max_word",
				"search_analyzer": "ik_smart",
				"term_vector": "with_positions_offsets"
			},
			"desc": {
				"boost": 1.0,
				"index": true,
				"store": true,
				"type": "text",
				"analyzer": "ik_max_word",
				"search_analyzer": "ik_smart",
				"term_vector": "with_positions_offsets"
			},
			"permissions": {
				"type": "text",
				"store": true,
				"index": true
			},
			"breadcrumb": {
				"type": "nested",
				"properties": {
					"id": {
						"index": false,
						"store": true,
						"type": "keyword"
					},
					"title": {
						"store": true,
						"index": true,
						"type": "keyword"
					},
					"url": {
						"store": false,
						"index": false,
						"type": "keyword"
					},
					"desc": {
						"store": false,
						"index": false,
						"type": "text"
					},
					"permissions": {
						"type": "text",
						"store": false,
						"index": false
					}
				}
			}
		}
	}
}