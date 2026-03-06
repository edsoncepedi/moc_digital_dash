from app.services.utils import nome_amigavel, nomes_amigaveis_numerados


MENSAGENS_POSTO_1 = {
    1: (
        "POSTO 1\n\n"
        "PEGUE A CPU\n\n"
        "Retire a CPU da bandeja.\n"
        "Segure sempre pelas bordas."
    ),
    2: (
        "POSTO 1\n\n"
        "INSIRA A CPU\n\n"
        "Posicione a CPU no soquete da placa-mãe.\n"
        "Alinhe o triângulo de referência."
    ),
    3: (
        "POSTO 1\n\n"
        "PEGUE O FAN\n\n"
        "Retire o cooler da bandeja."
    ),
    4: (
        "POSTO 1\n\n"
        "INSTALAR FAN\n\n"
        "Posicione o cooler sobre o processador\n"
        "e fixe corretamente."
    ),
    5: (
        "POSTO 1\n\n"
        "MONTAGEM CONCLUÍDA\n\n"
        "Pressione a pedaleira para enviar\n"
        "o produto ao próximo posto."
    ),
}

MENSAGENS_POSTO_2 = {
    1: (
        "POSTO 2\n\n"
        "PEGUE A MEMÓRIA 1\n\n"
        "Segure o primeiro módulo de RAM."
    ),
    2: (
        "POSTO 2\n\n"
        "INSIRA A MEMÓRIA 1\n\n"
        "Coloque o módulo no primeiro slot.\n"
        "Pressione até travar."
    ),
    3: (
        "POSTO 2\n\n"
        "PEGUE A MEMÓRIA 2\n\n"
        "Segure o segundo módulo de RAM."
    ),
    4: (
        "POSTO 2\n\n"
        "INSIRA A MEMÓRIA 2\n\n"
        "Coloque o módulo no segundo slot.\n"
        "Pressione até travar."
    ),
    5: (
        "POSTO 2\n\n"
        "MONTAGEM CONCLUÍDA\n\n"
        "Pressione a pedaleira para enviar\n"
        "o produto ao próximo posto."
    ),
}


def formatar_checklist(esperados, detectados):
    nomes = nomes_amigaveis_numerados(esperados)
    linhas = []

    for item in sorted(esperados):
        nome = nomes[item]
        if item in detectados:
            linhas.append(f"☑ {nome}")
        else:
            linhas.append(f"☐ {nome}")

    return "\n".join(linhas)


def formatar_itens(itens, vazio="Nenhum"):
    """
    Recebe list, set ou tuple e retorna string legível
    """
    if not itens:
        return vazio

    itens_ordenados = sorted(map(str, itens))

    return "\n".join(
        f"• {nome_amigavel(item)}"
        for item in itens_ordenados
    )


def mensagem_posto_0_inicio(posto_id: int, objetos_esperados, objetos_detectados) -> str:
    checklist = formatar_checklist(objetos_esperados, objetos_detectados)
    return (
        f"POSTO {posto_id}\n\n"
        f"INÍCIO DA MONTAGEM\n\n"
        f"Organize os itens na bancada conforme o checklist:\n\n"
        f"{checklist}"
    )


def mensagem_posto_0_montagem(posto_id: int, objetos_esperados, objetos_detectados, extras) -> str:
    checklist = formatar_checklist(objetos_esperados, objetos_detectados)

    mensagem = (
        f"POSTO {posto_id}\n\n"
        f"CHECKLIST DA MONTAGEM\n\n"
        f"Coloque os itens na bancada.\n\n"
        f"{checklist}"
    )

    if extras:
        mensagem += (
            "\n\n⚠ ATENÇÃO\n\n"
            "Itens fora da receita detectados:\n\n"
            f"{formatar_itens(extras)}"
        )

    return mensagem


def mensagem_posto_0_finalizado(posto_id: int, objetos_esperados, objetos_detectados) -> str:
    checklist = formatar_checklist(objetos_esperados, objetos_detectados)
    return (
        f"POSTO {posto_id}\n\n"
        f"ORGANIZAÇÃO CONCLUÍDA\n\n"
        f"{checklist}\n\n"
        f"Todos os itens estão corretos.\n"
        f"Passe o produto para o próximo posto."
    )


def obter_mensagem_etapa(posto_id: int, etapa: int) -> str:
    mensagens_por_posto = {
        1: MENSAGENS_POSTO_1,
        2: MENSAGENS_POSTO_2,
    }

    mensagens = mensagens_por_posto.get(posto_id, {})
    return mensagens.get(
        etapa,
        f"POSTO {posto_id}\n\nEtapa {etapa} não configurada."
    )