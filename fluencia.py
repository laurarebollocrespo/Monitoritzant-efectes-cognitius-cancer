from sentence_transformers import SentenceTransformer, util

# Modelo entrenado o multilingüe con soporte catalán
model_name = "mrm8488/roberta-base-ca-sentiment"  # RoBERTa catalán
model = SentenceTransformer(model_name)


def test_fluencia_verbal() -> int: #numero paraules
    ...



def pertany_camp_semantic(paraula: str, camp_semantic: str) -> bool:
    
    nom_model = "mrm8488/roberta-base-ca-sentiment"  # RoBERTa català
    model = SentenceTransformer(model_name)
    embedding = model.encode(paraula)
    def_camp = ...

    vec_camp = model.encode(def_camp)
    similitud = util.cos_sim(embedding, vec_camp).item()
    llindar = ...

    return True if similitud >= llindar else False


def comenca_lletra(paraula: str, lletra: str) -> bool:
    return True if paraula[0] == lletra else False