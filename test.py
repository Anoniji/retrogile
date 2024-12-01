def trier_dict_par_liste_uuid(liste_uuid, dict_a_trier):
    """Trie un dictionnaire par ordre d'une liste d'UUIDs.

    Args:
        liste_uuid (list): Liste des UUIDs spécifiant l'ordre.
        dict_a_trier (dict): Dictionnaire à trier.

    Returns:
        dict: Nouveau dictionnaire trié selon l'ordre de la liste.
    """

    dict_trie = {}
    for uuid in liste_uuid:
        uuid = uuid[5:]
        if uuid in dict_a_trier["Start"]:
            dict_trie[uuid] = dict_a_trier["Start"][uuid]
    return dict_trie

liste_ordre = ["uuid_229b2ab803904152b3201f7beca7bee4", "uuid_2e1560ecb1b94df29b66db044591b5a0"]
mon_dict = {"Start": {
    "2e1560ecb1b94df29b66db044591b5a0": {
        "pos": 20,
        "author": "toto",
        "author_id": 2,
        "content": "toto",
        "votes": 0
    },
    "229b2ab803904152b3201f7beca7bee4": {
        "pos": 4,
        "author": "test",
        "author_id": 24,
        "content": "qefqef",
        "votes": 0
    }
}}

print(mon_dict)
resultat = trier_dict_par_liste_uuid(liste_ordre, mon_dict)
print(resultat)