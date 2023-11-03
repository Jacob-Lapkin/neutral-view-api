from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.pydantic_v1 import BaseModel, Field


# create custom output parser
class ClaimCheckerParser(BaseModel):
    """
    Custom output parser for the fact checking to be used in the large langauge model 

    Attributes:
    - fact_score (str) : 
    """
    fact_score : int = Field(description="The score from 0-100 for how factual the given inputted claim is. Use your best judgement to judge its factual accuracy")

parser = PydanticOutputParser(pydantic_Object=ClaimCheckerParser)
prompt = """
            
            """

llm = ChatOpenAI(model="gpt-4", temperature=0.2)


class ClaimChecker:
    """
    Class to check the validity of a user claim

    Attributes:
    - _claim (str)  : this is the statement that the user is checking to verifiy the factual evidence of
    - _personal_bias (str) : this is the bias that the user can submit along with their claim for added context
    - prompt (str) : the pre prompt that will be send to the language model and formatted

    Methods:
    - get_claim : 
    - set_claim : 
    - get_bias
    - set_bias : 
    """
    def __init__(self, claim, person_bias):
        self._claim = claim
        self._personal_bias = person_bias
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
    def get_bias(self):
        """
        getter method to obtain bias 

        Returns:
        - claim (str) : the personal bias that the user holds when addressing historical global conflicts
        """
        return self._personal_bias
    def set_bias(self, bias):
        """"
        setter method to set bias 

        Returns:
        - self (obj) : returns current object
        """
        self._personal_bias = bias
        return self
    def analyze_claim(self):
        """
        method to analyze claim and return parsed output

        Returns:
        - parsed_ouput (obj) : dictionary containing the parsed output from the llm
        """

        # configuring prompt template
        completed_prompt = PromptTemplate(template=self.prompt, input_variables=["user_claim", "personal_bias"], partial_variables={"format_instructions":parser.get_format_instructions()})
        
        # filling in template to produce final input
        model_input = completed_prompt.format_prompt(user_claim=self._claim, personal_bias=self._personal_bias)

        # obtaining output
        output = llm(model_input.to_string())

        # parsed output
        parsed_ouput = parser.parse(output)

        return parsed_ouput


 