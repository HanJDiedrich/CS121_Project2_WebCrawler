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
        2. Page with most valid out links 
        3. List of downloaded URLs and identified traps (List)
        4. Longest page in words (exclude html markup) (int)
        5. 50 most common words, ignore stop words (List)
        """
        visited_Subdomains = {}
        mostOutLinks = 0
        pageWithMostOutLinks = None
        downloaded_URLS = []
        identified_Traps = []
        longest_Page = 0
        longestPageName = None
        totalWordFreq = {}
        most_Common_Words = []
        valid_links_count = 0
        
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
            '''
            temp_vl_count = 0
            for next_link in self.extract_next_links(url_data):
                if self.is_valid(next_link):
                    temp_vl_count += 1
                    valid_out_links.add(next_link)
                    if self.corpus.get_file_name(next_link) is not None:
                        self.frontier.add_url(next_link)
            if temp_vl_count > valid_links_count:
                valid_links_count = temp_vl_count
                most_vol_url = next_link
            '''
            # 3 downloaded urls
            downloaded_URLS.append(url)
            
            #print(f"PAGE URL: {url_data.get('url')}") #debugg
            #print(f"FINAL URL: {url_data.get('final_url')}")
            #Modified extract next links to return tuple (outputLinks, words)
            
            stuff = self.extract_next_links(url_data) #tuple of outputlinks list and words list
            
            pageWords = stuff[1] #list of all words in a page
            #print(pageWords)
            #{words: freq}
            #4 longest page:
            #pageUrl, length
            #currentPage = {url, len(pageWords)}
            if max(longest_Page, len(pageWords)) == len(pageWords):# if this is a new max length
                longestPageName = url
                longest_Page = len(pageWords)
                
            #5 most common words
            if len(pageWords) != 0:
                pageWordFrequencies = self.computeWordFrequencies(self.tokenize(pageWords))
                #print(pageWordFrequencies)
                for key, value in pageWordFrequencies.items():
                    if key.lower() not in english_Stop_Words: #check and skip over stop words
                        if key not in totalWordFreq: #check if its a new word
                            totalWordFreq[key] = value
                        else:
                            totalWordFreq[key] += value #increment current value
            #print(totalWordFreq)  
            pageOutLinks = stuff[0]
            #print(f'PAGEOUTLINKS::::::{pageOutLinks}')
            outLinkCount = 0

            for next_link in pageOutLinks:
                if self.is_valid(next_link):
                    outLinkCount += 1
                    if self.corpus.get_file_name(next_link) is not None:
                        self.frontier.add_url(next_link)
                    
                else:
                    #Not valid means its a trap
                    identified_Traps.append(next_link)
            #2
            if max(mostOutLinks, outLinkCount) == outLinkCount:
                pageWithMostOutLinks = url
                mostOutLinks = outLinkCount
            
            
        #While loop over, frontier has been searched
            
        #most_Common_Words = self.sortFreq(totalWordFreq)#returns a list of tuple
        #Calculate top 50 most common words for analytic 5:
        sortedWords = {}
        for word, freq in sorted(totalWordFreq.items(), key=lambda x: -x[1]):
            sortedWords[word] = freq
        top50 = []
        topCount = 0
        for key, value in sortedWords.items():
            #print(f"{key}: {value}")
            top50.append(key)
            topCount += 1
            if topCount == 50:
                break
        print(top50)
            
        '''
        WRITE DATA TO ANALYTICS.TXT
        #1:
            visited_Subdomains = DICT{subdomain, DICT} -> {'count' : 0, 'uniqueURLs' : set()}
            to access # of different urls, go to visited_Subdomains[subdomainName]['count']
        #2:
            pageWithMostOutLinks = string of the URL
            mostOutLinks = number of max outlinks
        #3:
            downloaded_URLS = [] list
            identified_Traps = [] list
        #4: 
            longestPageName = string of the URL
            longest_Page = number length of longest page

        #5:
            list of top 50 words
        
        '''
        
        
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
        words = []
        # Check if the 'content' key exists and if the key has a value, if not then the url is not in the corpus and we will go onto the next url
        if url_data.get('content') and url_data['content'] is not None:
            #content_type = url_data.get('content-type')
            #print(f'URL CONTENT TYPE: {content_type}')
            '''
            final url is none
            #Exit early when we get to a .classpath
            if url_data.get('final_url') and url_data['final_url'].endswith('.classpath'):
                return outputLinks
            '''
            #print(f"PAGE URL: {url_data.get('url')}")
            content = url_data['content'] #.decode('utf-8', errors='ignore') # Assuming content is UTF-8 encoded, decode the binary into a string - no

            try:
                if content.strip(): # Remove trailing whitespace just in case a document is only white space    
                    # Parse content using lxml library, create heirarchal structure of html document
                    tree = html.fromstring(content)
                    #extract text content from the tree
                    #text_content = tree.xpath('//text()')
                    text_content_noHTML = tree.text_content()
                    words.extend(text_content_noHTML.split())
                    
                    # Extract links from the tree.
                    # Links are identified by href attributes
                    for link in tree.xpath('//a/@href'):
                        #Absolute for includes protocol, subdomain, domain, and path
                        #urlJoin(base_url, relative_url)
                        absolute_url = urljoin(url_data['final_url'], link)
                        outputLinks.append(absolute_url)
            except etree.ParserError:
                pass
            except ValueError:
                pass
        #print(words)
        return outputLinks, words
    

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
    
    def tokenize(self,fData): #data is a list
        #alphanumeric - we are referring to English alphabet a-z and number 0-9
        #acceptableCharacters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        tokens = []
        for word in fData:
            if word.isalnum():
                tokens.append(word.lower())
        return tokens

    #Map<Token,Count> computeWordFrequencies(List<Token>) O(n)
    def computeWordFrequencies(self,tList):
        freqMap = {}
        for i in tList:
            if i in freqMap:
                freqMap[i] += 1
            else:
                freqMap[i] = 1
                
        return freqMap
    
    def sortFreq(self,freqMap): #parameter: dictionary
        #Convert to a list of tuples
        unordered = []
        for key, value in freqMap.items():
            temp = (key, value)
            unordered.append(temp) 
        
        
        #sorted by frequency (tuples)
        ordered = self.selectionSort(unordered)
        
        #sort alphabetically for ties
        maxFreq = ordered[0][1]
        #big list
        orderedWords = []
        for i in range(maxFreq, 0, -1):
            #locate all words with i frequency:
            words = []
            for j in ordered:
                if j[1] == i:
                    words.append(j[0])
            #sort alphabetically
            words.sort()       
            for k in words:
                #create tuple (word, freq)
                temp = (k, i)
                #add our sorted words to the big list
                orderedWords.append(temp)
        
        return orderedWords

    def selectionSort(self,arr):
        n = len(arr)
        for i in range(n):
            min_index = i
            for j in range(i+1,n):
                if arr[min_index][1] < arr[j][1]: #descending order
                    min_index = j
            temp = arr[i]
            arr[i] = arr[min_index]
            arr[min_index] = temp
        return arr