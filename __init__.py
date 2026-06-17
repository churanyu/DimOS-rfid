"""DimOS integration for the Vulcan RFID scanner."""

from dimos_rfid.msgs import RfidTag, RfidTagArray

__all__ = [
    "RfidModule",
    "RfidModuleConfig",
    "RfidTag",
    "RfidTagArray",
]


def __getattr__(name: str):
    if name in {"RfidModule", "RfidModuleConfig"}:
        from dimos_rfid.rfid_module import RfidModule, RfidModuleConfig

        return {"RfidModule": RfidModule, "RfidModuleConfig": RfidModuleConfig}[name]
    raise AttributeError(name)
