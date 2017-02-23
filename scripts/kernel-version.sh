VER=$(grep patch sources | head -n1 | awk '{ print $2 }' | sed s/patch-// | sed s/-git.*// | sed s/.xz// | tr -d "()")

if [ -z "$VER" ] ;
then
    VER=$(grep linux sources | head -1 | awk '{ print $2 }' | sed s/linux-// | sed s/.tar.xz// | tr -d "()")
fi


