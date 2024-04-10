

from global_code.helpful_functions import load_config
from openai import OpenAI

class State:
    """
    Singleton class for storing the state of the game.
    """

    config: dict = load_config()
    client = OpenAI(api_key=config['OPENAI']['API_KEY'])
    # os.environ['OPENAI_API_KEY'] = config['OPENAI']['API_KEY']
    # os.environ['REPLICATE_API_KEY'] = config['REPLICATE_API_KEY']
    #
    #
    # all_possible_agents = {'software engineer': 0, 'data scientist': 0, 'researcher': 0, 'writer': 0,
    #                        'devops': 0, 'ceo': 0, 'lawyer': 0, 'research': 0, 'risk managment': 0,
    #                        'finance': 0, 'it': 0, 'sales': 0, 'ethics': 0, 'marketing': 0,
    #                        'long term thinking': 0, 'bias detection': 0, 'science': 0, 'biology': 0,
    #                        'physics': 0, 'neuroscience': 0, 'chemistry': 0, 'enviormental science': 0,
    #                        'astronomy': 0, 'computer science': 0, 'information tech': 0, 'cyber security': 0,
    #                        'mechanical engineer': 0, 'civil engineer': 0, 'electrical engineer': 0,
    #                        'aerospace engineer': 0, 'chemical engineer': 0, 'pure math': 0,
    #                        'applied math': 0, 'statistics': 0, 'actuarial science': 0,
    #                        'operations research': 0, 'medicine': 0, 'dentist': 0, 'pharmacy': 0,
    #                        'nursing': 0, 'bio med science': 0, 'geology': 0, 'meteorology': 0,
    #                        'oceanography': 0, 'environmental engineer': 0, 'economics': 0, 'psychology': 0,
    #                        'geography': 0, 'genetic engineer': 0, 'bio med engineer': 0,
    #                        'bio information': 0, 'science education': 0, 'math education': 0,
    #                        'engineering education': 0, 'technology education': 0, 'machine learning': 0,
    #                        'nlp': 0, 'computer vision': 0, 'robotics': 0, 'expert systems': 0,
    #                        'neural networks': 0, 'ai ethics': 0, 'software testing': 0,
    #                        'database management': 0, 'software architecture': 0, 'aws': 0,
    #                        'iris_creation_agent': 0, 'ai engineer': 0, 'agi expert': 0,
    #                        'automation expert': 0, 'thomas shelby': 0, 'process optimization expert': 0,
    #                        'resource allocation expert': 0, 'task execution expert': 0,
    #                        'product manager': 0, 'project manager': 0, 'react frontend developer': 0,
    #                        'javascript developer': 0, '': 0, '': 0, '': 0, '': 0, '': 0, '': 0,
    #                        '': 0, '': 0, '': 0, '': 0, '': 0, '': 0}
    #
    #
    # ollama_openhermes = Ollama(model='openhermes')
    # gpt_3_5_model = ChatOpenAI(model="gpt-3.5-turbo")
    # static_low_power_llm_model = ollama_openhermes
    # static_medium_power_llm_model = gpt_3_5_model
    # static_high_power_llm_model = None
    #
    # idea_gen_agents = {'software engineer': 0, 'data scientist': 0, 'researcher': 0, 'writer': 0,
    #                        'devops': 0, 'ceo': 0, 'lawyer': 0, 'risk managment': 0,
    #                        'finance': 0, 'it': 0, 'sales': 0, 'ethics': 0, 'marketing': 0,
    #                        'long term thinking': 0, 'science': 0, 'biology': 0,
    #                        'physics': 0, 'neuroscience': 0, 'chemistry': 0, 'enviormental science': 0,
    #                        'astronomy': 0, 'computer science': 0, 'information tech': 0, 'cyber security': 0,
    #                        'mechanical engineer': 0, 'civil engineer': 0, 'electrical engineer': 0,
    #                        'aerospace engineer': 0, 'chemical engineer': 0, 'pure math': 0,
    #                        'applied math': 0, 'statistics': 0, 'actuarial science': 0,
    #                        'operations research': 0, 'medicine': 0, 'dentist': 0, 'pharmacy': 0,
    #                        'nursing': 0, 'bio med science': 0, 'geology': 0, 'meteorology': 0,
    #                        'oceanography': 0, 'environmental engineer': 0, 'economics': 0, 'psychology': 0,
    #                        'geography': 0, 'genetic engineer': 0, 'bio med engineer': 0,
    #                        'bio information': 0, 'science education': 0, 'math education': 0,
    #                        'engineering education': 0, 'technology education': 0, 'machine learning': 0,
    #                        'nlp': 0, 'computer vision': 0, 'robotics': 0, 'expert systems': 0,
    #                        'neural networks': 0, 'ai ethics': 0, 'software testing': 0,
    #                        'database management': 0, 'software architecture': 0, 'aws': 0,
    #                        'ai engineer': 0, 'agi expert': 0,
    #                        'automation expert': 0}


    def __init__(self):
        self._state = None


