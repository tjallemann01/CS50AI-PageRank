import os
import random
import re
import sys
import random

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages



def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.
    """

    n = len(corpus)
    links = corpus[page]

    # If there are no outgoing links, treat the page
    # as linking to every page in the corpus.
    if not links:
        return {p: 1 / n for p in corpus}

    # Base probability of randomly choosing any page.
    probabilities = {
        p: (1 - damping_factor) / n
        for p in corpus
    }

    # Additional probability for linked pages.
    link_probability = damping_factor / len(links)

    for linked_page in links:
        probabilities[linked_page] += link_probability

    return probabilities


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling
    n pages according to transition model, starting
    with a page at random.
    """

    # Initialize visit counter for every page
    visits = {page: 0 for page in corpus}

    pages = list(corpus.keys())

    # Select the first page uniformly at random
    current_page = random.choice(pages)

    # Generate exactly n samples
    for _ in range(n):

        # Count the current page as a sample
        visits[current_page] += 1

        # Obtain the transition probabilities
        probabilities = transition_model(
            corpus,
            current_page,
            damping_factor
        )

        # Select the next page using weighted probabilities
        current_page = random.choices(
            population=list(probabilities.keys()),
            weights=list(probabilities.values()),
            k=1
        )[0]

    # Convert visit counts into probabilities
    pagerank = {
        page: visits[page] / n
        for page in corpus
    }

    return pagerank



def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively
    updating PageRank values until convergence.
    """

    n = len(corpus)

    # Initialize all pages with equal PageRank
    ranks = {
        page: 1 / n
        for page in corpus
    }

    while True:
        new_ranks = {}

        for page in corpus:

            # Base probability for every page
            rank = (1 - damping_factor) / n

            # Contributions from other pages
            for other_page, links in corpus.items():

                if not links:
                    # Pages without links distribute
                    # their rank among all pages
                    rank += (
                        damping_factor
                        * ranks[other_page] / n
                    )

                elif page in links:
                    rank += (
                        damping_factor
                        * ranks[other_page] / len(links)
                    )

            new_ranks[page] = rank

        # Check convergence across all pages
        max_change = max(
            abs(new_ranks[page] - ranks[page])
            for page in corpus
        )

        ranks = new_ranks

        if max_change <= 0.001:
            break

    return ranks


if __name__ == "__main__":
    main()
