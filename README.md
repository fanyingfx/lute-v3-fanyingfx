# Lute v3 with chinese support



https://github.com/fanyingfx/lute-v3/assets/57335844/88519b5b-49b8-4bbd-b5f0-00b68ba29909



This is modified version of lute, it supports Chinese, accurately, it's Mandarin.

## Installation
The Installation are similar as installing Lute using pip . Only need to replace the Install Lute command 
`pip install --upgrade lute3`
> If your system is Linux I recommand to install pytorch cpu version first `pip install torch --extra-index-url https://download.pytorch.org/whl/cpu`

You can find the latest release in the [release page](https://github.com/fanyingfx/lute-v3/releases).
and copy the *.whl link then you can use command 
![image](https://github.com/fanyingfx/lute-v3/assets/57335844/f8163364-de3c-4534-ac9b-1e96f776f611)


```
pip install https://github.com/fanyingfx/lute-v3/releases/downlonad/<release tag>/lute3-<version>-none-any.whl --upgrade
```
to install the lute supporting Chinese.

## Migration
Because of some big change in the codebase, some features may not add to the lute.
I am also working on adding Chinese support to original lute, but need some time to find a suitable solution to not make a big change in Lute's code.

The database is full compatible with lute's db, but I also recommend you to create a new database to use.

If you want to migrate previous lute to this version, you can copy your previous database and then in this version of lute's Language Setting,
change the Parse as to Mandarin.
![image](https://github.com/fanyingfx/lute-v3/assets/57335844/7ce900cb-fd09-4962-9214-37c45762ae41)

## User Defined Dictionary
Another thing, it supports the user defined Chinese words dictionary to make parsed result more correct.
after start the lute and mark some terms in reading, then in the lute's data folder you can find a file `mandarin.user_dict.txt`.
in the file: 
```
竹条,编 // it means you make the parser always pase "竹条编" as "竹条" and "编", this is for multiple-words terms
珍珠鸟 // it mean parser will parse 珍珠鸟 as one terms
```
You can also add your define terms in the file , only Chinese  with English comma ',' not Chinese's comma '，'



## 
You can reach me in Lute's discord server @fanyingfx

