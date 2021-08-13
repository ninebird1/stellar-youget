import re
import StellarPlayer
from .you_get.extractors import iqiyi
from .you_get.extractors import youku
from .you_get.extractors import bilibili

class IqiyiPlugin(StellarPlayer.IStellarPlayerPlugin):
    def __init__(self, player: StellarPlayer.IStellarPlayer):
        super().__init__(player)
        self.playurl = []
        self.url = ''

    def show(self):
        list_layout = [[{'type':'label','name':'video_profile'},{'type':'link','name':'播放','width':60,'@click':'onPlayClick'}]]
        controls = [
            {'type':'space','height':10},
            {'group':
                [
                    {'type':'edit','name':'url_edit','label':'html页面地址'},
                    {'type':'button','name':'解析','width':60,'@click':'parse_html'},
                    {'type':'space','width':10}
                ],
                'height':30
            },
            {'type':'space','height':10},
            {'type':'list','name':'list','itemlayout':list_layout,'separator':True,'itemheight':40}
        ]
        self.player.doModal('main',500,400,'',controls)

    def parse_html(self,*args):
        url = self.player.getControlValue('main','url_edit')
        if url:
            if self.url == url:
                return
            self.player.updateControlValue('main','list',[])
            if hasattr(self.player, 'loadingAnimation'):
                self.player.loadingAnimation('main')
            self.url = url
            if re.match(r'(.*)iqiyi.com',url):
                youget = iqiyi.Iqiyi()
            elif re.match(r'(.*)youku.com',url):
                youget = youku.Youku()
            elif re.match(r'(.*)bilibili.com',url):
                youget = bilibili.Bilibili()
            try:
                youget.url = url
                youget.prepare()
            except:
                pass
            finally:
                if hasattr(self.player, 'loadingAnimation'):
                    self.player.loadingAnimation('main',stop=True)
                if youget.streams:
                    urls = []
                    print(youget.streams)
                    for k,v in youget.streams.items():
                        if type(youget) in [iqiyi.Iqiyi, youku.Youku]:
                            if 'm3u8_url' in v:
                                    urls.append({'url':v['m3u8_url'],'video_profile':v.get('video_profile',k)})
                        elif type(youget) == bilibili.Bilibili:
                            if 'src' in v:
                                    urls.append({'url':v['src'][0],'video_profile':v.get('quality',k)})
                    self.player.updateControlValue('main','list',urls)
                    self.playurl = urls
                    self.player.toast('main','解析完成')
                else:
                    self.player.toast('main','没有解析到播放地址')

            
    def onPlayClick(self, page, control, idx, *arg):
        if re.match(r'(.*)bilibili.com',self.url):
            ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'
            self.player.play(self.playurl[idx]['url'],headers={'referer':self.url,'user_agent':ua})
        else:
            self.player.play(self.playurl[idx]['url'])


def newPlugin(player:StellarPlayer.IStellarPlayer,*arg):
    plugin = IqiyiPlugin(player)
    return plugin

def destroyPlugin(plugin:StellarPlayer.IStellarPlayerPlugin):
    plugin.stop()
