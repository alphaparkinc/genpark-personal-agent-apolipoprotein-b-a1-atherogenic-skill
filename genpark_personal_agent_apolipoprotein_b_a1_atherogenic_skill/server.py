# -*- coding: utf-8 -*-
"""MCP Server for Apolipoprotein B/A1 Ratio & Atherogenic Particle Sentinel Skill."""
import sys
import json
import logging
from typing import Dict, Any

from .core import ApolipoproteinAtherogenicSentinel

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

TOOLS_SCHEMA = [
    {
        "name": "calculate_apob_apoa1_ratio",
        "description": "Compute ApoB / ApoA1 atherogenic ratio to predict coronary heart disease plaque burden independent of LDL-C.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "apob_mg_dl": {
                    "type": "number"
                },
                "apoa1_mg_dl": {
                    "type": "number"
                },
                "gender": {
                    "type": "string",
                    "enum": [
                        "male",
                        "female"
                    ]
                }
            },
            "required": [
                "apob_mg_dl",
                "apoa1_mg_dl"
            ]
        }
    },
    {
        "name": "audit_ldl_apob_discordance",
        "description": "Detect discordance between standard LDL-C and atherogenic particle count (ApoB) indicative of insulin resistance.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ldl_c_mg_dl": {
                    "type": "number"
                },
                "apob_mg_dl": {
                    "type": "number"
                },
                "triglycerides_mg_dl": {
                    "type": "number"
                }
            },
            "required": [
                "ldl_c_mg_dl",
                "apob_mg_dl"
            ]
        }
    }
]

def handle_rpc(line: str) -> str:
    try:
        req = json.loads(line)
        method = req.get("method")
        msg_id = req.get("id")

        if method == "initialize":
            res = {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "genpark-personal-agent-apolipoprotein-b-a1-atherogenic-skill", "version": "1.0.0"}
            }
            return json.dumps({"jsonrpc": "2.0", "id": msg_id, "result": res})

        elif method == "tools/list":
            return json.dumps({"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS_SCHEMA}})

        elif method == "tools/call":
            params = req.get("params", {})
            tool_name = params.get("name")
            args = params.get("arguments", {})

            target_func = getattr(ApolipoproteinAtherogenicSentinel, tool_name, None)
            if not target_func:
                return json.dumps({"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"Method not found: {tool_name}"}})

            result = target_func(**args)
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
                }
            })

        else:
            return json.dumps({"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"Method not found: {method}"}})

    except Exception as e:
        return json.dumps({"jsonrpc": "2.0", "id": req.get("id") if "req" in locals() else None, "error": {"code": -32000, "message": str(e)}})

def run_test():
    init_req = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    init_res = json.loads(handle_rpc(init_req))
    assert init_res.get("result", {}).get("serverInfo", {}).get("name") == "genpark-personal-agent-apolipoprotein-b-a1-atherogenic-skill"

    list_req = json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    list_res = json.loads(handle_rpc(list_req))
    assert len(list_res.get("result", {}).get("tools", [])) == 2
    return True

if __name__ == "__main__":
    if "--test" in sys.argv:
        if run_test():
            sys.exit(0)
        sys.exit(1)

    for line in sys.stdin:
        if not line.strip():
            continue
        out = handle_rpc(line)
        sys.stdout.write(out + "\n")
        sys.stdout.flush()
