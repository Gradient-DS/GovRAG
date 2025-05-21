import requests
from bs4 import BeautifulSoup
import json
import os
from urllib.parse import urljoin

# Base URL for NOS news
BASE_URL = "https://nos.nl"
NEWS_PATH = "/nieuws" # Main news page
MAX_ARTICLES = 20  # Limit the number of articles to scrape

def scrape_article_content(article_url):
    try:
        response = requests.get(article_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Updated selectors for article body - trying common patterns
        # Look for a main article container first, then paragraphs within it.
        # These are educated guesses and might need further refinement.
        article_container = (soup.find('article') or 
                            soup.find('div', class_=lambda x: x and ('article--full__body' in x or 'article_body' in x or 'article-content' in x)) or 
                            soup.find('div', attrs={'role': 'main'}) or 
                            soup.find('main'))
        
        content_parts = []
        if article_container:
            # Prioritize paragraphs with specific classes often used for article text
            paragraphs = article_container.find_all('p', class_=lambda x: x and ('paragraph' in x or 'textblock' in x or 'article__paragraph' in x))
            if not paragraphs: # Fallback to all paragraphs within the container
                paragraphs = article_container.find_all('p')
            
            for p in paragraphs:
                # Avoid paragraphs that are clearly captions or metadata
                if p.find_parent(class_=lambda x: x and ('caption' in x or 'meta' in x or 'byline' in x)):
                    continue
                text = p.get_text(separator='\n', strip=True)
                if text: # Add non-empty paragraphs
                    content_parts.append(text)
            
            if content_parts:
                return "\n\n".join(content_parts) # Join paragraphs with double newline for readability

        # Fallback: if no specific container found, try to get all p tags from body, but be more restrictive
        if not content_parts:
            all_paragraphs = soup.find('body').find_all('p') if soup.find('body') else []
            for p in all_paragraphs:
                # Simple heuristic: assume longer paragraphs are more likely main content
                text = p.get_text(strip=True)
                if len(text) > 100 : # Arbitrary length, adjust as needed
                    content_parts.append(text)
            if content_parts:
                 return "\n\n".join(content_parts)

        print(f"Could not find main content body for {article_url}")
        return "Content not found."
        
    except requests.RequestException as e:
        print(f"Error fetching article {article_url}: {e}")
        return "Could not fetch content."
    except Exception as e:
        print(f"Error parsing article {article_url}: {e}")
        return "Could not parse content."

def run_scraper():
    scraped_data = []
    target_url = urljoin(BASE_URL, NEWS_PATH)
    print(f"Scraping main news page: {target_url}")

    try:
        response = requests.get(target_url, timeout=15) # Increased timeout
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Updated selectors for article links and titles on the news overview page
        # Looking for <a> tags that likely link to articles and contain a title-like element
        article_elements = soup.select(
            'article a[href*="/artikel/"], ' +
            'div[class*="article"] a[href*="/artikel/"], ' +
            'li[class*="list-item"] a[href*="/artikel/"], ' +
            'a[href*="/artikel/"][class*="tile"], ' +
            'a[href*="/artikel/"] > h1, a[href*="/artikel/"] > h2, a[href*="/artikel/"] > h3'
        )
        
        # If the above is too broad or misses items, we can refine.
        # This new selector tries to find common list item patterns for news articles
        if not article_elements:
            article_elements = soup.find_all('a', href=lambda x: x and "/artikel/" in x)


        unique_links = set()
        article_count = 0

        for link_element_candidate in article_elements:
            # Determine the actual <a> tag and title text
            link_tag = None
            title_text = ""

            if link_element_candidate.name == 'a':
                link_tag = link_element_candidate
            else: # If a heading or other element was selected, find the parent <a>
                link_tag = link_element_candidate.find_parent('a', href=lambda x: x and "/artikel/" in x)

            if not link_tag or not link_tag.get('href'):
                continue

            href = link_tag.get('href')
            full_article_url = urljoin(BASE_URL, href)

            if full_article_url in unique_links:
                continue
            unique_links.add(full_article_url)

            # Try to find a prominent title within the link_tag or its children
            # Common title tags/classes: h1-h3, span with 'title', 'headline'
            title_element = link_tag.find(['h1', 'h2', 'h3', 'h4', 'span'], class_=[lambda x: x and ('title' in x or 'headline' in x or 'heading' in x)])
            if not title_element: # Fallback to finding any h1-h3
                title_element = link_tag.find(['h1','h2','h3'])
            
            if title_element:
                title_text = title_element.get_text(strip=True)
            else: # Fallback: Get text from the link_tag itself, or specific child span if no heading
                span_title = link_tag.find('span') # Simple span text
                if span_title:
                    title_text = span_title.get_text(strip=True)
                else:
                    title_text = link_tag.get_text(strip=True)
            
            # Clean up title if it's too long or generic
            if not title_text or len(title_text) > 150: # If title is excessively long, likely not the main title
                # Attempt to get a more concise title from an image alt text if present
                img_alt_title = link_tag.find('img', alt=True)
                if img_alt_title and img_alt_title.get('alt'):
                    title_text = img_alt_title['alt']
                elif not title_text: # if still no title
                     title_text = "Untitled Article - " + os.path.basename(href)


            print(f"Found article candidate: '{title_text.strip()[:70]}...' - {full_article_url}")
            
            content = scrape_article_content(full_article_url)
            
            if content and content not in ["Content not found.", "Could not fetch content.", "Could not parse content."]:
                scraped_data.append({
                    "title": title_text.strip(),
                    "content": content, # Already stripped and joined in scrape_article_content
                    "url": full_article_url,
                    "source": "nos.nl"
                })
                article_count += 1
                print(f"Successfully scraped: {title_text.strip()[:70]}...")
            else:
                print(f"Skipping article '{title_text.strip()[:70]}...' due to missing or invalid content.")
            
            if article_count >= MAX_ARTICLES:
                print(f"Reached max articles limit of {MAX_ARTICLES}.")
                break
        
        if not scraped_data:
            print("No articles were successfully scraped. Consider revising CSS selectors in scraper/run_all.py based on current nos.nl HTML structure.")
            # You might want to create an empty scraped.json or handle this case downstream
            # For now, we'll still write an empty list if nothing is found.
        
        output_dir = "/app/data"
        output_path = os.path.join(output_dir, "scraped.json")
        os.makedirs(output_dir, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(scraped_data, f, ensure_ascii=False, indent=4)
        
        print(f"Scraping complete. Data saved to {output_path}")
        print(f"Total articles successfully scraped: {len(scraped_data)}")

    except requests.RequestException as e:
        print(f"Error fetching main news page {target_url}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during scraping: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_scraper()
