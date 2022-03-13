# Check Memory

pip install -U memory_profiler


#  Set LINUXCNC.IN

Tuwf line  726 sau do rebuild lai linuxcnc

LOCKFILE=/tmp/linuxcnc.lock
echo "sssssssssss"
# Check for lock file
if [ -f $LOCKFILE ]; then
  if tty -s; then
    input=y
    echo -n "LinuxCNC is still running.  Restart it? [Y/n] "
    #read input; [ -z $input ] && input=y
  elif [ -z "$DISPLAY" ]; then
    echo "No display, no tty, trying to clean up other instance automatically"
    input=y
  else
    input=y
    #input=$(@WISH@ <<EOF
#wm wi .
#puts [tk_messageBox -title LinuxCNC -message "LinuxCNC is still running.  Restart it?" -type yesno]
#exit
#EOF
#)


# ICE default IO error handler doing an exit(), pid = ..., errno = 32

mv ~/.ICEauthority ~/.ICEauthority.bak 