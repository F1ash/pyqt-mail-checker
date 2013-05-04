templates = '\n\
< integrated mail Viewer >\n\
thunderbird mailbox://someone@pop.example.net/Inbox\n\
evolution -c mail\n\
/usr/bin/qdbus org.kde.kmail /KMail org.kde.kmail.kmail.selectFolder /1287421332/Inbox; /usr/bin/wmctrl -x -R kmail\n\
/usr/bin/qdbus org.kde.kmail /KMail org.kde.kmail.kmail.folderList\n\
'
