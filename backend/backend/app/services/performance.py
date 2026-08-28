"""Performance policy shared by search/matching endpoints."""
DEFAULT_PAGE_SIZE=25
MAX_PAGE_SIZE=100
MATCHING_TIMEOUT_SECONDS=20

def bounded_page(page=1,page_size=DEFAULT_PAGE_SIZE):
 page=max(1,int(page)); size=min(MAX_PAGE_SIZE,max(1,int(page_size)))
 return page,size
