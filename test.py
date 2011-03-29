import gdata.docs.service
from googlecred import *

# Create a client class which will make HTTP requests with Google Docs server.
gd_client = gdata.docs.service.DocsService()
gd_client.ClientLogin(sekret_username, sekret_password)


ms = gdata.MediaSource(file_path='./testing.txt', content_type=gdata.docs.service.SUPPORTED_FILETYPES['TXT'])
entry = gd_client.Upload(ms, 'testing')
print 'Document now accessible online at:', entry.GetAlternateLink().href

# Query the server for an Atom feed containing a list of your documents.
documents_feed = gd_client.GetDocumentListFeed()
for document_entry in documents_feed.entry:
  doc_entry = document_entry
  break

uri = ('https://docs.google.com/feeds/documents/private/full/'
       '-/mine?max-results=1')
feed = gd_client.GetDocumentListFeed(uri)
acl_feed = gd_client.GetDocumentListAclFeed(feed.entry[0].GetAclLink().href)
for acl_entry in acl_feed.entry:
  print '%s - %s (%s)' % (acl_entry.role.value, acl_entry.scope.value, acl_entry.scope.type)
