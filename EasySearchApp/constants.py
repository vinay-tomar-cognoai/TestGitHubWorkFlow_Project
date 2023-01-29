STOP_WORDS = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through',
              'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', 'couldn', 'didn', 'doesn', 'hadn', 'hasn', 'haven', 'isn', 'ma', 'mightn', 'mustn', 'needn', 'shan', 'shouldn', 'wasn', 'weren', 'won', 'wouldn']

HTTP_CHOICES = (
    ("https", "HTTPS"),
    ("http", "HTTP")
)

BANK_KEYWORDS_ADD = ['demat',
                     'loan',
                     'yojna',
                     'atal',
                     'gst',
                     'nri',
                     'mutual',
                     'icici',
                     'kotak',
                     'sbi',
                     'kyc'
                     ]

BANK_KEYWORDS_REMOVE = ['laon',
                        'mat',
                        'meat',
                        'esmat',
                        'dmae',
                        'eat',
                        'dat',
                        'drat',
                        'dma',
                        'dmt',
                        'metal',
                        'food',
                        'badhan']

RELATED_WORDS = {
    "apr": "annual percentage rate",
    "a/c": "account",
    "mf": "mutual funds",
    "bips": "bank Internet payment system",
    "chips": "clearing house interbank payment system",
    "eftpos": "electronic funds transfer at point of sale",
    "apv": "Adjusted present value",
    "apa": "Advance pricing agreement",
    "aar": "Average accounting return"
}

MAX_INTENT_PER_PAGE = 200

PDF_SEARCH_ACTIVE_STATUS = "active"
PDF_SEARCH_INACTIVE_STATUS = "inactive"
PDF_SEARCH_INDEXING_STATUS = "indexing"
PDF_SEARCH_NOT_INDEXED_STATUS = "not_indexed"
PDF_SEARCH_INDEXED_STATUS = "indexed"

PDF_SEARCH_STATUS_CHOICES = (
    (PDF_SEARCH_ACTIVE_STATUS, 'active'),
    (PDF_SEARCH_INACTIVE_STATUS, 'inactive'),
    (PDF_SEARCH_INDEXING_STATUS, 'indexing'),
    (PDF_SEARCH_INDEXED_STATUS, 'indexed'),
    (PDF_SEARCH_NOT_INDEXED_STATUS, 'not_indexed')
)
