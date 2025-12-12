from sentence_transformers import SentenceTransformer, util
from transformers import AutoTokenizer, AutoModel
import torch




def test_fluencia_verbal() -> None:  # numero paraules
    paraules = ["gat", "ornitorrinc", "taula", "pi"]
    def_camp = "un animal és un ésser viu que es mou i no és una planta"

    for p in paraules:
        if pertany_camp_semantic(p, def_camp):
            print(f"{p} → SÍ")
        else:
            print(f"{p} → NO")


def pertany_camp_semantic(paraula: str, camp_semantic: str) -> bool:

    model = SentenceTransformer("PlanTL-GOB-ES/roberta-base-ca")
    
    

    embedding_paraula = model.encode(paraula)
    embedding_camp = model.encode(camp_semantic)

    # Similaritat cosinus
    similitud = util.cos_sim(embedding_paraula, embedding_camp).item()


    llindar = 0.45 #acabar de decidir nosaltres

    return True if similitud >= llindar else False


def comenca_lletra(paraula: str, lletra: str) -> bool:
    return True if paraula[0] == lletra else False



def main() -> None:
    test_fluencia_verbal()

if __name__ == "__main__":
    main()