from app.feature_flags.flags import flags
from app import state

async def handle_feature_calibracao(payload: dict):
    enabled = bool(payload.get("enabled", False))
    flags.set_global("calibracao", enabled)

    print(
        f"🔧 Calibração GLOBAL "
        f"{'ATIVADA' if enabled else 'DESATIVADA'}"
    )


async def handle_dispositivo_posto(posto_nome: str, payload_raw):
    """
    payload_raw pode ser:
      - "BD"
      - {"msg": "BD"} (dependendo do ESP)
    """
    posto_id = None

    # Normaliza payload
    if isinstance(payload_raw, dict):
        comando = str(payload_raw.get("msg", "")).strip().upper()
    else:
        comando = str(payload_raw).strip().upper()

    if comando == "BD":
        # posto_nome vem tipo "posto_0"
        try:
            posto_id = int(posto_nome.split("_")[-1])
        except:
            print(f"❌ Posto inválido no tópico: {posto_nome}")
            return
        
        flags.set_posto("camera", posto_id, False)
        state.reset_posto(posto_id)
    elif comando == "BS":
        try:
            posto_id = int(posto_nome.split("_")[-1])
        except:
            print(f"❌ Posto inválido no tópico: {posto_nome}")
            return
        
        flags.set_posto("camera", posto_id, True)
    if posto_id is not None:
        print(f"🔄 RESET via MQTT: {posto_nome} (posto_id={posto_id})")