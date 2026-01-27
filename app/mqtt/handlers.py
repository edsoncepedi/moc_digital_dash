from app.feature_flags.flags import flags

async def handle_feature_calibracao(payload: dict):
    enabled = bool(payload.get("enabled", False))
    flags.set_global("calibracao", enabled)

    print(
        f"🔧 Calibração GLOBAL "
        f"{'ATIVADA' if enabled else 'DESATIVADA'}"
    )