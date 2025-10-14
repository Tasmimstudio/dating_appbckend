# app/models/interest.py

class Interest:
    def __init__(
        self,
        interest_id: str,
        name: str,
        category: str
    ):
        self.interest_id = interest_id
        self.name = name
        self.category = category
