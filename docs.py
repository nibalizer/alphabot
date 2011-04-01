import gdata.docs.data
import gdata.docs.client
import gdata.acl.data
import tinyurl

from googlecred import *

filename = './template.txt'

def add_first(prepend):
    f = open(filename, 'r+')
    old = f.readlines()
    old.insert(0, prepend + '\n')
    f.seek(0)
    f.writelines(old)
    f.close()

def remove_first():
    f = open(filename, 'r+')
    old = f.readlines()
    old = old[1:]
    f.seek(0)
    f.writelines(old)
    f.truncate()
    f.close()

def docify(prepend):
    link = ''
    
    add_first(prepend)
    
    client = gdata.docs.client.DocsClient(source='trailbot')
    client.ClientLogin(sekret_username, sekret_password, client.source);

    entry = client.Upload(filename, 'trip', content_type='text/plain')
    link = tinyurl.create_one(entry.GetAlternateLink().href)

    feed = client.GetDocList(uri='https://docs.google.com/feeds/default/private/full')
    doc_entry = feed.entry[0]

    scope = gdata.acl.data.AclScope(type='default')
    role = gdata.acl.data.AclRole(value='writer')
    acl_entry = gdata.docs.data.Acl(scope=scope, role=role)
    new_acl = client.Post(acl_entry, doc_entry.GetAclFeedLink().href)

    remove_first()

    return link

def dedocify(to_remove):
    client = gdata.docs.client.DocsClient(source='trailbot')
    client.ClientLogin(sekret_username, sekret_password, client.source)

    search = to_remove.replace(' ','+')
    urluri = 'https://docs.google.com/feeds/default/private/full?q=' + search
    feed = client.GetDocList(uri=urluri)
    
    if feed.entry:
        doc_entry = feed.entry[0]
        client.Delete(doc_entry)
