from fastapi import APIRouter
from ml_models import RecommendationModel

router = APIRouter()

recommend = RecommendationModel()
recommend.train()
recommend.save()


@router.get("/product/{id}/recommendation")
def get_recommendation(product_id: int):

    recommend.load()
    return recommend.recommend(product_id)
