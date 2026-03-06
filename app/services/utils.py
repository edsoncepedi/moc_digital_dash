import re
from collections import defaultdict

def normalizar_componente(texto: str) -> str:
    return re.sub(r'\d+', '', texto).upper()

def nome_amigavel(item: str) -> str:
    if item is None:
        return ""

    s = str(item).strip()

    # remove pontuação solta no fim, mesmo com espaço antes: "ram :" -> "ram"
    s = re.sub(r"\s*[:;.,]\s*$", "", s)

    # remove números no final (com ou sem espaços): "ram2 " -> "ram"
    s = re.sub(r"\s*\d+\s*$", "", s)

    # se ainda sobrar pontuação no fim repetida, remove geral
    s = re.sub(r"[:;.,]+$", "", s).strip()

    return s.capitalize()

def nomes_amigaveis_numerados(itens):
    """
    Recebe lista/set de itens como:
    ['cpu1','ram1','ram2']

    Retorna dict:
    {
        'cpu1': 'Cpu',
        'ram1': 'Ram 1',
        'ram2': 'Ram 2'
    }
    """

    grupos = defaultdict(list)

    for item in itens:
        base = re.sub(r"\d+$", "", item)
        grupos[base].append(item)

    resultado = {}

    for base, grupo in grupos.items():
        base_nome = base.capitalize()

        if len(grupo) == 1:
            resultado[grupo[0]] = base_nome
        else:
            for i, item in enumerate(sorted(grupo), 1):
                resultado[item] = f"{base_nome} {i}"

    return resultado

def processar_objetos_visao(lista, cor, posto_id):
    objs = []

    for obj in lista:
        texto = obj["texto"].lower()

        if 'hand' in texto:
            obj["mostra"] = False
            continue

        if posto_id == 2 and ('cpu' in texto or 'fan' in texto):
            obj["mostra"] = False
            continue

        obj["cor"] = cor
        obj["texto"] = normalizar_componente(obj["texto"])

        objs.append(obj)

    return objs