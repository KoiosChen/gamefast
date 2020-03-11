from mailmerge import MailMerge
from datetime import date

template = 'gf.docx'

document = MailMerge(template)

print(document.get_merge_fields())