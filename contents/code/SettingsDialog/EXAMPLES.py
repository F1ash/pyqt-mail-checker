# -*- coding: utf-8 -*-

EXAMPLES = '\n\
EXAMPLES :\n\
(Thanks to Murz at http://kde-look.org)\n\
\n\
1. Open thunderbird and selecting needed folder (folder path you must enter manually):\n\
thunderbird mailbox://someone@pop.example.net/Inbox\n\
\n\
2. Activate evolution window and select mail component\n\
evolution -c mail\n\
\n\
For kmail1 and kdepim < 4.6:\n\
3. Activate kmail window (for kmail1 with kdepim 4.4 or earlier) and select the specific folder:\n\
/usr/bin/qdbus org.kde.kmail /KMail org.kde.kmail.kmail.selectFolder /1287421332/Inbox; /usr/bin/wmctrl -x -R kmail\n\
For get folders id you can use command:\n\
/usr/bin/qdbus org.kde.kmail /KMail org.kde.kmail.kmail.folderList\n\
\n\
For use internal mailVeiwer select < integrated mail Viewer >.\n\
'
