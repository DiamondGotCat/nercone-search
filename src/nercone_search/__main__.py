# ┌─────────────────────────────────────────┐
# │ __main__.py on Nercone Search           │
# │ Copyright (c) 2026 DiamondGotCat        │
# │ Made by Nercone / MIT License           │
# └─────────────────────────────────────────┘

import argparse
import uvicorn
import multiprocessing
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from nercone_modern.logging import ModernLogging
from .config import *
from .crawler import crawl
from .embed import embed
from .database import initialize, search, get

app = FastAPI()
logger = ModernLogging(process_name="Nercone Search")

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
    print(list(map(get, search(embed(ns.query), nums=ns.nums))))

@app.api_route("/api/v1/status", methods=["GET"])
async def v1_status(request: Request):
    return JSONResponse(
        {
            "status": "ok",
            "config": {
                "ProductName": ProductName,
                "ProductIdentifier": ProductIdentifier,
                "EmbeddingModel": EmbeddingModel,
                "EmbeddingDimension": EmbeddingDimension,
                "CrawlerName": CrawlerName,
                "CrawlerVersion": CrawlerVersion,
                "CrawlerAdditionalInformations": CrawlerAdditionalInformations,
                "CrawlerRobotsCacheTTL": CrawlerRobotsCacheTTL,
                "CrawlerRobotsCacheSize": CrawlerRobotsCacheSize
            }
        },
        status_code=200
    )

@app.api_route("/api/v1/search", methods=["GET"])
async def v1_search(request: Request):
    if not "query" in request.headers.keys():
        return JSONResponse({"status": "error", "description": "'query'ヘッダーが存在しません。検索するには少なくとも1つのキーワードを'query'ヘッダーに渡す必要があります。"}, status_code=400)
    query = request.headers.get("query", "").strip()
    if query == "":
        return JSONResponse({"status": "error", "description": "'query'ヘッダーに渡された文字列が空です。検索するには少なくとも1つのキーワードを'query'ヘッダーに渡す必要があります。"}, status_code=400)
    try:
        nums = int(request.headers.get("nums", "50"))
    except ValueError:
        return JSONResponse({"status": "error", "description": "'nums'ヘッダーに渡された値が数値ではありません。値は10進数の半角アラビア数字でなければなりません。"}, status_code=400)
    result_ids = search(embed(query), nums=nums)
    result = list(map(get, result_ids))
    return JSONResponse({"status": "ok", "result": result}, status_code=200)

@app.api_route("/api/v1/get", methods=["GET"])
async def v1_search(request: Request):
    if not "id" in request.headers.keys():
        return JSONResponse({"status": "error", "description": "'id'ヘッダーが存在しません。取得したい項目のIDを'id'ヘッダーに渡す必要があります。"}, status_code=400)
    id = request.headers.get("id", "").strip()
    if id == "":
        return JSONResponse({"status": "error", "description": "'id'ヘッダーに渡された文字列が空です。取得したい項目のIDを'id'ヘッダーに渡す必要があります。"}, status_code=400)
    return JSONResponse({"status": "ok", "result": get(id)}, status_code=200)

def serve():
    logger.log("Nercone Search API Server Started.")
    cores_count = multiprocessing.cpu_count()
    logger.log(f"CPU Core Count: {cores_count} Core(s)")
    workers_count = cores_count*2
    logger.log(f"Starting with {workers_count} workers.")
    uvicorn.run("__main__:app", host="0.0.0.0", port=8081, log_level="error", workers=workers_count, server_header=False)
    logger.log("Nercone Search API Server Stopped.")

def main():
    parser = argparse.ArgumentParser(prog=ProductName)
    subparser = parser.add_subparsers(dest="command", required=True)

    cmd_init = subparser.add_parser("init", help="データーベースを初期化")
    cmd_init.add_argument("--exist_ok", type=str_to_bool, default=True, help="既に必要なテーブルが存在する場合にスキップするかどうか")
    cmd_init.set_defaults(func=_cmd_init)

    cmd_serve = subparser.add_parser("serve", help="APIサーバーを起動")
    cmd_serve.set_defaults(func=_cmd_serve)

    cmd_crawl = subparser.add_parser("crawl", help="指定したサイトをクロール")
    cmd_crawl.add_argument("url", type=str, help="クロールするページのURL")
    cmd_crawl.add_argument("--recursive", type=str_to_bool, default=True, help="サイト内にあるリンクをさらにクロールするかどうか")
    cmd_crawl.add_argument("--disallow_ok", type=str_to_bool, default=True, help="robots.txtで拒否された場合に例外を発生させないかどうか")
    cmd_crawl.set_defaults(func=_cmd_crawl)

    cmd_search = subparser.add_parser("search", help="キーワードから検索")
    cmd_search.add_argument("query", type=str, help="クエリ")
    cmd_search.add_argument("--nums", type=int, default=50, help="検索結果数の上限")
    cmd_search.set_defaults(func=_cmd_search)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
