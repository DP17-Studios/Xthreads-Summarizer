import asyncio
import re
from typing import List, Dict, Optional
import os
import logging
import json

# Import firecrawl with try/except for different versions
try:
    from firecrawl_py import FirecrawlApp
    print('Using firecrawl_py import')
except ImportError:
    try:
        from firecrawl import FirecrawlApp
        print('Using firecrawl import')
    except ImportError:
        print('Using mock FirecrawlApp')
        class FirecrawlApp:
            def __init__(self, api_key):
                self.api_key = api_key
            def scrape_url(self, url, params=None):
                return {'markdown': 'Mock content for testing'}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ThreadScraper:
    def __init__(self):
        self.firecrawl_api_key = os.getenv('FIRECRAWL_API_KEY')
        if not self.firecrawl_api_key:
            raise ValueError("FIRECRAWL_API_KEY environment variable is required")
        self.app = FirecrawlApp(api_key=self.firecrawl_api_key)
    
    def _validate_twitter_url(self, url: str) -> bool:
        """
        Validate if the URL is a valid Twitter/X thread URL
        """
        patterns = [
            r'https?://(?:www\.)?twitter\.com/\w+/status/\d+',
            r'https?://(?:www\.)?x\.com/\w+/status/\d+'
        ]
        return any(re.match(pattern, url) for pattern in patterns)
    
    def _extract_thread_id(self, url: str) -> Optional[str]:
        """
        Extract the status ID from the Twitter URL
        """
        match = re.search(r'/status/(\d+)', url)
        return match.group(1) if match else None
    
    async def scrape_thread(self, url: str) -> Dict[str, any]:
        """
        Scrape a Twitter thread using Firecrawl API
        """
        try:
            # Validate URL
            if not self._validate_twitter_url(url):
                raise ValueError("Invalid Twitter/X URL format")
            
            logger.info(f"Scraping thread: {url}")
            
            # Use Firecrawl to scrape the page
            result = await asyncio.to_thread(
                self.app.scrape_url,
                url,
                params={
                    'formats': ['markdown', 'html'],
                    'includeTags': [
                        'article', 
                        'div[data-testid="tweetText"]', 
                        'div[data-testid="tweet"]',
                        'div[data-testid="cellInnerDiv"]',
                        'span[data-testid="tweetText"]',
                        'time',
                        'div[role="article"]'
                    ],
                    'excludeTags': ['script', 'style', 'nav', 'footer', 'aside', 'header'],
                    'waitFor': 3000,  # Wait longer for dynamic content to load
                    'timeout': 10000,  # Increase timeout for complex pages
                    'onlyMainContent': True  # Focus on main content area
                }
            )
            
            if not result:
                logger.error("Firecrawl returned empty result")
                raise Exception("Failed to scrape content: Firecrawl returned empty result")
                
            if 'markdown' not in result:
                logger.error(f"Firecrawl result missing markdown content: {json.dumps(result)[:200]}")
                raise Exception("Failed to scrape content: No markdown in response")
            
            # Extract and process thread content
            thread_data = self._process_scraped_content(result['markdown'], url)
            
            return {
                'success': True,
                'thread_data': thread_data,
                'original_url': url
            }
            
        except Exception as e:
            logger.error(f"Error scraping thread {url}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'original_url': url
            }
    
    def _process_scraped_content(self, markdown_content: str, url: str) -> Dict[str, any]:
        """
        Process the scraped markdown content to extract thread tweets
        """
        try:
            # Extract tweets from markdown content
            tweets = self._extract_tweets_from_markdown(markdown_content)
            
            if not tweets:
                logger.warning(f"No tweets found in content. Raw content sample: {markdown_content[:200]}")
                raise Exception("No tweets found in the scraped content")
            
            # Get thread metadata
            thread_id = self._extract_thread_id(url)
            
            return {
                'thread_id': thread_id,
                'tweets': tweets,
                'total_tweets': len(tweets),
                'full_text': ' '.join([tweet['text'] for tweet in tweets]),
                'author': tweets[0].get('author', 'Unknown') if tweets else 'Unknown'
            }
            
        except Exception as e:
            logger.error(f"Error processing scraped content: {str(e)}")
            raise Exception(f"Error processing scraped content: {str(e)}")
    
    def _extract_tweets_from_markdown(self, markdown: str) -> List[Dict[str, str]]:
        """
        Extract individual tweets from markdown content
        """
        tweets = []
        
        # If markdown is empty or too short, return empty list
        if not markdown or len(markdown) < 50:
            logger.warning(f"Markdown content too short: {markdown}")
            return []
            
        # Split content into lines for processing
        lines = markdown.split('\n')
        
        # Look for patterns that indicate thread structure
        author_pattern = r'@(\w+)'
        time_pattern = r'\d{1,2}[hms]|\w{3} \d{1,2}|\d{1,2}:\d{2}'
        
        # Common separators and indicators for tweet boundaries
        tweet_separators = [
            'Show this thread',
            '·',  # Dot separator often used in Twitter
            'Quote Tweet',
            'Show replies',
            'Retweet',
            'Like',
            '---',  # Common markdown separator
            '___'   # Another separator
        ]
        
        # Indicators that content should be excluded (replies, etc.)
        exclude_indicators = [
            'Replying to',
            'In reply to',
            'Reply to this tweet',
            'Show this reply',
            'This Tweet is unavailable',
            'This account is private'
        ]
        
        # Track current tweet being built
        current_tweet_lines = []
        current_author = None
        tweet_count = 0
        
        # First pass: extract author from early mentions
        for line in lines[:15]:  # Check first 15 lines for author
            author_match = re.search(author_pattern, line)
            if author_match:
                current_author = author_match.group(1)
                break
        
        # If no @mention found, look for author in lines that might contain usernames
        if not current_author:
            for line in lines[:20]:
                line_clean = line.strip()
                if line_clean and not any(ui in line_clean.lower() for ui in ['twitter', 'home', 'explore', 'notifications']):
                    # Look for standalone usernames (not @mentions)
                    if re.match(r'^[a-zA-Z0-9_]+$', line_clean) and len(line_clean) > 3:
                        current_author = line_clean
                        break
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip completely empty lines
            if not line:
                i += 1
                continue
            
            # Check if this line indicates a tweet separator
            is_separator = any(sep.lower() in line.lower() for sep in tweet_separators)
            
            # Check if this line should be excluded (replies, etc.)
            is_excluded_content = any(excl.lower() in line.lower() for excl in exclude_indicators)
            
            # Check for UI elements to skip
            is_ui_element = any(ui_term in line.lower() for ui_term in [
                'home', 'explore', 'notifications', 'messages', 'bookmarks',
                'twitter', 'x.com', 'what\'s happening', 'trending',
                'follow', 'followers', 'following', 'profile',
                'search twitter', 'log in', 'sign up'
            ])
            
            # If we hit excluded content, skip this section entirely
            if is_excluded_content:
                # Finalize any current tweet before skipping
                if current_tweet_lines:
                    self._finalize_current_tweet(current_tweet_lines, tweets, current_author, tweet_count)
                    current_tweet_lines = []
                    tweet_count += 1
                
                # Skip ahead until we find a separator or new thread content
                while i < len(lines) - 1:
                    i += 1
                    next_line = lines[i].strip()
                    # Stop when we find a clear thread continuation (numbered tweets, separators)
                    if (any(sep.lower() in next_line.lower() for sep in tweet_separators) or
                        re.match(r'^\d+[/)\s]', next_line) or  # Numbered tweets like "3/" or "4)"
                        (next_line.startswith('@') and current_author and current_author.lower() in next_line.lower())):
                        break
                continue
            
            # If we hit a separator or UI element, finalize current tweet
            if is_separator or is_ui_element:
                self._finalize_current_tweet(current_tweet_lines, tweets, current_author, tweet_count)
                current_tweet_lines = []
                tweet_count += 1
                i += 1
                continue
            
            # Look for potential tweet indicators
            has_time = re.search(time_pattern, line)
            starts_with_number = re.match(r'^\d+[/.)\s]', line.strip())  # Added / for numbered threads
            is_long_content = len(line) > 50
            
            # If this looks like a new numbered tweet
            if starts_with_number and current_tweet_lines:
                # Finalize previous tweet before starting new one
                self._finalize_current_tweet(current_tweet_lines, tweets, current_author, tweet_count)
                current_tweet_lines = []
                tweet_count += 1
            # If this looks like a time-based separator and we have content
            elif has_time and current_tweet_lines and len(current_tweet_lines) > 1:
                # Finalize previous tweet
                self._finalize_current_tweet(current_tweet_lines, tweets, current_author, tweet_count)
                current_tweet_lines = []
                tweet_count += 1
            
            # Clean and add the line if it contains substantial content
            cleaned_line = self._clean_tweet_line(line)
            if cleaned_line and len(cleaned_line) > 5:  # Minimum content threshold
                current_tweet_lines.append(cleaned_line)
            
            i += 1
        
        # Finalize the last tweet if we have content
        if current_tweet_lines:
            self._finalize_current_tweet(current_tweet_lines, tweets, current_author, tweet_count)
        
        # Fallback: if no tweets extracted, try to split content intelligently
        if not tweets:
            logger.warning("No tweets extracted through structured parsing, using fallback extraction")
            tweets = self._fallback_content_extraction(markdown, current_author)
        
        # Post-process: merge very short tweets and split very long ones
        tweets = self._post_process_tweets(tweets)
        
        # Final fallback: if still no tweets, create a dummy tweet with the raw content
        if not tweets and markdown.strip():
            logger.warning("Using emergency fallback: creating dummy tweet with raw content")
            cleaned_content = re.sub(r'\s+', ' ', markdown).strip()
            if len(cleaned_content) > 50:  # Only if we have substantial content
                tweets = [{
                    'text': cleaned_content[:1000],  # Limit length to avoid excessive content
                    'author': current_author or 'Unknown',
                    'timestamp': 'Tweet 1'
                }]
        
        return tweets
    
    def _finalize_current_tweet(self, current_lines: List[str], tweets: List[Dict], author: str, tweet_num: int):
        """
        Finalize a tweet from accumulated lines
        """
        if not current_lines:
            return
        
        # Join lines and clean up
        tweet_text = ' '.join(current_lines).strip()
        
        # Extract any author mentions from the tweet text to verify consistency
        mentioned_authors = re.findall(r'@(\w+)', tweet_text)
        
        # Only add if we have substantial content and it's from the original author
        if (len(tweet_text) > 15 and 
            not self._is_purely_ui_content(tweet_text) and
            not self._is_reply_content(tweet_text, author, mentioned_authors)):
            tweets.append({
                'text': tweet_text,
                'author': author or 'Unknown',
                'timestamp': f'Tweet {tweet_num + 1}' if tweet_num > 0 else ''
            })
    
    def _clean_tweet_line(self, line: str) -> str:
        """
        Clean a line of tweet content
        """
        # Remove excessive whitespace
        cleaned = ' '.join(line.split())
        
        # Remove common markdown artifacts
        cleaned = re.sub(r'^[#*-]\s*', '', cleaned)  # Remove markdown bullets/headers
        cleaned = re.sub(r'\[.*?\]', '', cleaned)    # Remove markdown links
        
        # Remove timestamp patterns that aren't part of content
        cleaned = re.sub(r'\b\d{1,2}[hms]\b', '', cleaned)
        cleaned = re.sub(r'\b\d{1,2}:\d{2}\s*[AP]M\b', '', cleaned)
        
        # Remove excessive punctuation
        cleaned = re.sub(r'\s*[·•]\s*', ' ', cleaned)
        
        return cleaned.strip()
    
    def _is_purely_ui_content(self, text: str) -> bool:
        """
        Check if text is purely UI content with no substantial tweet content
        """
        ui_patterns = [
            r'^\s*\d+\s*$',  # Just numbers
            r'^\s*[·•]+\s*$',  # Just dots/bullets
            r'^\s*@\w+\s*$',  # Just mentions
            r'^\s*(Reply|Retweet|Like|Share)\s*$',  # Just actions
            r'^\s*\d+[hms]\s*$',  # Just timestamps
        ]
        
        return any(re.match(pattern, text, re.IGNORECASE) for pattern in ui_patterns)
    
    def _is_reply_content(self, text: str, original_author: str, mentioned_authors: List[str]) -> bool:
        """
        Check if the content appears to be a reply rather than part of the original thread
        """
        # Convert to lowercase for case-insensitive matching
        text_lower = text.lower()
        
        # Direct reply indicators
        reply_phrases = [
            'replying to',
            'in reply to', 
            'reply to this',
            '@' + (original_author.lower() if original_author else ''),
            'responding to',
            'this is in response to'
        ]
        
        # Check for reply phrases
        has_reply_indicator = any(phrase in text_lower for phrase in reply_phrases if phrase)
        
        # Check if this appears to be addressing someone else (multiple @mentions)
        if mentioned_authors and original_author:
            # If there are mentions of accounts other than the original author
            other_mentions = [a for a in mentioned_authors if a.lower() != original_author.lower()]
            # Even a single mention of another user often indicates a reply
            if len(other_mentions) >= 1:
                return True
        
        # Check for conversational patterns typical of replies
        conversational_patterns = [
            r'^@\w+',  # Starts with @mention
            r'thanks for',
            r'thank you for',
            r'you\'re right',
            r'i agree',
            r'good point',
            r'exactly',
            r'yes\s*[,!.]',
            r'no\s*[,!.]'
        ]
        
        has_conversational_pattern = any(re.search(pattern, text_lower) for pattern in conversational_patterns)
        
        return has_reply_indicator or has_conversational_pattern
    
    def _fallback_content_extraction(self, markdown: str, author: str) -> List[Dict]:
        """
        Fallback method to extract content when structured parsing fails
        """
        # Remove common UI elements and get clean content
        lines = markdown.split('\n')
        content_lines = []
        
        for line in lines:
            cleaned = line.strip()
            if (cleaned and 
                len(cleaned) > 10 and
                not any(ui_term in cleaned.lower() for ui_term in [
                    'twitter', 'home', 'explore', 'notifications', 'what\'s happening',
                    'trending', 'follow', 'log in', 'sign up', 'search'
                ])):
                content_lines.append(cleaned)
        
        if not content_lines:
            return []
        
        # Join all content and split into reasonable chunks
        full_content = ' '.join(content_lines)
        
        # Try to split on natural boundaries like periods, but ensure minimum length
        sentences = re.split(r'[.!?]\s+', full_content)
        tweets = []
        current_chunk = ''
        
        for sentence in sentences:
            if len(current_chunk + sentence) < 500:  # Twitter-like limit
                current_chunk += sentence + '. '
            else:
                if current_chunk.strip():
                    tweets.append({
                        'text': current_chunk.strip(),
                        'author': author or 'Unknown',
                        'timestamp': f'Tweet {len(tweets) + 1}'
                    })
                current_chunk = sentence + '. '
        
        # Add the final chunk
        if current_chunk.strip():
            tweets.append({
                'text': current_chunk.strip(),
                'author': author or 'Unknown',
                'timestamp': f'Tweet {len(tweets) + 1}'
            })
        
        return tweets
    
    def _post_process_tweets(self, tweets: List[Dict]) -> List[Dict]:
        """
        Post-process tweets to merge short ones and split long ones
        """
        if not tweets:
            return tweets
        
        processed_tweets = []
        
        for tweet in tweets:
            text = tweet['text']
            
            # If tweet is very long, try to split it
            if len(text) > 800:
                chunks = self._split_into_chunks(text, 400)
                for i, chunk in enumerate(chunks):
                    processed_tweets.append({
                        'text': chunk,
                        'author': tweet['author'],
                        'timestamp': f"{tweet['timestamp']} (part {i+1})" if tweet['timestamp'] else f"Part {i+1}"
                    })
            else:
                processed_tweets.append(tweet)
        
        # Merge very short adjacent tweets (under 50 characters)
        final_tweets = []
        i = 0
        while i < len(processed_tweets):
            current = processed_tweets[i]
            
            # If current tweet is short and there's a next tweet by the same author
            if (i < len(processed_tweets) - 1 and 
                len(current['text']) < 50 and 
                processed_tweets[i+1]['author'] == current['author']):
                
                # Merge with next tweet
                merged_text = current['text'] + ' ' + processed_tweets[i+1]['text']
                final_tweets.append({
                    'text': merged_text,
                    'author': current['author'],
                    'timestamp': current['timestamp']
                })
                i += 2  # Skip the next tweet as it's been merged
            else:
                final_tweets.append(current)
                i += 1
        
        return final_tweets
    
    def _split_into_chunks(self, text: str, max_length: int = 280) -> List[str]:
        """
        Split long text into smaller chunks at sentence boundaries
        """
        sentences = re.split(r'[.!?]\s+', text)
        chunks = []
        current_chunk = ''
        
        for sentence in sentences:
            if len(current_chunk + sentence) <= max_length:
                current_chunk += sentence + '. '
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + '. '
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks

# Example usage and testing
if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    async def test_scraper():
        scraper = ThreadScraper()
        test_url = "https://x.com/skyeepl/status/1939941174606799254"
        result = await scraper.scrape_thread(test_url)
        print(f"Success: {result['success']}")
        if result['success']:
            print(f"Found {result['thread_data']['total_tweets']} tweets")
            print(f"Author: {result['thread_data']['author']}")
            print("\nFirst tweet:")
            print(result['thread_data']['tweets'][0]['text'][:200] + "...")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
    
    # Run the test
    asyncio.run(test_scraper())