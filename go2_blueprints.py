# Copyright 2026. RFID DimOS integration — Go2 + RFID blueprints.
#
# Requires: pip install 'dimos[base,unitree]'

from __future__ import annotations

import os

from dimos.core.coordination.blueprints import autoconnect
from dimos.core.transport import pLCMTransport
from dimos.robot.unitree.go2.blueprints.smart.unitree_go2_spatial import unitree_go2_spatial

from dimos_rfid.msgs import RfidTagArray
from dimos_rfid.rfid_module import RfidModule

_RFID_TRANSPORTS = {
    ("rfid_tags", RfidTagArray): pLCMTransport("/rfid/tags"),
}


def _rfid_module_blueprint():
    return RfidModule.blueprint(
        connection_mode=os.environ.get("RFID_CONNECTION_MODE", "http"),
        api_base=os.environ.get(
            "RFID_API_BASE",
            "http://192.168.123.18:8765/api/v1",
        ),
    )


unitree_go2_rfid = autoconnect(
    unitree_go2_spatial,
    _rfid_module_blueprint(),
).transports(_RFID_TRANSPORTS)

try:
    from dimos.agents.mcp.mcp_client import McpClient
    from dimos.agents.mcp.mcp_server import McpServer
    from dimos.robot.unitree.go2.blueprints.agentic._common_agentic import _common_agentic

    unitree_go2_rfid_agentic = autoconnect(
        unitree_go2_spatial,
        _rfid_module_blueprint(),
        McpServer.blueprint(),
        McpClient.blueprint(),
        _common_agentic,
    ).transports(_RFID_TRANSPORTS)
except ModuleNotFoundError as exc:
    _AGENTIC_IMPORT_ERROR = exc

    def unitree_go2_rfid_agentic():
        raise RuntimeError(
            "The Go2 RFID agentic blueprint requires DimOS agentic/web dependencies. "
            f"Import failed: {_AGENTIC_IMPORT_ERROR}"
        ) from _AGENTIC_IMPORT_ERROR

__all__ = ["unitree_go2_rfid", "unitree_go2_rfid_agentic"]
