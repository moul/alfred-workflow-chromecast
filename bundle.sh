#!/bin/bash

# This script will create the Alfred workflow file and optionally it will install it.
# To install it, pass the argument "-i" or "--install", e.g.
# bundle.sh --install

echo "Creating Chromecast workflow file..."

WORKFLOW_FILE=Chromecast.alfredworkflow
if [ -f "$WORKFLOW_FILE" ]; then
    echo "Removing previous workflow..."
    rm "$WORKFLOW_FILE"
fi

echo "Cleaning it..."
find src \( -name "*~" -or -name ".??*~" -or -name "*.pyc" -or -name "#*#" -or -name ".DS_Store" \) -delete

echo "Bundling it..."
cd src && zip -r "../$WORKFLOW_FILE" * && cd ..

while test $# -gt 0
do
    case "$1" in
        --install | -i)
            echo "Installing $WORKFLOW_FILE..."
            open "$WORKFLOW_FILE"
            ;;
    esac
    shift
done

echo "$WORKFLOW_FILE is ready!"
