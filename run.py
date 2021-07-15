from time import sleep
import requests
from bs4 import BeautifulSoup
import re
import os
import random

class GetCookieFacebook():
	def __init__(self, uID, passWord, key2FA):
		self.uID = uID
		self.passWord = passWord
		self.key2FA = key2FA
		self.ses = requests.session()

	# lay header
	def get_headers(self):
		headers = {
			'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
			'accept-language': 'en-US,en;q=0.9',
			'cache-control': 'max-age=0',
			'sec-fetch-dest': 'document',
			'sec-fetch-mode': 'navigate',
			'sec-fetch-site': 'none',
			'sec-fetch-user': '?1',
			'upgrade-insecure-requests': '1',
			'user-agent': 'Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36',
		}
		return headers

	def get_otp(self):
		key2FA = self.key2FA.replace(' ', '')
		url = f'https://2fa.live/tok/{key2FA}'
		res = requests.get(url)
		data = res.json()
		otp = data['token']
		return otp

	# loc attribute
	def fill_att(self, data):
		f = { 'url_post': None, 'lsd': None, 'jazoest': None, 'm_ts': None, 'li': None, 'nh': None }
		soup = BeautifulSoup(data, 'html.parser')
		root = soup.find(id='root')
		form = root.form
		f['url_post'] = 'https://mbasic.facebook.com' + form.get('action')
		lst_ipt = form.find_all('input')
		for ipt in lst_ipt:
			if ipt.get('name') == 'lsd': f['lsd'] =  ipt.get('value')
			elif ipt.get('name') == 'fb_dtsg': f['fb_dtsg'] =  ipt.get('value')
			elif ipt.get('name') == 'jazoest': f['jazoest'] =  ipt.get('value')
			elif ipt.get('name') == 'm_ts': f['m_ts'] =  ipt.get('value')
			elif ipt.get('name') == 'li': f['li'] =  ipt.get('value')
			elif ipt.get('name') == 'nh': f['nh'] =  ipt.get('value')
		return f

	# đăng nhập facebook
	def loginFb(self):
		headers = self.get_headers()
		payload = {
			'lsd': None,
			'jazoest': None,
			'm_ts': None,
			'li': None,
			'try_number': '0',
			'unrecognized_tries': '0',
			'email': self.uID,
			'pass': self.passWord,
			'login': 'Đăng nhập'
		}
		url = 'https://mbasic.facebook.com'
		res = self.ses.get(url, headers=headers)
		# lọc phần tử
		data = res.text
		f = self.fill_att(data)

		url_post = f['url_post']
		payload['lsd'] = f['lsd']
		payload['jazoest'] = f['jazoest']
		payload['m_ts'] = f['m_ts']
		payload['li'] = f['li']
		# gửi lên facebook
		res = self.ses.post(url_post, data=payload, headers=headers)
		# vượt xác thực 2 yếu tố
		if 'checkpoint' in res.url:
			# submit 2FA
			otp = self.get_otp()
			# lọc phần tử
			data = res.text
			f = self.fill_att(data)
			payload = {
				'fb_dtsg': f['fb_dtsg'],
				'jazoest': f['jazoest'],
				'checkpoint_data': '',
				'approvals_code': otp,
				'codes_submitted': '0',
				'submit[Submit Code]': 'Gửi mã',
				'nh': f['nh']
			}
			url = 'https://mbasic.facebook.com/login/checkpoint/'
			res = self.ses.post(url, data=payload, headers=headers)
			# lọc phần tử
			data = res.text
			f = self.fill_att(data)
			payload = {
				'fb_dtsg': f['fb_dtsg'],
				'jazoest': f['jazoest'],
				'checkpoint_data': '', 
				'name_action_selected': 'save_device',
				'submit[Continue]': 'Tiếp tục',
				'nh': f['nh']
			}
			url = 'https://mbasic.facebook.com/login/checkpoint/'
			# lưu thiết bị
			res = self.ses.post(url, data=payload, headers=headers)
			# Kiểm tra
			data = res.text
			# f = open('html.html', 'w', encoding="utf8")
			# f.write(data)
			# f.close()
			check = re.search('query', data)
			if check == None:
				return False
			else:
				return True
		else:
			return False

	# đăng nhập
	def getCookie(self):
		cookie = ''
		check = self.loginFb()
		if check == True:
			# print('Login success')
			ck = self.ses.cookies.get_dict()
			for c in ck:
				cookie = cookie + f'{c}={ck[c]};'
		else:
			# print('Login failed')
			return None
		self.ses.close()
		return cookie


class CmtReact():
	def __init__(self, cookie):
		self.ses = requests.session()
		self.cookie = cookie

	def getHeaders(self):
		headers = {
			'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
			'accept-language': 'en-US,en;q=0.9',
			'cache-control': 'max-age=0',
			'sec-fetch-dest': 'document',
			'sec-fetch-mode': 'navigate',
			'sec-fetch-site': 'none',
			'sec-fetch-user': '?1',
			'upgrade-insecure-requests': '1',
			'user-agent': 'Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36',
			'cookie': self.cookie
		}
		return headers

	# lấy danh sách bào viết
	def getListPost(self):
		listPost = []

		headers = self.getHeaders()
		res = self.ses.get('https://mbasic.facebook.com/home.php', headers=headers)
		data = res.text
		soup = BeautifulSoup(data, 'html.parser')
		list_article = soup.find_all('article')
		for article in list_article:
			post = {'idPost': None, 'comment': False}
			temp = str(article)
			page_id = re.findall('"page_id"', temp)
			group_id = re.findall('"group_id"', temp)
			if len(group_id)==0:
				if len(page_id)==0: post['comment'] = True
				# tim id bài viết
				f = re.findall(r'\"like_(.*?)\"', temp)
				if len(f) != 0:
					post['idPost'] = f[0]
				else:
					continue
				listPost.append(post)
			else:
				continue
		return listPost

	# lấy thông tin bài viết
	def getInfoPost(self, idPost):
		infoPost = {
			'linkPost': None,
			'name': None, 
			'caption': '...', 
			'linkReaction': None,
			'postAtt': {
				'link':None,
				'payload': {
					'fb_dtsg': None,
					'jazoest': None,
					'comment_text': None
				}
			} 
		}
		url = 'https://mbasic.facebook.com/'+idPost
		headers = self.getHeaders()
		# get linkPost
		res = self.ses.head(url, headers=headers).headers
		if 'Location' not in res: return None
		url = res['Location']
		if '/m.' in url: url = url.replace('/m.', '/mbasic.')
		infoPost['linkPost'] = url
		# load post
		res = self.ses.get(url, headers=headers)
		soup = BeautifulSoup(res.content, 'html.parser')
		# get name
		f = soup.find_all('strong')
		if f!=[]: infoPost['name'] = f[0].text
		# get caption
		f = soup.find_all('p')
		if f!=[]:
			infoPost['caption'] = f[0].text
			if len(f[0].text) > 25:
				infoPost['caption'] = f[0].text[0:25]+'...'
		# get linkReaction
		list_a = soup.find_all('a')
		for a in list_a:
			try: url = a.get("href")	
			except: url= ''
			if url==None: continue
			if '/reactions/' in url:
				infoPost['linkReaction'] = 'https://mbasic.facebook.com'+url
				break
		# get postAtt 
		f = soup.find_all('form')
		if f!=[]:
			form = f[0]
			# get postAtt.link
			infoPost['postAtt']['link'] = 'https://mbasic.facebook.com' + form.get("action")
			list_ipt = form.find_all('input')
			for ipt in list_ipt:
				# get postAtt.fb_dtsg
				if ipt.get("name")=='fb_dtsg':
					infoPost['postAtt']['payload']['fb_dtsg'] = ipt.get("value")
				# get postAtt.jazoest
				if ipt.get("name")=='jazoest':
					infoPost['postAtt']['payload']['jazoest'] = ipt.get("value")
		return infoPost

	# comment bai viet
	def commentPost(self, postAtt, content):
		headers = self.getHeaders()
		url = postAtt['link']
		payload = postAtt['payload']
		payload['comment_text'] = content
		self.ses.post(url, data=payload, headers=headers)

	# bay to cam xúc bai viet
	def reactionPost(self, linkReaction, reaction):
		dict_reaction = {'LIKE':0, 'LOVE':1, 'THUONGTHUONG':2, 'HAHA':3, 'WOW':4, 'SAD':5, 'ANGRY':6}
		headers = self.getHeaders()
		res = self.ses.get(linkReaction, headers=headers)

		data = res.content

		soup = BeautifulSoup(data, 'html.parser')
		soup = soup.body.find(id='root')
		list_li = soup.find_all('li')	
		vt = dict_reaction[reaction]
		url = list_li[vt].a.get('href')
		link = 'https://mbasic.facebook.com' + url
		self.ses.get(link, headers=headers)

# Kiểm tra cookie die ỏ live
def checkCookie(cookie):
	headers = {
		'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
		'accept-language': 'en-US,en;q=0.9',
		'cache-control': 'max-age=0',
		'sec-fetch-dest': 'document',
		'sec-fetch-mode': 'navigate',
		'sec-fetch-site': 'none',
		'sec-fetch-user': '?1',
		'upgrade-insecure-requests': '1',
		'user-agent': 'Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36',
		'cookie': cookie
	}
	url = 'https://m.facebook.com/composer/ocelot/async_loader/?publisher=feed'
	res = requests.get(url, headers=headers)
	data = res.text
	token = re.findall(r'accessToken\\":\\"(.*?)\\', data)
	if token != []: return True
	else: return False

def auto(uID, passWord, key2FA, soLuong, reaction, delay):
	nFileCookie = f'Cookies/{uID}.txt'
	if not os.path.exists(nFileCookie): open(nFileCookie, 'w').close()

	cookie = open(nFileCookie).read()
	
	check = checkCookie(cookie)
	if check == False:
		GCF = GetCookieFacebook(uID, passWord, key2FA)
		print("login facebook...")
		cookie = GCF.getCookie()
		# print(cookie)
		if cookie == None:
			print("Error")
			return 0
		else:
			f = open(nFileCookie, 'w')
			f.write(cookie)
			f.close()

	CR = CmtReact(cookie)

	nd = open('contentCMT.txt', 'r', encoding='utf8').read()

	listContent = nd.split('|')
	listIdPost = []
	stt = 1
	while True:
		listPost = CR.getListPost()
		for post in listPost:
			idPost = post['idPost']

			if idPost in listIdPost: continue
			else: listIdPost.append(idPost)

			infoPost = CR.getInfoPost(idPost)

			name = infoPost['name'] 
			caption = infoPost['caption']
			linkReaction = infoPost['linkReaction'] 
			postAtt = infoPost['postAtt']
			
			print(f'\n{stt} +++ {name}: {caption}')
			CR.reactionPost(linkReaction, reaction)
			print(f'\tReact: {reaction}')
			if post['comment'] == True:
				content = random.choice(listContent).replace("#", name)
				CR.commentPost(postAtt, content)
				print(f'\tComment: {content}')

			stt += 1
			if stt > soLuong: return 0
			sleep(random.randint(delay-1,delay+1))

def main():
	print("ID facebook|mat khau|ma 2Fa")
	tk = input("\n- Nhap: ")
	tk = tk.replace(" ", "")
	tk = tk.split('|')

	uID = tk[0]
	passWord = tk[1]
	key2FA = tk[2]

	soLuong = int(input("\n- So luong bai viet: "))
	delay = int(input("\n- Time delay: "))

	print("<======>\nLIKE: 0\nLOVE: 1\nTHUONGTHUONG: 2\nHAHA: 3\nWOW: 4\nSAD: 5\nANGRY: 6\n<======>")
	lst = ['LIKE', 'LOVE', 'THUONGTHUONG', 'HAHA', 'WOW', 'SAD', 'ANGRY']
	vt = int(input("\n- Cam xuc: "))
	reaction = lst[vt]
	print("\n(>.<)(>.<)(>.<)(>.<)(>.<)\n")
	auto(uID, passWord, key2FA, soLuong, reaction, delay)
	input("Xong!!!")

if __name__ == '__main__':
	main()