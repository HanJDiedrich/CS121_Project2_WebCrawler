import logging
import re
from urllib.parse import urlparse #Breaks url into components (scheme, netloc, path, params, query,fragment,username, password, hostname, port)

from urllib.parse import urljoin # Used to build an absolute URL
from lxml import html, etree

logger = logging.getLogger(__name__)

class Crawler:
    """
    This class is responsible for scraping urls from the next available link in frontier and adding the scraped links to
    the frontier
    """

    def __init__(self, frontier, corpus):
        self.frontier = frontier
        self.corpus = corpus

    def start_crawling(self):
        """
        This method starts the crawling process which is scraping urls from the next available link in frontier and adding
        the scraped links to the frontier
        
        
        Also calculate/record analytics here
        1. Visited subdomains, count how many unique URLs processed from each subdomain (Dict)
        2. Page with most valid out links (Dict)
        3. List of downloaded URLs and identified traps (List)
        4. Longest page in words (exclude html markup) (int)
        5. 50 most common words, ignore stop words (List)
        """
        visited_Subdomains = {}
        valid_Out_Links = {}
        downloaded_URLS = []
        identified_Traps = []
        longest_Page = 0
        most_Common_Words = []
        
        english_Stop_Words = "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at", 
        "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", 
        "can't", "cannot", "could", "couldn't", 
        "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", 
        "each", 
        "few", "for", "from", "further", 
        "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", 
        "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself",
        "let's", 
        "me", "more", "most", "mustn't", "my", "myself", 
        "no", "nor", "not", 
        "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", 
        "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", 
        "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under", "until", 
        "up", 
        "very", 
        "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", 
        "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"


        while self.frontier.has_next_url():
            url = self.frontier.get_next_url()
            logger.info("Fetching URL %s ... Fetched: %s, Queue size: %s", url, self.frontier.fetched, len(self.frontier))
            url_data = self.corpus.fetch_url(url)
            
            #Analytics
            # 1 visited subdomains
            components = urlparse(url) # breaks down url into components
            splitHostname = components.hostname.split(".") # Splits the hostname ex. ics.uci.edu, ics is the subdomain
            if len(splitHostname) > 1: # Check if there is a subdomain
                subdomain = splitHostname[0]
                if subdomain in visited_Subdomains.keys():
                    # Add url to subdomain and count
                    visited_Subdomains[subdomain]['uniqueURLs'].add(url)
                    visited_Subdomains[subdomain]['count'] = len(visited_Subdomains[subdomain]['uniqueURLs'])

                else: # Create a new key, Value pair
                    visited_Subdomains[subdomain] = {'count' : 0, 'uniqueURLs' : set()}
                    visited_Subdomains[subdomain]['uniqueURLs'].add(url)
                    visited_Subdomains[subdomain]['count'] = len(visited_Subdomains[subdomain]['uniqueURLs'])

            # Else No subdomain, for example a website like www.uci.edu

            # 3 downloaded urls
            downloaded_URLS.append(url)
            
            print(f"PAGE URL: {url_data.get('url')}") #debugg
            for next_link in self.extract_next_links(url_data):
                if self.is_valid(next_link):
                    if self.corpus.get_file_name(next_link) is not None:
                        self.frontier.add_url(next_link)

    def extract_next_links(self, url_data):
        """
        The url_data coming from the fetch_url method will be given as a parameter to this method. url_data contains the
        fetched url, the url content in binary format, and the size of the content in bytes. This method should return a
        list of urls in their absolute form (some links in the content are relative and needs to be converted to the
        absolute form). Validation of links is done later via is_valid method. It is not required to remove duplicates
        that have already been fetched. The frontier takes care of that.

        Suggested library: lxml
        
        url_data is a dictionary of keys...
        url : 
        content : 
        size : 
        content_type : 
        http_code : 
        is_redirected : 
        final_url : 
        """
        
        outputLinks = []
        
        # Check if the 'content' key exists and if the key has a value, if not then the url is not in the corpus and we will go onto the next url
        if url_data.get('content') and url_data['content'] is not None:
            #content_type = url_data.get('content-type')
            #print(f'URL CONTENT TYPE: {content_type}')
            
            '''
            #Exit early when we get to a .classpath
            if url_data.get('final_url') and url_data['final_url'].endswith('.classpath'):
                return outputLinks
            '''
            #print(f"PAGE URL: {url_data.get('url')}")
            # Assuming content is UTF-8 encoded, decode the binary into a string
            content = url_data['content']#.decode('utf-8', errors='ignore') 

            try:
                if content.strip(): # Remove trailing whitespace just in case a document is only white space    
                    # Parse content using lxml library, create heirarchal structure of html document
                    tree = html.fromstring(content)
                    # Extract links from the tree.
                    # Links are identified by href attributes
                    for link in tree.xpath('//a/@href'):
                        #Absolute for includes protocol, subdomain, domain, and path
                        #urlJoin(base_url, relative_url)
                        absolute_url = urljoin(url_data['final_url'], link)
                        outputLinks.append(absolute_url)
                        
            except etree.ParserError as e:
                pass
            
        return outputLinks
    

    def is_valid(self, url):
        """
        Function returns True or False based on whether the url has to be fetched or not. This is a great place to
        filter out crawler traps. Duplicated urls will be taken care of by frontier. You don't need to check for duplication
        in this method
        """
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        
        
        try:
            if parsed.scheme not in {"http","https"}:
                return False
            
            return ".ics.uci.edu" in parsed.hostname \
                   and not re.match(".*\.(css|js|bmp|gif|jpe?g|ico" + "|png|tiff?|mid|mp2|mp3|mp4" \
                                    + "|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf" \
                                    + "|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1" \
                                    + "|thmx|mso|arff|rtf|jar|csv" \
                                    + "|rm|smil|wmv|swf|wma|zip|rar|gz|pdf)$", parsed.path.lower())

        except TypeError:
            print("TypeError for ", parsed)
            return False

        '''
        CRAWLER TRAPS
        Repetetive patterns
        Pages with duplicate tiles, meta descriptions, headings
        
        
        '''
        
