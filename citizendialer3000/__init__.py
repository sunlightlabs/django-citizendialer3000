__version__ = "1.0dev"

# chambers of congress

HOUSE   = 1
SENATE  = 2

CHAMBERS = {
    'H': HOUSE,
    'S': SENATE,
}

# political parties

DEMOCRAT    = 1
REPUBLICAN  = 2
INDEPENDENT = 3

PARTIES = {
    'D': DEMOCRAT,
    'R': REPUBLICAN,
    'I': INDEPENDENT,
}

__all__ = [
    'CHAMBERS', 'HOUSE', 'SENATE',
    'PARTIES', 'DEMOCRAT', 'REPUBLICAN', 'INDEPENDENT',
]