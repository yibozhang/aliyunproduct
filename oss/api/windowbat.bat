setlocal enabledelayedexpansion
for /L %%i in (1,1,100) do (

C:\Users\hanli.zyb\curl -v -f -L -o file.zip http://mtl.alibaba-inc.com/oss/mupp/10328057/build/lipo/EscortService.library.zip --create-dirs --netrc-optional --retry 2
)
