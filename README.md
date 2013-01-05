# TrueCrypt Volume Manager #

Linux has DM-CRYPT, FreeBSD has GEOM_ELI and Oracle is holding ZFS encryption options open source. The incompatible nature of encrypted storage throughout various UNIX systems is an obvious problem. TrueCrypt supports most popular platforms but until now there hasn't been a simple way to organize and maintain TrueCrypt containers over different types of systems. TrueCrypt Volume Manager aims to be this bridge.

TrueCrypt Volume Manager, shortened TCVM, is a UNIX shell environment written in Python. It provides a simple CLI shell interface to easily create, mount, unmount and list containers and also the possibility to easily change the passphrase of a given encryption container. Since TCVM is intended to run as a UNIX shell this allows you to securely administrate your TrueCrypt containers over the SSH protocol.

TCVM also provides the function to automatically generate secure passphrases for TrueCrypt containers and store the passphrases in a separate container. This function is fully optional to use and is essentially inspired by the KeePass project. TCVM flexes a custom wrapper for TrueCrypt.

Please note that TCVM is still new and may be slightly rough around the edges. I am happy to fix any issue you may encounter.

## Installation ##

Download the files and create a new user. Specify shell.py as the user's shell. You can access the user the normal way: either by logging in as the user directly, by using su or over SSH. Make sure that you set the correct permissions for the user's HOME and allow it to mount TrueCrypt containers.

## Usage ##

After you've installed it and set everything up properly using TCVM is very straight forward. There is a help command that you can read whenever. Commands are written to be easily remembered and tab completed. Just to paint you the picture your first time using TCVM will look something like this:

<pre># su cvm
:: TrueCrypt Volume Manager (c) 2013 qnrq ::
:: type help for help for help for help.. ::
WARNING: Missing configuration file, run configure
TCVM> help
Command                      Description
-------                      -----------
help                         Shows this help
clear                        Clears the terminal
showconf                     Prints current configuration table
configure                    Configuration wizard
create                       Creates encrypted container (wizard)
chpass <drive>               Changes passphrase of given drive
list <all|mounted>           Lists located containers
mount <drive> <path>         Mounts a drive
unmount <all|drive>          Unmounts a drive
exit                         Exits tcvm
TCVM> configure
Container location (default: /home/cvm/containers/): 
Use master container to store passphrases? (default yes) [Y/n]: y
Passphrase: 
Your passphrase should really be at least 20 characters, but I won't stand in your way.
Verify passphrase: 
Creating container /home/cvm/containers/master.tc
Create first container? (default yes) [Y/n]: y
Volume type:
0: Normal
1: Hidden
(Default 0)
: 0
Container name: demo.tc
Size int(Gb): 1
Encryption algorithm: 
0: AES
1: Serpent
2: Twofish
3: AES-Twofish
4: AES-Twofish-Serpent
5: Serpent-AES
6: Serpent-Twofish-AES
7: Twofish-Serpent
(Default 4)
: 0
Hash algorihm:
0: RIPEMD-160
1: SHA-512
2: Whirlpool
(Default 0)
: 1
Filesystem:
0: None
1: FAT
2: EXT2
3: EXT3
4: EXT4
: 1
hash        : SHA-512
encryption  : AES
filesystem  : FAT
path        : /home/cvm/containers/demo.tc
volume-type : Normal
size        : 1073741824
Mounting container '/home/cvm/containers/master.tc'...
Passphrase: 
Creating container '/home/cvm/containers/demo.tc'
Would you like to mount demo.tc now? (default yes) [Y/n]: n
TCVM> list
Mounted  Container
----------------------------------
        /home/cvm/containers/master.tc
        /home/cvm/containers/demo.tc
TCVM> exit
Bye!</pre>
