# Jianxian Game Helper

This is a bot clent for WuXingXiuZhen-JianXian with the feature of supportting batch accounts.

## Reqiurement

```
python3
 - flask
```

## Usage

### Web daemon

To start a web daemon, you could use `FALSK_APP=web.py nohup flask run &`. This will start a web server at background. Note the account.csv stores the credentials for accounts.

### Mannual Usage

To manipulate a specific account, you could start `python3` first, then type `from helper import Account` and use `a=Account()` to initilize an object. Note that you should assign parameters properly.


