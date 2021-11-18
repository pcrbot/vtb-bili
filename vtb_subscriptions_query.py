import json
import os

import httpx
from nonebot import CommandSession, on_startup

import hoshino
from hoshino import Service

sv = Service('查成分')

vtb_dict = {}

def load_vtb(): #我就没想懂为什么明明获取了一份名单存在本地
	global vtb_dict  #却还要利用启动时现场拿到的数据而不用存在本地的数据，要是启动时没拿到数据那不是寄了
	with open(os.path.join(os.path.dirname(__file__), 'bilibili_vtbs.json'), "r", encoding='utf8') as f: 
		vtb_dict = json.load(f)				

load_vtb()  #hoshino在启动时就会自动运行一遍写在外面的函数，不太需要@on_startup

@sv.on_command('查成分')
async def _vtb_search(session: CommandSession):
	if not vtb_dict: #防止启动时没读到数据
		load_vtb()
	bid = session.current_arg.strip()
	if not bid.isdigit():
		session.finish("格式有误，应为数字uid")
	async with httpx.AsyncClient() as client:
		try:
			resp = await client.get(
				f"https://account.bilibili.com/api/member/getCardByMid?mid={bid}", timeout=10)
			if resp.status_code != 200:
				session.finish(f"获取关注列表失败：HTTP {resp.status_code}\n请检查账号的隐私设置")
		except Exception as e:
			hoshino.logger.exception(e)
			session.finish(f"获取关注列表失败：{e}\n请联系维护组")
	try:
		data = resp.json()
		subscriptions = set([str(x) for x in data["card"]["attentions"]])
		vtbs = set(vtb_dict.keys())
		subscribe_vtbs = subscriptions & vtbs
		subscribe_vtbs_name = [vtb_dict[x] for x in subscribe_vtbs]
		message = f"{data['card']['name']} 关注的vtb有{len(subscribe_vtbs)}位，TA们是：\n{'，'.join(subscribe_vtbs_name)}"
	except Exception as e:
		hoshino.logger.exception(e)
		message = f"检索关注列表时失败:{e}\n请检查账号的隐私设置"

	session.finish(message)


@sv.on_command('更新vtb') #改为手动触发，也可以改成定时触发，这样比只能启动时触发好多了
async def _update_vtb_list(session: CommandSession):  # 只在启动时更新  #这里感觉应该另写成一个函数，然后检测到命令时调用会合理一些
	global vtb_dict
	hoshino.logger.info("更新vtb名单...")
	async with httpx.AsyncClient() as client:
		try:
			resp = await client.get(
				f"https://vdb.vtbs.moe/json/list.json", timeout=10)
			if resp.status_code != 200:
				session.finish("更新vtb列表时发生错误")
				hoshino.logger.error(f"更新vtb列表时发生错误:HTTP {resp.status_code}")
				return
		except Exception as e:
			session.finish("更新vtb列表时发生错误")
			hoshino.logger.exception(e)
			hoshino.logger.error(f"更新vtb列表时发生错误:{repr(e)}")
			return
		data = resp.json()["vtbs"]
		for i in data:  #暴力处理算法，强行将需要的数据移至[0]位置
			for ii in range(0,10):
				try:
					if i["accounts"][ii].get("platform") == 'bilibili':
						i["accounts"][0] = i["accounts"][ii]
						break
				except:
					break
		bilibili_vtbs = filter(lambda x: len(x["accounts"]) != 0 and x["accounts"][0].get("platform") == 'bilibili',
							   data)
		bilibili_vtbs_dict = {x["accounts"][0].get(
			"id"): x["name"][x["name"]["default"]] for x in bilibili_vtbs}
		with open(os.path.join(os.path.dirname(__file__), 'bilibili_vtbs.json'), 'w', encoding='utf8') as f:
			json.dump(bilibili_vtbs_dict, f, ensure_ascii=False, indent=2)
		vtb_dict = bilibili_vtbs_dict
		with open('C:\/Users/Administrator/Desktop/bilibili_vtbs.json', 'w', encoding='utf8') as f:
			json.dump(data, f, ensure_ascii=False, indent=2)
		
		message = "更新完成"

		session.finish(message)
