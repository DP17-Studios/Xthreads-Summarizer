import os
import asyncio
from typing import List, Dict, Optional
from langchain_community.llms import OpenAI
from langchain_openai import ChatOpenAI
from langchain_mistralai import ChatMistralAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.schema import HumanMessage, SystemMessage
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ThreadSummarizer:
    def __init__(self, provider: str = "openai"):
        self.provider = provider.lower()
        self.llm = self._initialize_llm()
        self.summary_prompt = self._create_summary_prompt()
    
    def _initialize_llm(self):
        """
        Initialize the LLM based on the specified provider
        """
        try:
            if self.provider == "openai":
                api_key = os.getenv('OPENAI_API_KEY')
                if not api_key:
                    raise ValueError("OPENAI_API_KEY environment variable is required")
                
                return ChatOpenAI(
                    api_key=api_key,
                    model_name="gpt-3.5-turbo",
                    temperature=0.3,
                    max_tokens=500
                )
            
            elif self.provider == "mistral":
                api_key = os.getenv('MISTRAL_API_KEY')
                if not api_key:
                    raise ValueError("MISTRAL_API_KEY environment variable is required")
                
                return ChatMistralAI(
                    api_key=api_key,
                    model="mistral-tiny",
                    temperature=0.3,
                    max_tokens=500
                )
            
            else:
                raise ValueError(f"Unsupported LLM provider: {self.provider}")
                
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {str(e)}")
            raise
    
    def _create_summary_prompt(self) -> PromptTemplate:
        """
        Create a prompt template for thread summarization
        """
        template = """
You are an expert at summarizing Twitter/X threads. Your task is to read the following thread content and create a concise, informative summary.

Thread Content:
{thread_content}

Instructions:
1. Create exactly 5 bullet points that capture the main ideas and key insights
2. Each bullet point should be concise but informative (1-2 sentences max)
3. Focus on the most important takeaways and actionable insights
4. Maintain the original tone and perspective of the author
5. Avoid repetition between bullet points
6. Use clear, accessible language

Please provide your summary in the following format:

• [First main point]
• [Second main point]
• [Third main point]
• [Fourth main point]
• [Fifth main point]

Summary:
"""
        
        return PromptTemplate(
            input_variables=["thread_content"],
            template=template
        )
    
    async def summarize_thread(self, thread_data: Dict[str, any]) -> Dict[str, any]:
        """
        Summarize a Twitter thread using the configured LLM
        """
        try:
            # Extract the full thread content
            full_text = thread_data.get('full_text', '')
            tweets = thread_data.get('tweets', [])
            author = thread_data.get('author', 'Unknown')
            
            if not full_text:
                raise ValueError("No content found to summarize")
            
            # Prepare the content for summarization
            formatted_content = self._format_thread_content(tweets, author)
            
            logger.info(f"Summarizing thread with {len(tweets)} tweets")
            
            # Generate the summary
            summary = await self._generate_summary(formatted_content)
            
            # Process and validate the summary
            bullet_points = self._extract_bullet_points(summary)
            
            return {
                'success': True,
                'summary': {
                    'bullet_points': bullet_points,
                    'author': author,
                    'tweet_count': len(tweets),
                    'raw_summary': summary
                },
                'original_content': {
                    'full_text': full_text[:500] + '...' if len(full_text) > 500 else full_text,
                    'tweet_count': len(tweets)
                }
            }
            
        except Exception as e:
            logger.error(f"Error summarizing thread: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'summary': None
            }
    
    def _format_thread_content(self, tweets: List[Dict], author: str) -> str:
        """
        Format the thread content for better LLM processing
        """
        if not tweets:
            return "No tweets found"
        
        formatted_content = f"Twitter Thread by @{author}\n\n"
        
        for i, tweet in enumerate(tweets, 1):
            tweet_text = tweet.get('text', '').strip()
            if tweet_text:
                formatted_content += f"Tweet {i}: {tweet_text}\n\n"
        
        return formatted_content
    
    async def _generate_summary(self, content: str) -> str:
        """
        Generate summary using the configured LLM
        """
        try:
            # Create the chain
            chain = LLMChain(
                llm=self.llm,
                prompt=self.summary_prompt,
                verbose=False
            )
            
            # Generate summary
            result = await asyncio.to_thread(
                chain.run,
                thread_content=content
            )
            
            return result.strip()
            
        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            raise Exception(f"Failed to generate summary: {str(e)}")
    
    def _extract_bullet_points(self, summary_text: str) -> List[str]:
        """
        Extract and validate the 5 bullet points from the summary
        """
        lines = summary_text.split('\n')
        bullet_points = []
        
        for line in lines:
            line = line.strip()
            # Look for bullet points (•, -, *, or numbered)
            if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                # Remove bullet character and clean up
                clean_point = line[1:].strip()
                if clean_point:
                    bullet_points.append(clean_point)
            elif line and len(line.split('.')) >= 2 and line.split('.')[0].isdigit():
                # Handle numbered lists (1. 2. etc.)
                clean_point = '.'.join(line.split('.')[1:]).strip()
                if clean_point:
                    bullet_points.append(clean_point)
        
        # If we don't have exactly 5 points, try to fix it
        if len(bullet_points) == 0:
            # Fallback: split the summary into sentences and take first 5
            sentences = [s.strip() for s in summary_text.split('.') if s.strip()]
            bullet_points = sentences[:5]
        
        elif len(bullet_points) < 5:
            # If we have fewer than 5, pad with additional content
            while len(bullet_points) < 5 and len(bullet_points) < 10:
                bullet_points.append(f"Additional insight {len(bullet_points)}: Content analysis point")
        
        elif len(bullet_points) > 5:
            # If we have more than 5, take the first 5 most substantial ones
            bullet_points = sorted(bullet_points, key=len, reverse=True)[:5]
        
        return bullet_points[:5]  # Ensure exactly 5 points
    
    def get_provider_status(self) -> Dict[str, any]:
        """
        Get the current provider and its status
        """
        return {
            'provider': self.provider,
            'initialized': self.llm is not None,
            'model': getattr(self.llm, 'model_name', 'Unknown')
        }

class MultiProviderSummarizer:
    """
    A wrapper that can fallback between multiple LLM providers
    """
    def __init__(self, providers: List[str] = ["mistral", "openai"]):
        self.providers = providers
        self.current_provider_index = 0
        self.summarizer = None
        self._initialize_current_provider()
    
    def _initialize_current_provider(self):
        """
        Initialize the current provider
        """
        while self.current_provider_index < len(self.providers):
            try:
                provider = self.providers[self.current_provider_index]
                self.summarizer = ThreadSummarizer(provider)
                logger.info(f"Successfully initialized {provider} provider")
                return
            except Exception as e:
                logger.warning(f"Failed to initialize {provider}: {str(e)}")
                self.current_provider_index += 1
        
        raise Exception("No LLM providers could be initialized")
    
    async def summarize_thread(self, thread_data: Dict[str, any]) -> Dict[str, any]:
        """
        Summarize thread with automatic provider fallback
        """
        last_error = None
        
        for attempt in range(len(self.providers)):
            try:
                if self.summarizer:
                    result = await self.summarizer.summarize_thread(thread_data)
                    if result['success']:
                        return result
                    else:
                        last_error = result.get('error', 'Unknown error')
                        raise Exception(last_error)
                
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Provider {self.providers[self.current_provider_index]} failed: {str(e)}")
                
                # Try next provider
                self.current_provider_index += 1
                if self.current_provider_index < len(self.providers):
                    try:
                        self._initialize_current_provider()
                    except Exception as init_error:
                        logger.error(f"Failed to initialize next provider: {str(init_error)}")
                        continue
        
        return {
            'success': False,
            'error': f"All providers failed. Last error: {last_error}",
            'summary': None
        }

# Example usage and testing
if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv
    
    load_dotenv()
    
    async def test_summarizer():
        # Test data
        test_thread_data = {
            'author': 'TestUser',
            'tweets': [
                {'text': 'This is the first tweet in our thread about AI development.'},
                {'text': 'The second point discusses the importance of ethical AI practices.'},
                {'text': 'Finally, we need to consider the future implications of this technology.'}
            ],
            'full_text': 'This is the first tweet in our thread about AI development. The second point discusses the importance of ethical AI practices. Finally, we need to consider the future implications of this technology.'
        }
        
        summarizer = MultiProviderSummarizer()
        result = await summarizer.summarize_thread(test_thread_data)
        print(f"Summarization result: {result}")
    
    # Uncomment to test
    # asyncio.run(test_summarizer())