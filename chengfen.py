import requests
from .vtb import vtb
from hoshino import R, Service, util
sv=Service('查成分')


@sv.on_prefix('查成分')
async def vtb(bot,ev):
    
    mid = (ev.message.extract_plain_text().strip())
    
    if True:
        #mid=str(event.message).split('查成分')[0]
        url="https://account.bilibili.com/api/member/getCardByMid?mid={}".format(mid)
        res = requests.get(url)
        attlist = eval(res.text)
        mid=attlist['card']['mid']
        name=attlist['card']['name']
        faces=attlist['card']['face'] 
        face=f'[CQ:image,file={faces}]'
        msg=""
        attlist=attlist['card']['attentions']
        a=0
       
        for ids in attlist:
            for i in vtb:
  
                for ac in i['accounts']:
                    if str(ids) ==  ac['id']:
                        ww=i['name']['default']
                        msg+=i['name'][ww]+', '
                        a+=1

                        
        await bot.send(ev, f'{name}(uid{mid}){face}关注的vtb有{a}个:{msg}')
        
    else:
        await bot.send(ev,'出错了，可能输入的id有误')