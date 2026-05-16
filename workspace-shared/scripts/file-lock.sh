#!/bin/bash
LOCK_DIR=~/.openclaw/workspace-shared/.locks
mkdir -p $LOCK_DIR

case "$1" in
    acquire)
        LOCK_FILE="$LOCK_DIR/$(echo $2 | md5 | awk '{print $1}').lock"
        if [ -f "$LOCK_FILE" ]; then
            LOCK_AGE=$(($(date +%s) - $(stat -f%m "$LOCK_FILE" 2>/dev/null || stat -c%Y "$LOCK_FILE" 2>/dev/null || echo 0)))
            if [ $LOCK_AGE -gt 5 ]; then
                rm -f "$LOCK_FILE"
                echo "$$" > "$LOCK_FILE"
                echo "acquired"
            else
                echo "locked"
            fi
        else
            echo "$$" > "$LOCK_FILE"
            echo "acquired"
        fi
        ;;
    release)
        LOCK_FILE="$LOCK_DIR/$(echo $2 | md5 | awk '{print $1}').lock"
        rm -f "$LOCK_FILE"
        echo "released"
        ;;
    check)
        LOCK_FILE="$LOCK_DIR/$(echo $2 | md5 | awk '{print $1}').lock"
        [ -f "$LOCK_FILE" ] && echo "locked" || echo "free"
        ;;
esac
