import os
import Skype4Py

if os.name == "nt":
    print("Windows")
    #32 bit and 64 bit windows behave differently with Skype
    if 'PROGRAMFILES(X85)' in os.environ:
        sconn = Skype4Py.Skype() #64-bit
    else:
        sconn = Skype4Py.Skype() #32-bit
elif os.name == "os2":
    print("Mac")
    sconn = Skype4Py.Skype()
else:
    print("Linux machine or similar")
    sconn = Skype4Py.Skype(Transport='x11')

#Now go do the usual Skype API things.
