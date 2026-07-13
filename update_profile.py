import datetime
import requests
import os
import time
import hashlib
import xml.etree.ElementTree as ET

# Configuration
USER_NAME = os.environ.get('USER_NAME', 'iambalaji-k')
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')

HEADERS = {'authorization': f'token {ACCESS_TOKEN}'} if ACCESS_TOKEN else {}
QUERY_COUNT = {'user_getter': 0, 'follower_getter': 0, 'graph_repos_stars': 0, 'recursive_loc': 0, 'graph_commits': 0, 'loc_query': 0}
OWNER_ID = None

def daily_readme(start_date):
    """
    Returns the length of time since starting professional CA track
    """
    today = datetime.date.today()
    # Manual delta calculation to avoid python-dateutil dependency
    years = today.year - start_date.year
    months = today.month - start_date.month
    days = today.day - start_date.day
    
    if days < 0:
        # borrow from previous month
        # approximate days in previous month
        prev_month = today.month - 1 if today.month > 1 else 12
        prev_year = today.year if today.month > 1 else today.year - 1
        if prev_month in [1, 3, 5, 7, 8, 10, 12]:
            days_in_prev = 31
        elif prev_month in [4, 6, 9, 11]:
            days_in_prev = 30
        else:
            days_in_prev = 29 if (prev_year % 4 == 0 and (prev_year % 100 != 0 or prev_year % 400 == 0)) else 28
        days += days_in_prev
        months -= 1
        
    if months < 0:
        months += 12
        years -= 1
        
    def format_plural(unit, word):
        return f"{unit} {word}{'s' if unit != 1 else ''}"
        
    return f"{format_plural(years, 'year')}, {format_plural(months, 'month')}, {format_plural(days, 'day')}"

def simple_request(func_name, query, variables):
    if not ACCESS_TOKEN:
        print(f"Warning: ACCESS_TOKEN not set. Mocking result for {func_name}")
        # Return a mock response object
        class MockResponse:
            def __init__(self):
                self.status_code = 200
            def json(self):
                return {'data': {
                    'user': {
                        'id': 'mock_id',
                        'createdAt': '2020-11-01T00:00:00Z',
                        'followers': {'totalCount': 42},
                        'repositories': {
                            'totalCount': 12,
                            'edges': [],
                            'pageInfo': {'endCursor': None, 'hasNextPage': False}
                        },
                        'contributionsCollection': {
                            'contributionCalendar': {'totalContributions': 150}
                        }
                    }
                }}
        return MockResponse()
        
    request = requests.post('https://api.github.com/graphql', json={'query': query, 'variables':variables}, headers=HEADERS)
    if request.status_code == 200:
        return request
    raise Exception(f"{func_name} failed with status {request.status_code}: {request.text}")

def graph_commits(start_date, end_date):
    query_count('graph_commits')
    query = '''
    query($start_date: DateTime!, $end_date: DateTime!, $login: String!) {
        user(login: $login) {
            contributionsCollection(from: $start_date, to: $end_date) {
                contributionCalendar {
                    totalContributions
                }
            }
        }
    }'''
    variables = {'start_date': start_date, 'end_date': end_date, 'login': USER_NAME}
    request = simple_request(graph_commits.__name__, query, variables)
    try:
        return int(request.json()['data']['user']['contributionsCollection']['contributionCalendar']['totalContributions'])
    except (KeyError, TypeError):
        return 0

def graph_repos_stars(count_type, owner_affiliation, cursor=None):
    query_count('graph_repos_stars')
    query = '''
    query ($owner_affiliation: [RepositoryAffiliation], $login: String!, $cursor: String) {
        user(login: $login) {
            repositories(first: 100, after: $cursor, ownerAffiliations: $owner_affiliation) {
                totalCount
                edges {
                    node {
                        ... on Repository {
                            nameWithOwner
                            stargazers {
                                totalCount
                            }
                        }
                    }
                }
                pageInfo {
                    endCursor
                    hasNextPage
                }
            }
        }
    }'''
    variables = {'owner_affiliation': owner_affiliation, 'login': USER_NAME, 'cursor': cursor}
    request = simple_request(graph_repos_stars.__name__, query, variables)
    data = request.json()
    
    try:
        repos_data = data['data']['user']['repositories']
        if count_type == 'repos':
            return repos_data['totalCount']
        elif count_type == 'stars':
            total_stars = 0
            for edge in repos_data['edges']:
                total_stars += edge['node']['stargazers']['totalCount']
            return total_stars
    except (KeyError, TypeError):
        return 0

def recursive_loc(owner, repo_name, data, cache_comment, addition_total=0, deletion_total=0, my_commits=0, cursor=None):
    query_count('recursive_loc')
    query = '''
    query ($repo_name: String!, $owner: String!, $cursor: String) {
        repository(name: $repo_name, owner: $owner) {
            defaultBranchRef {
                target {
                    ... on Commit {
                        history(first: 100, after: $cursor) {
                            totalCount
                            edges {
                                node {
                                    ... on Commit {
                                        committedDate
                                    }
                                    author {
                                        user {
                                            id
                                        }
                                    }
                                    deletions
                                    additions
                                }
                            }
                            pageInfo {
                                endCursor
                                hasNextPage
                            }
                        }
                    }
                }
            }
        }
    }'''
    variables = {'repo_name': repo_name, 'owner': owner, 'cursor': cursor}
    if not ACCESS_TOKEN:
        return 100, 10, 5  # Mock values
        
    request = requests.post('https://api.github.com/graphql', json={'query': query, 'variables':variables}, headers=HEADERS)
    if request.status_code == 200:
        repo_data = request.json().get('data', {}).get('repository', {})
        if repo_data and repo_data.get('defaultBranchRef'):
            history = repo_data['defaultBranchRef']['target']['history']
            for node in history['edges']:
                author_user = node['node']['author']['user']
                if author_user and author_user.get('id') == OWNER_ID:
                    my_commits += 1
                    addition_total += node['node']['additions']
                    deletion_total += node['node']['deletions']
            if not history['pageInfo']['hasNextPage'] or history['edges'] == []:
                return addition_total, deletion_total, my_commits
            else:
                return recursive_loc(owner, repo_name, data, cache_comment, addition_total, deletion_total, my_commits, history['pageInfo']['endCursor'])
        else:
            return 0, 0, 0
            
    force_close_file(data, cache_comment)
    raise Exception(f"recursive_loc failed with status {request.status_code}: {request.text}")

def loc_query(owner_affiliation, comment_size=0, force_cache=False, cursor=None, edges=[]):
    query_count('loc_query')
    query = '''
    query ($owner_affiliation: [RepositoryAffiliation], $login: String!, $cursor: String) {
        user(login: $login) {
            repositories(first: 60, after: $cursor, ownerAffiliations: $owner_affiliation) {
                edges {
                    node {
                        ... on Repository {
                            nameWithOwner
                            defaultBranchRef {
                                target {
                                    ... on Commit {
                                        history {
                                            totalCount
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                pageInfo {
                    endCursor
                    hasNextPage
                }
            }
        }
    }'''
    variables = {'owner_affiliation': owner_affiliation, 'login': USER_NAME, 'cursor': cursor}
    request = simple_request(loc_query.__name__, query, variables)
    
    try:
        repos_data = request.json()['data']['user']['repositories']
        edges += repos_data['edges']
        if repos_data['pageInfo']['hasNextPage']:
            return loc_query(owner_affiliation, comment_size, force_cache, repos_data['pageInfo']['endCursor'], edges)
        else:
            return cache_builder(edges, comment_size, force_cache)
    except (KeyError, TypeError) as e:
        print(f"Error in loc_query: {e}")
        return [0, 0, 0, True]

def cache_builder(edges, comment_size, force_cache, loc_add=0, loc_del=0):
    if not os.path.exists('cache'):
        os.makedirs('cache')
        
    filename = 'cache/' + hashlib.sha256(USER_NAME.encode('utf-8')).hexdigest() + '.txt'
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = f.readlines()
    except FileNotFoundError:
        data = []
        if comment_size > 0:
            for _ in range(comment_size):
                data.append('This line is a comment block. Write whatever you want here.\n')
        with open(filename, 'w', encoding='utf-8') as f:
            f.writelines(data)

    if len(data) - comment_size != len(edges) or force_cache:
        flush_cache(edges, filename, comment_size)
        with open(filename, 'r', encoding='utf-8') as f:
            data = f.readlines()

    cache_comment = data[:comment_size]
    data = data[comment_size:]
    
    for index in range(len(edges)):
        if not data[index].strip():
            continue
        parts = data[index].split()
        if len(parts) < 5:
            parts = [parts[0], '0', '0', '0', '0']
        repo_hash, commit_count = parts[0], parts[1]
        
        node_repo = edges[index]['node']
        name_w_owner = node_repo['nameWithOwner']
        
        if repo_hash == hashlib.sha256(name_w_owner.encode('utf-8')).hexdigest():
            try:
                db_ref = node_repo.get('defaultBranchRef')
                if db_ref:
                    actual_commit_count = db_ref['target']['history']['totalCount']
                    if int(commit_count) != actual_commit_count:
                        owner, repo_name = name_w_owner.split('/')
                        loc = recursive_loc(owner, repo_name, data, cache_comment)
                        data[index] = f"{repo_hash} {actual_commit_count} {loc[2]} {loc[0]} {loc[1]}\n"
                else:
                    data[index] = f"{repo_hash} 0 0 0 0\n"
            except Exception as e:
                print(f"Error checking cache for {name_w_owner}: {e}")
                data[index] = f"{repo_hash} 0 0 0 0\n"
                
    with open(filename, 'w', encoding='utf-8') as f:
        f.writelines(cache_comment)
        f.writelines(data)
        
    for line in data:
        parts = line.split()
        if len(parts) >= 5:
            loc_add += int(parts[3])
            loc_del += int(parts[4])
            
    return [loc_add, loc_del, loc_add - loc_del, True]

def flush_cache(edges, filename, comment_size):
    with open(filename, 'r', encoding='utf-8') as f:
        data = []
        if comment_size > 0:
            data = f.readlines()[:comment_size]
    with open(filename, 'w', encoding='utf-8') as f:
        f.writelines(data)
        for node in edges:
            f.write(hashlib.sha256(node['node']['nameWithOwner'].encode('utf-8')).hexdigest() + ' 0 0 0 0\n')

def force_close_file(data, cache_comment):
    filename = 'cache/' + hashlib.sha256(USER_NAME.encode('utf-8')).hexdigest() + '.txt'
    with open(filename, 'w', encoding='utf-8') as f:
        f.writelines(cache_comment)
        f.writelines(data)
    print(f"Partial cache saved to {filename}")

def user_getter(username):
    query_count('user_getter')
    query = '''
    query($login: String!){
        user(login: $login) {
            id
            createdAt
        }
    }'''
    variables = {'login': username}
    request = simple_request(user_getter.__name__, query, variables)
    user_data = request.json().get('data', {}).get('user', {})
    if user_data:
        return user_data.get('id'), user_data.get('createdAt')
    return 'mock_id', '2020-11-01T00:00:00Z'

def follower_getter(username):
    query_count('follower_getter')
    query = '''
    query($login: String!){
        user(login: $login) {
            followers {
                totalCount
            }
        }
    }'''
    request = simple_request(follower_getter.__name__, query, {'login': username})
    try:
        return int(request.json()['data']['user']['followers']['totalCount'])
    except (KeyError, TypeError):
        return 0

def commit_counter(comment_size):
    total_commits = 0
    filename = 'cache/' + hashlib.sha256(USER_NAME.encode('utf-8')).hexdigest() + '.txt'
    if not os.path.exists(filename):
        return 0
    with open(filename, 'r', encoding='utf-8') as f:
        data = f.readlines()[comment_size:]
    for line in data:
        parts = line.split()
        if len(parts) >= 3:
            total_commits += int(parts[2])
    return total_commits

def find_by_id(element, element_id):
    """
    Recursively find an XML element by its 'id' attribute
    """
    if element.get('id') == element_id:
        return element
    for child in element:
        res = find_by_id(child, element_id)
        if res is not None:
            return res
    return None

def justify_exact(root, element_id, new_text, total_len):
    if isinstance(new_text, int):
        new_text = f"{new_text:,}"
    new_text = str(new_text)
    
    # Update target text element
    target = find_by_id(root, element_id)
    if target is not None:
        target.text = new_text
        
    # We want len(dot_string) + len(new_text) == total_len
    # So len(dot_string) == total_len - len(new_text)
    dot_len = total_len - len(new_text)
    if dot_len >= 3:
        # Format: " " + "." * (dot_len - 2) + " "
        dot_string = ' ' + ('.' * (dot_len - 2)) + ' '
    elif dot_len == 2:
        dot_string = '. '
    elif dot_len == 1:
        dot_string = ' '
    else:
        dot_string = ''
        
    dots_target = find_by_id(root, f"{element_id}_dots")
    if dots_target is not None:
        dots_target.text = dot_string

def svg_overwrite(filename, age_data, commit_data, star_data, repo_data, contrib_data, follower_data, loc_data):
    # Standard ElementTree parser works on any environment
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    tree = ET.parse(filename)
    root = tree.getroot()
    
    justify_exact(root, 'age_data', age_data, 49)
    justify_exact(root, 'commit_data', commit_data, 22)
    
    # Contributed doesn't have dots spacer
    contrib_el = find_by_id(root, 'contrib_data')
    if contrib_el is not None:
        contrib_el.text = str(contrib_data)
        
    contrib_len = len(str(contrib_data))
    repo_total_len = 8 - contrib_len
    justify_exact(root, 'repo_data', repo_data, repo_total_len)
    justify_exact(root, 'star_data', star_data, 14)
    justify_exact(root, 'follower_data', follower_data, 13)
    
    # loc_add
    loc_add_str = f"{loc_data[0]:,}" if isinstance(loc_data[0], int) else str(loc_data[0])
    add_el = find_by_id(root, 'loc_add')
    if add_el is not None:
        add_el.text = loc_add_str
        
    loc_add_len = len(loc_add_str)
    loc_total_len = 12 - loc_add_len
    justify_exact(root, 'loc_data', loc_data[2], loc_total_len)
    justify_exact(root, 'loc_del', loc_data[1], 9)
    
    # Write back
    tree.write(filename, encoding='utf-8', xml_declaration=True)

def query_count(funct_id):
    global QUERY_COUNT
    QUERY_COUNT[funct_id] += 1

if __name__ == '__main__':
    print(f"Updating profile for user: {USER_NAME}")
    
    # Retrieve user stats
    OWNER_ID, acc_date = user_getter(USER_NAME)
    
    # Uptime since birthday (Sep 28, 2002)
    start_date = datetime.date(2002, 9, 28)
    age_data = daily_readme(start_date)
    
    total_loc = loc_query(['OWNER', 'COLLABORATOR', 'ORGANIZATION_MEMBER'], 7)
    commit_data = commit_counter(7)
    star_data = graph_repos_stars('stars', ['OWNER'])
    repo_data = graph_repos_stars('repos', ['OWNER'])
    contrib_data = graph_repos_stars('repos', ['OWNER', 'COLLABORATOR', 'ORGANIZATION_MEMBER'])
    follower_data = follower_getter(USER_NAME)
    
    print(f"Stats fetched: Commits={commit_data}, Stars={star_data}, Repos={repo_data}, Followers={follower_data}")
    
    # Overwrite template files
    svg_overwrite('D:/Vibe Coding/githubhome/dark_mode.svg', age_data, commit_data, star_data, repo_data, contrib_data, follower_data, total_loc[:-1])
    svg_overwrite('D:/Vibe Coding/githubhome/light_mode.svg', age_data, commit_data, star_data, repo_data, contrib_data, follower_data, total_loc[:-1])
    print("SVGs successfully updated with live statistics!")
