from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.pydantic_v1 import BaseModel, Field


# create custom output parser
class FactCheckerParser(BaseModel):
    """
    Custom output parser for the fact checking to be used in the large langauge model 

    Attributes:
    - fact_score (str) : 
    """
    fact_score : int = Field(description="The score from 0-100 for how factual the given inputted claim is. Use your best judgement to judge its factual accuracy")
 