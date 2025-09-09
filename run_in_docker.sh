#!/bin/bash
python -m academia_mcp | (sleep 10 && mcpo --port 5001 --server-type "streamable-http" -- http://127.0.0.1:5000/mcp)


