import os
import random
import re
import sys

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

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    pagerankdict = {}
    pagelinksset = corpus[page]
    if pagelinksset is None or len(pagelinksset) == 0:
        pagerank = 1/len(corpus)
        for k in corpus.keys():
            pagerankdict[k] = pagerank
    else:
        dp = (1-damping_factor)/len(corpus)
        p = damping_factor/len(pagelinksset)
        for k in corpus.keys():
            if k == page:
                pagerankdict[k] = dp
            else:
                pagerankdict[k] = dp + p
    return pagerankdict


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pagerankdict = {}
    for k in corpus.keys():
        pagerankdict[k]=0
    rp=None
    for i in range(n):
        if i==0:
            rp = random.choice(list(corpus.keys()))
            pagerankdict[rp] = (pagerankdict[rp]+1)
        else:
            prank = transition_model(corpus,rp,damping_factor)
            plist = [k for k,v in prank.items()]
            rlist = [v for k,v in prank.items()]
            # print(plist)
            # print(rlist)
            rp = random.choices(plist,rlist,k=1)[0]
            # print(rp)
            pagerankdict[rp] = (pagerankdict[rp] + 1)
    for k,v in pagerankdict.items():
        pagerankdict[k] = v/n
    # print(corpus)
    return pagerankdict


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pagerankdict={}
    newpagerankdict={}
    N = len(corpus)
    for k in corpus.keys():
        pagerankdict[k] = 1/N
    while True:
        for p in corpus.keys():
            newpagerankdict[p] = ((1-damping_factor)/N) + pr(corpus,damping_factor,pagerankdict,p)
        if checkthresholdreached(newpagerankdict,pagerankdict,0.001):
            break
        else:
            pagerankdict = newpagerankdict

    return pagerankdict


def pr(corpus,dampingfactor,pagerankdict,p):
    numlinks = {}
    ipr = 0
    for page in corpus.keys():
        if (p in corpus[page] or len(corpus[page]) == 0) and page != p:
            if len(corpus[page]) > 0:
                numlinks[page] = len(corpus[page])
            else:
                numlinks[page] = len(corpus)
            ipr = ipr + pagerankdict[page]/numlinks[page]

    return ipr*dampingfactor

def checkthresholdreached(newdict,olddict,threshold):
    for k in newdict.keys():
        if newdict[k] - olddict[k] <= threshold:
            return True
    return False


if __name__ == "__main__":
    main()
