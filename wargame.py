import re
import time

NB_LIGNES = 10
NB_COLONNES = 10
INFINI = 10000
plateau_de_jeu = None
nb_noeuds = 0


def f_convert_char2int(c):
    if "A" <= c <= "Z":
        return ord(c) - ord("A")
    if "a" <= c <= "z":
        return ord(c) - ord("a")
    return -1


def f_convert_int2char(i):
    return chr(i + ord("A"))


def f_init_plateau():
    plateau = [[0, 0] for _ in range(NB_LIGNES * NB_COLONNES)]

    # (ligne, colonne, couleur, valeur)
    pions = [
        (9, 5, 1, 1), (9, 6, 1, 2), (9, 7, 1, 3), (9, 8, 1, 2), (9, 9, 1, 1),
        (8, 0, 1, 1), (8, 1, 1, 3), (8, 2, 1, 3), (8, 3, 1, 1),
        (8, 6, 1, 1), (8, 7, 1, 1), (8, 8, 1, 1),
        (7, 1, 1, 1), (7, 2, 1, 1),
        (2, 7, -1, 1), (2, 8, -1, 1),
        (1, 1, -1, 1), (1, 2, -1, 1), (1, 3, -1, 1),
        (1, 6, -1, 1), (1, 7, -1, 3), (1, 8, -1, 3), (1, 9, -1, 1),
        (0, 0, -1, 1), (0, 1, -1, 2), (0, 2, -1, 3), (0, 3, -1, 2), (0, 4, -1, 1),
    ]
    for l, c, couleur, valeur in pions:
        plateau[l * NB_COLONNES + c] = [couleur, valeur]
    return plateau


def f_affiche_plateau(plateau):
    ligne_sep = "-- " * NB_COLONNES
    out = ["\n    "]
    out.append("".join(f"{f_convert_int2char(k):>2} " for k in range(NB_COLONNES)))
    out.append("\n    " + ligne_sep + "\n")
    for i in range(NB_LIGNES - 1, -1, -1):
        out.append(f"{i:2d} ")
        for j in range(NB_COLONNES):
            couleur, valeur = plateau[i * NB_COLONNES + j]
            out.append("|")
            if couleur == -1:
                out.append(f"{valeur}o")
            elif couleur == 1:
                out.append(f"{valeur}x")
            else:
                out.append("  ")
        out.append("|\n    " + ligne_sep + "\n")
    out.append("    ")
    print("".join(out), end="")


def f_gagnant():
    for i in range(NB_COLONNES):
        if plateau_de_jeu[i][0] == 1:
            return 1
        if plateau_de_jeu[(NB_LIGNES - 1) * NB_COLONNES + i][0] == -1:
            return -1

    somme1 = sum(1 for p in plateau_de_jeu if p[0] == 1)
    somme2 = sum(1 for p in plateau_de_jeu if p[0] == -1)
    if somme1 == 0:
        return -1
    if somme2 == 0:
        return 1
    return 0


def f_bataille_plateau(plateau, l, c):
    mini = max(l - 1, 0)
    maxi = min(l + 1, NB_LIGNES - 1)
    minj = max(c - 1, 0)
    maxj = min(c + 1, NB_COLONNES - 1)

    somme = 0
    for i in range(mini, maxi + 1):
        for j in range(minj, maxj + 1):
            couleur, valeur = plateau[i * NB_COLONNES + j]
            somme += couleur * valeur

    couleur, valeur = plateau[l * NB_COLONNES + c]
    somme -= couleur * valeur

    if somme < 0:
        return -1
    if somme > 0:
        return 1
    return couleur


def f_bataille(l, c):
    return f_bataille_plateau(plateau_de_jeu, l, c)


def f_test_mouvement(plateau, l1, c1, l2, c2, couleur):
    # Hors du plateau
    if (l1 < 0 or l1 >= NB_LIGNES or l2 < 0 or l2 >= NB_LIGNES or
            c1 < 0 or c1 >= NB_COLONNES or c2 < 0 or c2 >= NB_COLONNES):
        return 1
    # Pas de pion a deplacer ou pion n'appartenant pas au joueur
    if plateau[l1 * NB_COLONNES + c1][1] == 0 or plateau[l1 * NB_COLONNES + c1][0] != couleur:
        return 1
    if plateau[l2 * NB_COLONNES + c2][0] == plateau[l1 * NB_COLONNES + c1][0]:
        return 1
    if abs(l1 - l2) > 1 or abs(c1 - c2) > 1 or (l1 == l2 and c1 == c2):
        return 1
    return 0


def f_bouge_piece(plateau, l1, c1, l2, c2, couleur):
    if f_test_mouvement(plateau, l1, c1, l2, c2, couleur) != 0:
        return 1

    src = l1 * NB_COLONNES + c1
    dst = l2 * NB_COLONNES + c2

    if plateau[dst][1] == 0:
        # Personne a l'arrivee
        plateau[dst] = plateau[src][:]
        plateau[src] = [0, 0]
    else:
        gagnant = f_bataille_plateau(plateau, l2, c2)
        if gagnant == couleur:
            # victoire
            plateau[dst] = plateau[src][:]
            plateau[src] = [0, 0]
        elif gagnant != 0:
            # defaite
            plateau[src] = [0, 0]
    return 0


def f_nb_pions(jeu, joueur):
    return sum(1 for p in jeu if p[0] == joueur)


def f_valeur(jeu, joueur):
    return sum(p[1] for p in jeu if p[0] == joueur)


def f_eval(jeu, joueur):
    ligne_joueur = 0 if joueur == 1 else NB_LIGNES - 1
    ligne_adverse = NB_LIGNES - 1 if joueur == 1 else 0

    # Conditions de victoire
    for j in range(NB_COLONNES):
        if jeu[ligne_joueur * NB_COLONNES + j][0] == joueur:
            return INFINI
        if jeu[ligne_adverse * NB_COLONNES + j][0] == -joueur:
            return -INFINI

    nb_joueur = f_nb_pions(jeu, joueur)
    nb_adverse = f_nb_pions(jeu, -joueur)
    if nb_joueur == 0:
        return -INFINI
    if nb_adverse == 0:
        return INFINI

    force = f_valeur(jeu, joueur) - f_valeur(jeu, -joueur)
    nombre = nb_joueur - nb_adverse

    # Progression vers la ligne adverse
    avancee = 0
    for i in range(NB_LIGNES):
        for j in range(NB_COLONNES):
            couleur = jeu[i * NB_COLONNES + j][0]
            if couleur == 0:
                continue
            # Le joueur 1 va vers la ligne 0, le joueur -1 vers la derniere ligne
            progres = NB_LIGNES - 1 - i if couleur == 1 else i
            if couleur == joueur:
                avancee += progres
            else:
                avancee -= progres

    return 10 * force + 3 * nombre + 5 * avancee


def f_copie_plateau(source):
    return [p[:] for p in source]


def f_raz_plateau():
    return [[0, 0] for _ in range(NB_LIGNES * NB_COLONNES)]


def f_min(plateau, joueur_ia, profondeur, alpha, beta):
    global nb_noeuds
    meilleur = INFINI
    nb_coups = 0
    evaluation = f_eval(plateau, joueur_ia)
    nb_noeuds += 1

    if profondeur <= 0 or evaluation == INFINI or evaluation == -INFINI:
        return evaluation

    for i in range(NB_LIGNES):
        for j in range(NB_COLONNES):
            if plateau[i * NB_COLONNES + j][0] != -joueur_ia:
                continue
            for dl in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dl == 0 and dc == 0:
                        continue
                    l2 = i + dl
                    c2 = j + dc
                    if l2 < 0 or l2 >= NB_LIGNES or c2 < 0 or c2 >= NB_COLONNES:
                        continue

                    copie = f_copie_plateau(plateau)
                    if f_bouge_piece(copie, i, j, l2, c2, -joueur_ia) != 0:
                        continue

                    nb_coups += 1
                    score = f_max(copie, joueur_ia, profondeur - 1, alpha, beta)

                    if score < meilleur:
                        meilleur = score
                    if meilleur < beta:
                        beta = meilleur
                    if alpha >= beta:
                        return meilleur

    if nb_coups == 0:
        return evaluation
    return meilleur


def f_max(plateau, joueur_ia, profondeur, alpha, beta):
    global nb_noeuds
    meilleur = -INFINI
    nb_coups = 0
    evaluation = f_eval(plateau, joueur_ia)
    nb_noeuds += 1

    if profondeur <= 0 or evaluation == INFINI or evaluation == -INFINI:
        return evaluation

    for i in range(NB_LIGNES):
        for j in range(NB_COLONNES):
            if plateau[i * NB_COLONNES + j][0] != joueur_ia:
                continue
            for dl in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dl == 0 and dc == 0:
                        continue
                    l2 = i + dl
                    c2 = j + dc
                    if l2 < 0 or l2 >= NB_LIGNES or c2 < 0 or c2 >= NB_COLONNES:
                        continue

                    copie = f_copie_plateau(plateau)
                    if f_bouge_piece(copie, i, j, l2, c2, joueur_ia) != 0:
                        continue

                    nb_coups += 1
                    score = f_min(copie, joueur_ia, profondeur - 1, alpha, beta)

                    if score > meilleur:
                        meilleur = score
                    if meilleur > alpha:
                        alpha = meilleur
                    if alpha >= beta:
                        return meilleur

    if nb_coups == 0:
        return evaluation
    return meilleur


def f_ia(joueur):

    global nb_noeuds
    meilleur_score = -INFINI
    coup_trouve = False
    meilleur_coup = None
    nb_noeuds = 0
    debut = time.process_time()

    for i in range(NB_LIGNES):
        for j in range(NB_COLONNES):
            if plateau_de_jeu[i * NB_COLONNES + j][0] != joueur:
                continue
            for dl in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dl == 0 and dc == 0:
                        continue
                    l1, c1 = i, j
                    l2, c2 = i + dl, j + dc

                    if f_test_mouvement(plateau_de_jeu, l1, c1, l2, c2, joueur) != 0:
                        continue

                    copie = f_copie_plateau(plateau_de_jeu)
                    if f_bouge_piece(copie, l1, c1, l2, c2, joueur) != 0:
                        continue

                    score = f_min(copie, joueur, 2, -INFINI, INFINI)

                    if score > meilleur_score or not coup_trouve:
                        meilleur_score = score
                        meilleur_coup = (l1, c1, l2, c2)
                        coup_trouve = True

    if meilleur_coup is not None:
        f_bouge_piece(plateau_de_jeu, *meilleur_coup, joueur)

    fin = time.process_time()
    print(f"IA : {nb_noeuds} noeuds visites, {fin - debut:.4f} s")


def f_humain(joueur):
    symbole = {-1: "o", 1: "x"}.get(joueur, "inconnu")
    print(f"joueur {symbole} joue:")
    motif = re.compile(r"\s*([A-Za-z])\s*(\d+)\s*([A-Za-z])\s*(\d+)")
    while True:
        try:
            saisie = input()
        except EOFError:
            raise SystemExit(0)
        m = motif.match(saisie)
        if m:
            c1, l1, c2, l2 = m.group(1), int(m.group(2)), m.group(3), int(m.group(4))
            if f_bouge_piece(plateau_de_jeu, l1, f_convert_char2int(c1),
                             l2, f_convert_char2int(c2), joueur) == 0:
                break
        print("mauvais choix")


def main():
    global plateau_de_jeu
    print("1 humain vs IA\n2 humain vs humain\n3 IA vs IA")
    try:
        mode = int(input())
    except ValueError:
        mode = 0

    plateau_de_jeu = f_init_plateau()
    joueur = 1
    fin = False
    while not fin:
        f_affiche_plateau(plateau_de_jeu)
        if mode == 1:
            if joueur > 0:
                f_humain(joueur)
            else:
                f_ia(joueur)
        elif mode == 2:
            f_humain(joueur)
        else:
            f_ia(joueur)

        ret = f_gagnant()
        if ret == 1:
            f_affiche_plateau(plateau_de_jeu)
            print("joueur x gagne!")
            fin = True
        elif ret == -1:
            f_affiche_plateau(plateau_de_jeu)
            print("joueur o gagne!")
            fin = True
        joueur = -joueur


if __name__ == "__main__":
    main()