#!/bin/bash
# 1. Get Doc by ID
get_doc_by_id()
{
    curl -XGET http://cybertron.eng.vmware.com:9200/redhat_kb/kb/750283
}
# 2. Match Query 
match_query()
{
    curl -XGET http://cybertron.eng.vmware.com:9200/redhat_kb/kb/_search -d '{"query":{"match":{"title":"RIP"}}}'
}
# 3. MultiMatch Query
multi_match_query()
{
    curl -XGET http://cybertron.eng.vmware.com:9200/redhat_kb/kb/_search -d '
    {"query":
        {"multi_match":
            {"query":"sysrq_handle_crash __handle_sysrq write_sysrq_trigger",
            "fields":["issue","resolution","diagnostic"]
            }
        }
    }'
}
# 4. RegExp Query
# MIND: regexp match is based on term, I should modify the index to use new tookenizer
regexp_query()
{
            #"issue":"(RIP:) ([0-9a-f]{4}:\[\<[0-9a-f]{16}\>\])  (\[\<[0-9a-f]{16}\>\]) (sysrq_handle_crash.+)\+"
    curl -XGET http://cybertron.eng.vmware.com:9200/redhat_kb/kb/_search -d '
    {"query":
        {"regexp":
            { 
            "issue":"sysrq_handle_crash"
            }
        }
    }'
}
# 5. Index
index()
{
        #"user": "abcd"
    curl -XPUT http://localhost:9200/twitter/tweet/2 -d '{
        "user": "abc abc\negh\n\nzzz"
    }'
    #curl -XGET http://cybertron.eng.vmware.com:9200/twitter/user/kimchy
}
# 6. Index with Pattern Tokenizer
pattern_tokenizer_index()
{
    curl -XPUT http://cybertron.eng.vmware.com:9200/twitter -d '
    {
        "settings" : {
            "analysis" : {
                "analyzer" : {
                    "my_analyzer" : {
                        "tokenizer" : "line_tokenizer"
                    }
                },
                "tokenizer" : {
                    "line_tokenizer" : {
                        "type" : "pattern",
                        "pattern" : "\\\\n",
                        "group":-1
                    }
                }
            }
        }
    }'
    
        #"user": "abc fdfd fd \\nand\\naaa"
    curl -XPUT http://localhost:9200/twitter/tweet/2 -d '{
        "user": "\nabc abc\negh e\n\nzzz"
    }'

    #curl 'localhost:9200/test/_analyze?pretty=1&analyzer=my_edge_ngram_analyzer' -d 'FC Schalke 04'
    # FC, Sc, Sch, Scha, Schal, 04    
}
#index
pattern_tokenizer_index
echo ""
curl -XGET 'localhost:9200/twitter/_analyze?pretty=1' -d 'abc abc\nabc'
curl -XGET 'localhost:9200/twitter/_analyze?pretty=1&analyzer=my_analyzer' -d 'abc abc\nabc'

curl -XGET 'localhost:9200/twitter/tweet/_search?pretty=1&analyzer=my_analyzer&tokenizer=line_tokenizer' -d '
    {"query":
        {
            "regexp":
            {
                "user":"egh"
            }
        }
    }' 
echo ""
 # FC, Sc, Sch, Scha, Schal, 04    
