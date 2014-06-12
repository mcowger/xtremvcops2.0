#XtremVCOPS 2.0

###Collect Performance Statistics from an XtremIO array and push them to vCenter Operations

####Basic Install / Run

1. Have python 2.7 or 3.4 installed…any modern mac laptop already has this.
2. Checkout the code with `git clone https://github.com/mcowger/xtremvcops2.0.git`
3. Install the requirements with `pip install -r requirements.txt` (just a couple convenience libraries - may need to do it via sudo if you don’t use python virtualenvs)
4. run the help
```

    python xtremevcops-rest.py -h
    Usage: xtremevcops-rest.py [-h] XMS_IP XMS_USER XMS_PASS VCOPS_IP [--interval=<interval>] [--vcops_user=<user>] [--vcops_pass=<pass>] [--quiet] [--debug_level=<level>] [--protocol=<proto>] [--xms_base_path=<base_path>]
    
    Collect Performance Statistics from an XtremIO array and push them to vCenter Operations
    
    Arguments:
        XMS_IP       IP of XMS (required)
        XMS_USER    Username for XMS
        XMS_PASS    PAssword for XMS
        VCOPS_IP    IP of VCOPS instance
    
    
    Options:
        -h --help    show this
        --quiet      print less text
        --debug_level=<level>    Very verbose debugging [default: WARN]
        --protocol=<proto>   [http | https] [default: https]
        --xms_base_path=<base_path>  base_path for API operations [default: /api/json/types]
        --vcops_user=<user>  VC Ops User [default: admin]
        --vcops_pass=<pass>  VC Ops Password [default: P@ssword1!]
        --interval=<interval>   Sleep interval between collections [default: 60]
```

And then fill in what you need 
```
python xtremevcops-rest.py X.X.X.X demo demo X.X.X.X --debug_level=INFO
```

License: CC-BY-SA
http://creativecommons.org/licenses/by-sa/4.0/


