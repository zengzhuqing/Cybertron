# Cybertron
Cybertron is a  tool for Linux vmcore automatic analysis.

# Modules
dir database: mongo and mysql database setup document
dir elasticsearch: elasticsearch environment setup and some usage example
dir repo_crawler: crawl debuginfo packages for crash
dir retrace_server: from fedora retrace project, including web ui, retrace main module(use crash to handle coredump file), and the parser
dir web_crawler: crawl redhat kb /vmware ikb webpages, load redhat kbs, ikbs, bugzilla data to elasticseach

# About repo crawler
To use repo crawler to crawl debuginfo packages:
1. Create a Crawler object;
2. add seeds(a list of root URLs);
3. add rules(URL links rule. Here, the rule find the dir link);
4. just start
Moreover, just see main in repo_crawler/crawler.py

The debuginfo packages file are downloaded in dir cybertron://cores/retrace/repos/{redhat,centos,opensuse}/Packages.
If some packages have to be downloaded manually, just put them in the corresponding dir

# About repo crawler for redhat
We use three redhat repo server to download redhat debuginfo packages.
Server code is repo_crawler/redhat/server.py, just put it in RHEL5/RHEL6/RHEL7, we will use yumdownloader to download debuginfo packages,
please make sure yumdownloader can be use in the RHEL server.
If the server doesn't work correctly, you can download manaully and put it in cybertron://cores/retrace/repos/redhat/Packages.

# About web crawler
There are two crawler, one is RedHatCrawler(crawl redhat kb webpages), another is IKBCrawler(crawl vmware kb webpages).
To use, just Create RedHatCrawler/IKBCrawler object, then run start on it.
Moreover, just see main in web_crawler/crawler.py
Mind that if you run crawler in terminal environment, you shound run "source web_crawler/in_prepare.sh"

# About elasticsearch setup
just see elasticsearch/setup.sh

# About index data to elasticsearch
use elasticsearch python api to index data to elasticsearch
1. use ElasticSearch.indices.create to create index(can set tokenizer and mappings in doc)
2. use ElasticSearch.index to add a doc to index
source code:
1.load_bugzilla_to_es.py: load bugzilla data in mysql to elasticsearch bugzilla/text/{text,summary}
2.load_redhat_kbs_to_es.py: load redhat kb webpages "issue, env, resolution, rootcause, diagnostic" to redhat_kb/kb/text
3.webpage.py: RedHatWebPage and iKBWebPage parser
4.load_ikbs_to_es.py: load ikb webpages "symptoms, resolution, solution, details, purpose, cause" to ikb/kb/text

# About elasticsearch REST API usage examaple
source code in elasticsearch/examples/
Moreover, just see comments in the examples
strcuture in elasticsearch: index/doc_type/doc
A good online guide:http://www.learnes.net/

# About Retrace Server
to setup, refer to retrace_server/RetraceServer-deployment-guide-ver1.1.txt
main source code: retrace_server/retrace-server-1.12/src/
Use Flask to develop the web application
1. retrace-server-worker will call program "cybertron_parser" when it found kernellog, cybertron_parser will parse kernel log and try to find whether
it has a matched parser, if found, try to get search result from elasticsearch, and write result in file
/cores/retrace/spool/<task_id>/{cybertron_vmbugzilla_matched,cybertron_rhkb_matched} using json format. The json result will be use to show
search result in web.
2.search in cybertron_parser
in function get_search_result of a concrete parser.
It use curl to use elasticsearch REST API in the search.
It use regexp search. REST regexp search can be tested in cmd, you can refer to  # About elasticsearch REST API usage examaple
function get_crash_ip_search_result in cybertron_parser can be a good example.
