# ┌─────────────────────────────────────────┐
# │ config.py on Nercone Search             │
# │ Copyright (c) 2026 DiamondGotCat        │
# │ Made by Nercone / MIT License           │
# └─────────────────────────────────────────┘

# General
ProductName = "Nercone Search"
ProductIdentifier = "net.diamondgotcat.search"

# Database
DatabaseHost = "localhost"
DatabasePort = 5432
DatabaseName = "nercone-search"
DatabaseTableName = "pages"
DatabaseUser = "nercone-search"
DatabasePassword = "password"

# Embedding
EmbeddingModel = "Qwen/Qwen3-Embedding-0.6B"
EmbeddingDimension = 1024

# Crawler
CrawlerName = "NerconeBot"
CrawlerVersion = "1.0.0"
CrawlerAdditionalInformations = ["Made by Nercone <nercone@diamondgotcat.net>", "https://github.com/DiamondGotCat/nercone-search/"]
CrawlerRobotsCacheTTL = 2592000
CrawlerRobotsCacheSize = 128
