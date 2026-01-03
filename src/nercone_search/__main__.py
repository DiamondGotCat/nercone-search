# ┌─────────────────────────────────────────┐
# │ __main__.py on Nercone Search           │
# │ Copyright (c) 2026 DiamondGotCat        │
# │ Made by Nercone / MIT License           │
# └─────────────────────────────────────────┘

import argparse
from .config import ProductName
from .api import serve
from .crawler import crawl
from .embed import embed
from .database import initialize, search

def str_to_bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("true", "t", "yes", "y", "1"):
        return True
    if v.lower() in ("false", "f", "no", "n", "0"):
        return False
    raise argparse.ArgumentTypeError("Boolean value expected")

def _cmd_init(ns: argparse.Namespace):
    initialize(exist_ok=ns.exist_ok)

def _cmd_serve(ns: argparse.Namespace):
    serve()

def _cmd_crawl(ns: argparse.Namespace):
    crawl(url=ns.url, recursive=ns.recursive, disallow_ok=ns.disallow_ok)

def _cmd_search(ns: argparse.Namespace):
    search(embed(ns.query), nums=ns.nums)

def main():
    parser = argparse.ArgumentParser(prog=ProductName)
    subparser = parser.add_subparsers(dest="command", required=True)

    cmd_init = subparser.add_parser("init", help="データーベースを初期化")
    cmd_init.add_argument("exist_ok", type=str_to_bool, default=True, help="既に必要なテーブルが存在する場合にスキップするかどうか")
    cmd_init.set_defaults(func=_cmd_init)

    cmd_serve = subparser.add_parser("serve", help="APIサーバーを起動")
    cmd_serve.set_defaults(func=_cmd_serve)

    cmd_crawl = subparser.add_parser("crawl", help="指定したサイトをクロール")
    cmd_crawl.add_argument("url", type=str, help="クロールするページのURL")
    cmd_crawl.add_argument("recursive", type=str_to_bool, default=True, help="サイト内にあるリンクをさらにクロールするかどうか")
    cmd_crawl.add_argument("disallow_ok", type=str_to_bool, default=True, help="robots.txtで拒否された場合に例外を発生させないかどうか")
    cmd_crawl.set_defaults(func=_cmd_crawl)

    cmd_search = subparser.add_parser("search", help="キーワードから検索")
    cmd_search.add_argument("query", type=str, required=True, help="クエリ")
    cmd_search.add_argument("nums", type=int, default=50, help="検索結果数の上限")
    cmd_search.set_defaults(func=_cmd_search)

if __name__ == "__main__":
    main()
