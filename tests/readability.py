"""Run against npm start: python3 tests/readability.py"""
from playwright.sync_api import sync_playwright
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
verbs=json.loads((root/'verbs.json').read_text())['verbs']
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':320,'height':568})
 page.set_default_timeout(8000)
 page.add_init_script('''(()=>{
   const OriginalAudio=window.Audio;window.tracks=[];
   window.Audio=function(...args){const a=new OriginalAudio(...args);tracks.push(a);return a;};
   window.Audio.prototype=OriginalAudio.prototype;
 })();''')
 url='http://127.0.0.1:4173/'
 page.goto(url)
 page.get_by_role('button',name='10問チャレンジをはじめる').wait_for()
 for base in ['be','have','take','understand','practice','listen']:
  ids=[v['id'] for v in verbs if v['base']!=base]
  page.evaluate('(ids)=>localStorage.setItem("kuroneko-english-v1",JSON.stringify({learned:ids,settings:{sfx:false}}))',ids)
  page.reload();page.get_by_role('button',name='10問チャレンジをはじめる').click()
  # Simulate top and bottom safe areas in the smallest supported viewport.
  page.locator('.app').evaluate("el=>{el.style.paddingTop='20px';el.style.paddingBottom='34px';}")
  assert page.locator('.choice').count()==4
  assert page.evaluate('document.documentElement.scrollHeight<=innerHeight'),base
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),base
  for rect in page.locator('.choice').evaluate_all('(els)=>els.map(el=>el.getBoundingClientRect().toJSON())'):
   assert rect['height']>=44 and rect['bottom']<=534,(base,rect)
  assert int(page.locator('.question h1').evaluate('el=>parseFloat(getComputedStyle(el).fontSize)'))>=36
  assert int(page.locator('.choice').first.evaluate('el=>parseFloat(getComputedStyle(el).fontSize)'))>=28
  assert int(page.locator('.meaning').evaluate('el=>parseFloat(getComputedStyle(el).fontSize)'))>=20
  assert int(page.locator('.target').evaluate('el=>parseFloat(getComputedStyle(el).fontSize)'))>=20
  if base=='understand':page.screenshot(path='/tmp/kuroneko-readable-small.png')
 page.set_viewport_size({'width':390,'height':844})
 page.reload();page.get_by_role('button',name='10問チャレンジをはじめる').click()
 page.screenshot(path='/tmp/kuroneko-readable.png')
 # Audio files actually decode and play after a user interaction.
 page.get_by_role('button',name='音の設定').click()
 page.locator('#bgm-toggle').check();page.get_by_role('button',name='閉じる',exact=True).click()
 page.wait_for_function('tracks.length && tracks.at(-1).currentTime > 0 && !tracks.at(-1).paused')
 assert page.evaluate('tracks.at(-1).src.endsWith("normal.mp3")')
 base=page.locator('.question h1').inner_text()
 verb=next(v for v in verbs if v['base']==base)
 field='past' if page.locator('.target b').inner_text()=='過去形' else 'participle'
 choices=page.locator('.choice b').all_text_contents();answer=verb[field].split(' / ')[0]
 page.locator('.choice').nth(choices.index(answer)).click()
 page.get_by_role('button',name='結果を見る').click()
 page.wait_for_function('tracks.at(-1).src.endsWith("perfect.mp3") && tracks.at(-1).currentTime>0')
 assert page.evaluate('tracks.slice(0,-1).every(a=>a.paused)')
 page.get_by_role('button',name='もう一度チャレンジ').click()
 base=page.locator('.question h1').inner_text();verb=next(v for v in verbs if v['base']==base)
 field='past' if page.locator('.target b').inner_text()=='過去形' else 'participle'
 choices=page.locator('.choice b').all_text_contents();answer=verb[field].split(' / ')[0]
 page.locator('.choice').nth(next(i for i,c in enumerate(choices) if c!=answer)).click()
 page.get_by_role('button',name='結果を見る').click()
 page.wait_for_function('tracks.at(-1).src.endsWith("result.mp3") && tracks.at(-1).currentTime>0')
 assert page.evaluate('tracks.slice(0,-1).every(a=>a.paused)')
 print('PASS: 4 readable choices, compact worst cases with simulated safe areas, required font sizes, all 3 MP3 files play and previous BGM stops')
 browser.close()
