"""Run with python3 tests/browser.py (requires Playwright and Chromium)."""
from playwright.sync_api import sync_playwright
from pathlib import Path
import json, subprocess, tempfile, time
root=Path(__file__).resolve().parents[1]
verbs=json.loads((root/'verbs.json').read_text())['verbs']
by_base={v['base']:v for v in verbs}
server=subprocess.Popen(['python3','-m','http.server','4174','--bind','127.0.0.1','--directory',str(root.parent)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
time.sleep(.5)
errors=[]
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  context=browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,device_scale_factor=1)
  page=context.new_page()
  page.set_default_timeout(8000)
  page.on('pageerror',lambda error:errors.append(str(error)))
  url='http://127.0.0.1:4174/'+root.name+'/'
  page.goto(url)
  page.get_by_role('button',name='10問チャレンジをはじめる').wait_for()
  page.screenshot(path='/tmp/kuroneko-home.png',full_page=True)
  page.get_by_role('button',name='10問チャレンジをはじめる').click()
  for width,height in [(320,568),(375,667),(390,844),(430,932)]:
   page.set_viewport_size({'width':width,'height':height})
   assert page.evaluate('document.documentElement.scrollHeight <= innerHeight'),f'scrolling at {width}x{height}'
   assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),f'horizontal overflow at {width}'
   assert page.locator('.choice').count()==5
   for rect in page.locator('.choice').evaluate_all('(els)=>els.map(el=>el.getBoundingClientRect().toJSON())'):
    assert rect['height']>=44 and rect['bottom']<=height
  page.set_viewport_size({'width':390,'height':844})
  page.screenshot(path='/tmp/kuroneko-quiz.png',full_page=True)
  seen=[]
  for i in range(10):
   base=page.locator('.question h1').inner_text();seen.append(base)
   target='past' if page.locator('.target b').inner_text()=='過去形' else 'participle'
   correct=by_base[base][target].split(' / ')[0]
   page.locator('.choice').nth(page.locator('.choice b').all_text_contents().index(correct)).click()
   page.get_by_role('heading',name='正解！その調子だにゃ').wait_for()
   assert page.locator('.example').count()==2
   if i==0:page.get_by_role('button',name='この単語を覚えた').click()
   page.get_by_role('button',name='結果を見る' if i==9 else '次の問題へ').click()
  assert len(set(seen))==10
  page.get_by_role('heading',name='満点！すごいにゃ！').wait_for()
  page.goto(url+'#words')
  page.locator('#search').fill(seen[0])
  assert page.locator('.learn.learned').count()>=1
  page.reload()
  page.locator('#status').select_option('learned')
  assert page.locator('#count').inner_text()=='1語の単語'
  page.locator('.learn.learned').click()
  assert page.locator('#count').inner_text()=='0語の単語'
  page.locator('#status').select_option('')
  page.locator('#type').select_option('regular')
  assert page.locator('#count').inner_text()=='40語の単語'
  page.locator('#type').select_option('irregular')
  assert page.locator('#count').inner_text()=='60語の単語'
  page.locator('#level').select_option('1')
  assert int(page.locator('#count').inner_text().split('語')[0])>0
  page.goto(url+'#history')
  assert '10問' in page.locator('main').inner_text()
  page.evaluate("localStorage.setItem('kuroneko-english-v1',JSON.stringify({learned:"+json.dumps([v['id'] for v in verbs[3:]])+",history:[],settings:{sfx:false}}))")
  page.goto(url);page.reload()
  page.get_by_role('button',name='10問チャレンジをはじめる').click()
  assert '/ 3' in page.locator('.quiz-top').inner_text()
  for i in range(3):
   base=page.locator('.question h1').inner_text();target='past' if page.locator('.target b').inner_text()=='過去形' else 'participle'
   answer=by_base[base][target].split(' / ')[0]
   choices=page.locator('.choice b').all_text_contents()
   value=next(x for x in choices if x!=answer) if i==0 else answer
   page.locator('.choice').nth(choices.index(value)).click()
   page.get_by_role('button',name='結果を見る' if i==2 else '次の問題へ').click()
  assert '2 / 3' in page.locator('.score').inner_text()
  assert page.locator('.review-word').count()==1
  page.evaluate("localStorage.setItem('kuroneko-english-v1',JSON.stringify({learned:"+json.dumps([v['id'] for v in verbs])+"}))")
  page.goto(url);page.reload()
  page.get_by_role('button',name='全100語のお祝いへ').click()
  page.get_by_role('heading',name='100語、ぜんぶ覚えたね！').wait_for()
  page.goto(url+'#words')
  assert page.locator('.word-card').count()==100
  page.locator('.learn').first.click()
  page.goto(url)
  page.get_by_role('button',name='10問チャレンジをはじめる').click()
  assert '/ 1' in page.locator('.quiz-top').inner_text()
  page.goto(url)
  page.evaluate('navigator.serviceWorker.ready')
  page.wait_for_function('navigator.serviceWorker.controller !== null')
  context.set_offline(True)
  page.reload()
  page.get_by_role('button',name='10問チャレンジをはじめる').wait_for()
  page.get_by_role('button',name='10問チャレンジをはじめる').click()
  assert page.locator('.choice').count()==5
  assert not errors, errors
  print('PASS: 4 mobile sizes, 10 unique questions, perfect and partial results, filters, persistence, learned exclusion/unmarking, 0/1/3 remaining, GitHub Pages subpath, offline reload; no page errors.')
  browser.close()
finally:
 server.terminate();server.wait()
