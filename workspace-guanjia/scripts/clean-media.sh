#!/bin/bash
# 每天 23:59 清理前一天及之前的 media 文件
# 只保留今天的文件

set -e

MEDIA_DIR="$HOME/.openclaw/media"
TODAY=$(date +%Y-%m-%d)

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "开始清理 media 目录（保留今天 $TODAY 的文件）"

# 清理 inbound
if [ -d "$MEDIA_DIR/inbound" ]; then
    BEFORE=$(find "$MEDIA_DIR/inbound" -type f | wc -l | tr -d ' ')
    find "$MEDIA_DIR/inbound" -type f ! -newermt "$TODAY" -delete
    AFTER=$(find "$MEDIA_DIR/inbound" -type f | wc -l | tr -d ' ')
    DELETED=$((BEFORE - AFTER))
    log "inbound: 删除 $DELETED 个文件（剩余 $AFTER）"
fi

# 清理 browser
if [ -d "$MEDIA_DIR/browser" ]; then
    BEFORE=$(find "$MEDIA_DIR/browser" -type f | wc -l | tr -d ' ')
    find "$MEDIA_DIR/browser" -type f ! -newermt "$TODAY" -delete
    AFTER=$(find "$MEDIA_DIR/browser" -type f | wc -l | tr -d ' ')
    DELETED=$((BEFORE - AFTER))
    log "browser: 删除 $DELETED 个文件（剩余 $AFTER）"
fi

log "清理完成"
