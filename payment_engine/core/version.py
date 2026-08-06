"""
Swift Payment Engine Version Information
"""

ENGINE_NAME = "Swift Payment Engine"
ENGINE_VERSION = "5.0.0"
ENGINE_STATUS = "Production"
COPYSWIFTAI_VERSION = "5.0.0"

def engine_info():
    return {
        "name": ENGINE_NAME,
        "version": ENGINE_VERSION,
        "status": ENGINE_STATUS,
        "platform": "CopySwiftAI",
        "platform_version": COPYSWIFTAI_VERSION,
    }
