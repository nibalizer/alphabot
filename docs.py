#!/usr/bin/env python

"""The methods for google doc creation/trashing and url shortening

This module uses the google docs list api and tinyurl to generate and trash
links to template documents on the respective add and remove of trips from
trailbot's logs.

There are a few utility methods to add the trip description to the template
when uploading, but the main work is done in the docify() and dedocify()
methods. It's all on my google account too, so I keep my credentials very
secret in googlecred.py.

"""

import gdata.docs.data
import gdata.docs.client
import gdata.acl.data
import tinyurl

from googlecred import *

# template used for generated docs
filename = './template.txt'

def add_first(prepend):
    """adds the trip description to the first line of the template"""
    f = open(filename, 'r+')
    old = f.readlines()
    old.insert(0, prepend + '\n')
    f.seek(0)
    f.writelines(old)
    f.close()

def remove_first():
    """removes the trip description so the template can be used later"""
    f = open(filename, 'r+')
    old = f.readlines()
    old = old[1:]
    f.seek(0)
    f.writelines(old)
    f.truncate()
    f.close()

def docify(prepend):
    """creates and uploads a shared google doc from the template in filename

    This method is only called when adding a new trip.

    This first alters the template document to have the trip info stored on the
    first line of the file. It then proceeds to set up a client for the google
    docs interactions using my secret credentials.

    The edited template is uploaded with a generic name and the link to the
    document is shortened to be returned. The document is then found in the
    DocsList and the ACL permissions are altered so anyone can edit the file.

    Before returning the shortened link, the template is restored by removing
    the trip description from the first line.

    """

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
    """trashes a matching google doc from my account
    
    This method is called when removing a trip with keywords about the trip.
    After logging in to the google account, the DocsList feed is searched for
    files containing the trip keywords, then the matching file is trashed.

    A matching trip has already been found when this method is called, so as
    long as the google doc was generated when the trip was added, a match 
    should be found to trash.

    """

    client = gdata.docs.client.DocsClient(source='trailbot')
    client.ClientLogin(sekret_username, sekret_password, client.source)

    search = to_remove.replace(' ','+')
    urluri = 'https://docs.google.com/feeds/default/private/full?q=' + search
    feed = client.GetDocList(uri=urluri)
    
    if feed.entry:
        doc_entry = feed.entry[0]
        client.Delete(doc_entry)
