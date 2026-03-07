COOKIE_ACCEPT_XPATHS = [
    "//button[contains(., 'SIM, EU ACEITO')]",
    "//button[contains(., 'Aceito')]",
    "//button[contains(., 'ACEITAR')]",
    "//button[contains(., 'OK')]",
    "//button[contains(., 'Fechar')]",
    "//button[contains(., 'Agora não')]",
    "//button[contains(., 'Não, obrigado')]",
    "//button[contains(., 'NÃO, OBRIGADO')]",
    "//button[contains(., 'ENTENDI')]",
    "//button[contains(., 'Continuar')]",
    "//button[contains(., 'Prosseguir')]",
]

MATCH_BLOCKS_XPATH = """
//div[
    .//*[contains(text(), '1')]
    and .//*[contains(text(), 'X')]
    and .//*[contains(text(), '2')]
]
"""