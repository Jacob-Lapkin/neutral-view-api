import os
from json import load
from pyexpat import model
from typing import List
from langchain.callbacks import get_openai_callback

from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import (ChatPromptTemplate,
                               HumanMessagePromptTemplate
                               )
from pydantic import BaseModel, Field
from .icons_list import icons

load_dotenv()

# create custom output parser
class ClaimCheckerParser(BaseModel):
    """
    Custom output parser for the fact checking to be used in the large langauge model 

    Attributes:
    - fact_score (str) : 
    """
    fact_score: int = Field(
        description="The score from 0-100 for how factual the given inputted claim is. Use your best judgement to judge its factual accuracy")
    explanation: str = Field(description="""A detailed justification for the assigned fact score, providing context and analysis based on historical evidence within a 200 word limit. 
                             This explanation should clarify the reasoning behind the score, highlight relevant historical facts detail any discrepancies or uncertainties encountered during the fact-checking process.""")
    icons_list: int = Field(description=f"""Select the key (the number) for the icon that best fits the claim type: {icons}
                                        """)
    source_url: str = Field(
        description="A URL to the original document, study, website, article, book, or other content from which we can site as a good source.")
    relevance: bool = Field(description="True or False value for whether or not the claim has anything to with history or what you are supposed to answer questions on")

parser = PydanticOutputParser(pydantic_object=ClaimCheckerParser)


prompt = """
    You are an advanced historical analysis system with specialized capabilities in verifying the accuracy of historical claims.
    
    Please ensure your responses adhere to the following format: {format_instructions}
    
    Ensure that you remain objective and that you always supply a score, explanation, icons, and source url no matter what. 

    Your main goal is to provide a thorough and factual analysis of historical claims, assisting users in discerning the truth based on solid historical evidence.

    Historical claim to analyze: {user_claim}
    """


class ClaimChecker:
    """
    Class to check the validity of a user claim

    Attributes:
    - _claim (str)  : this is the statement that the user is checking to verifiy the factual evidence of
    - prompt (str) : the pre prompt that will be send to the language model and formatted

    Methods:
    - get_claim : 
    - set_claim :  
    """

    def __init__(self, model='gpt-3.5-turbo', company='openai'):
        self.model = model
        self.company = company
        self._claim = None
        self.prompt = prompt

    def get_claim(self):
        """
        getter method to obtain claim 

        Returns:
        - claim (str) : the claim that the user is seeking to address about historical global conflicts
        """
        return self._claim

    def set_claim(self, claim):
        """"
        setter method to set claim 

        Returns:
        - self (obj) : returns current object
        """
        self._claim = claim
        return self

    def analyze_claim(self):
        """
        method to analyze claim and return parsed output

        Returns:
        - parsed_ouput (obj) : dictionary containing the parsed output from the llm
        """
        
        # check if claim exists
        if self._claim is None:
            raise ValueError("Claim must have a value before analyzing claim")

        # set llm with model
        llm = ChatOpenAI(model=self.model, temperature=0.2)

        # configuring prompt template for openai
        completed_prompt = ChatPromptTemplate(messages=[HumanMessagePromptTemplate.from_template(self.prompt)],
                                                    input_variables=[
                                                        "user_claim"],
                                                    partial_variables={
            "format_instructions": parser.get_format_instructions(),
        },
        )
        
        # filling in template to produce final input
        model_input = completed_prompt.format_prompt(user_claim=self._claim)

        with get_openai_callback() as cb:
        # obtaining output
            output = llm(model_input.to_messages())
            # parsed output
            parsed_ouput = parser.parse(output.content)

            return (parsed_ouput, cb)


new_claim = ClaimChecker(company='openai')

new_claim.set_claim(
    "The Ming dynasty and the roman empire were extreme rivals")

response, token_count = new_claim.analyze_claim()
