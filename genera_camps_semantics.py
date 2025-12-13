from collections import defaultdict
import wn

# Descarregar WordNet multilingüe
wn.download('omw-en')
wn.download('omw-ca')

en = wn.Wordnet('omw-en')

camps = defaultdict(set)

tots_synsets = en.synsets()

for syn in tots_synsets:
    hypers = syn.hypernyms()
    if not hypers:
        continue
    
    hiper = hypers[0]  # primer hiperònim
    
    # Nom del camp: intentar català, sinó anglès
    lem_cat = hiper.lemmas(lang='ca')
    if lem_cat:
        nom_camp = lem_cat[0].lemma  # català
    else:
        nom_camp = hiper.lemmas()[0].lemma  # fallback anglès

    # Paraules en català del synset actual
    for lemma in syn.lemmas(lang='ca'):
        camps[nom_camp].add(lemma.lemma)

# Escriure a fitxer
with open("camps_semantics.txt", "w", encoding="utf-8") as f:
    for camp, mots in sorted(camps.items()):
        if not mots:
            continue
        f.write(camp.upper() + "\n")
        f.write(", ".join(sorted(mots)) + "\n\n")

print("Fitxer generat correctament: camps_semantics.txt")
