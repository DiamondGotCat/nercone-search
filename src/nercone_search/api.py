from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from nercone_modern.logging import ModernLogging
from .config import *
from .embed import embed
from .database import search, get

app = FastAPI()
logger = ModernLogging(process_name="API")

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
