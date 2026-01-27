def comparar_objetos(objetos_detectados: set, objetos_esperados: set):
    faltantes = objetos_esperados - objetos_detectados
    extras = objetos_detectados - objetos_esperados

    return {
        "faltantes": sorted(faltantes),
        "extras": sorted(extras),
        "ok": len(faltantes) == 0
    }