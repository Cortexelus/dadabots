from ttapi import Bot

AUTH = 'HDuKXnXcExdxcpjGuVVOuSEJ'
USERID = '511479b5eb35c11c9a3b65e1'
ROOMID = '5114792feb35c11c9a3b65e0'


bot = Bot(AUTH, USERID, ROOMID)

def speak(data):
   name = data['name']
   text = data['text']
   if text == '/hello':
      bot.speak('Hey! How are you %s ?' % name)

bot.on('speak', speak)

bot.start()