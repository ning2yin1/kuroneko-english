const VERSION='kuroneko-v2';
const ROOT=new URL('./',self.location.href);
const FILES=['./','./index.html','./style.css','./app.js','./core.js','./verbs.json','./manifest.webmanifest','./assets/audio/tracks.json','./assets/audio/normal.mp3','./assets/audio/perfect.mp3','./assets/audio/result.mp3','./assets/cat.svg','./assets/icon-192.png','./assets/icon-512.png','./assets/icon-maskable.png'];
self.addEventListener('install',event=>event.waitUntil(caches.open(VERSION).then(cache=>cache.addAll(FILES)).then(()=>self.skipWaiting())));
self.addEventListener('activate',event=>event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(key=>key.startsWith('kuroneko-')&&key!==VERSION).map(key=>caches.delete(key)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',event=>{
 const req=event.request,url=new URL(req.url);
 if(req.method!=='GET'||url.origin!==ROOT.origin||!url.pathname.startsWith(ROOT.pathname))return;
 event.respondWith((async()=>{
  const cache=await caches.open(VERSION);
  try{const response=await fetch(req);if(response.ok){await cache.put(req,response.clone());}return response;}
  catch{const saved=await cache.match(req);if(saved)return saved;if(req.mode==='navigate')return cache.match(new URL('./index.html',ROOT));return new Response('',{status:503,statusText:'Offline'});}
 })());
});
