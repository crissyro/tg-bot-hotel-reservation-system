from pymongo import ReturnDocument, DESCENDING
from models.mongo_models import Review
from typing import List, Optional

class ReviewCRUD:
    def __init__(self, collection):
        self.collection = collection

    async def create_review(self, review: Review):
        return await self.collection.insert_one(review.dict())

    async def update_review(self, review_id: str, update_data: dict):
        return await self.collection.find_one_and_update(
            {"_id": review_id},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER
        )

    async def delete_review(self, review_id: str):
        return await self.collection.delete_one({"_id": review_id})

    async def get_reviews(
        self,
        page: int = 1,
        per_page: int = 10,
        min_rating: Optional[int] = None,
        approved_only: bool = True
    ) -> List[dict]:
        query = {}
        if min_rating:
            query["rating"] = {"$gte": min_rating}
        if approved_only:
            query["is_approved"] = True

        skip = (page - 1) * per_page
        return await self.collection.find(query)\
            .sort("created_at", DESCENDING)\
            .skip(skip)\
            .limit(per_page)\
            .to_list(None)

    async def get_average_rating(self):
        pipeline = [
            {"$match": {"is_approved": True}},
            {"$group": {"_id": None, "average": {"$avg": "$rating"}}}
        ]
        result = await self.collection.aggregate(pipeline).to_list(None)
        return result[0]['average'] if result else 0