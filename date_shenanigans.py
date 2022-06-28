from datetime import datetime
from dateutil import parser
ISO_8601_FORMAT = '%Y-%m-%dT%H:%M:%S.%f%z'

def string_to_date(s: str):
    return parser.isoparse(s)

def date_to_string(date: datetime):
    s = date.strftime(ISO_8601_FORMAT)
    s1 = s[:s.find('.')]
    s2 = s[s.find('.'):s.find('+')][:-3]
    s3 = s[s.find('+'):]
    s3 = s3[:-2] + ':' + s3[-2:]
    print(date)
    print(f"{s = }", f"{s1 = }", f"{s2 = }", f"{s3 = }")
    return (s1 + s2 + s3).replace('+00:00', 'Z')

if __name__ == '__main__':
    date = '2022-05-28T21:12:01.000Z'
    print(string_to_date(date))
    print(date_to_string(string_to_date(date)))