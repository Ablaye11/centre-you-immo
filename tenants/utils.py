"""
Utilitaires pour l'application tenants (gestion des locataires et contrats de bail).
"""

def number_to_words_fr(n):
    """
    Convertit un entier n en toutes lettres en français (en majuscules).
    Exemple: 250000 -> DEUX CENT CINQUANTE MILLE
             15000 -> QUINZE MILLE
             265000 -> DEUX CENT SOIXANTE-CINQ MILLE
    """
    try:
        n = int(n)
    except (ValueError, TypeError):
        return ""

    if n == 0:
        return "ZERO"
    if n < 0:
        return "MOINS " + number_to_words_fr(-n)

    units = ['', 'UN', 'DEUX', 'TROIS', 'QUATRE', 'CINQ', 'SIX', 'SEPT', 'HUIT', 'NEUF',
             'DIX', 'ONZE', 'DOUZE', 'TREIZE', 'QUATORZE', 'QUINZE', 'SEIZE', 'DIX-SEPT',
             'DIX-HUIT', 'DIX-NEUF']
    tens = ['', '', 'VINGT', 'TRENTE', 'QUARANTE', 'CINQUANTE', 'SOIXANTE', 'SOIXANTE',
            'QUATRE-VINGT', 'QUATRE-VINGT']

    def convert_below_1000(num):
        res = []
        c = num // 100
        r = num % 100
        if c > 0:
            if c == 1:
                res.append('CENT')
            else:
                res.append(units[c] + ' CENT' + ('S' if r == 0 else ''))
        if r > 0:
            if r < 20:
                res.append(units[r])
            else:
                t = r // 10
                u = r % 10
                if t in (7, 9):
                    base_t = 'SOIXANTE' if t == 7 else 'QUATRE-VINGT'
                    sub = r - (60 if t == 7 else 80)
                    if sub == 11 and t == 7:
                        res.append(base_t + ' ET ONZE')
                    else:
                        res.append(base_t + '-' + units[sub])
                else:
                    if u == 1 and t != 8:
                        res.append(tens[t] + ' ET UN')
                    elif u == 0:
                        res.append(tens[t] + ('S' if t == 8 else ''))
                    else:
                        res.append(tens[t] + '-' + units[u])
        return ' '.join(res)

    parts = []
    millions = n // 1000000
    thousands = (n % 1000000) // 1000
    remainder = n % 1000

    if millions > 0:
        if millions == 1:
            parts.append('UN MILLION')
        else:
            parts.append(convert_below_1000(millions) + ' MILLIONS')

    if thousands > 0:
        if thousands == 1:
            parts.append('MILLE')
        else:
            parts.append(convert_below_1000(thousands) + ' MILLE')

    if remainder > 0:
        parts.append(convert_below_1000(remainder))

    return ' '.join(parts)

