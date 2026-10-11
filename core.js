export const fields = ['base', 'past', 'participle'];
export const labels = {base:'原形', past:'過去形', participle:'過去分詞'};
export function shuffle(items, random = Math.random) {
  const result = [...items];
  for (let i=result.length-1;i>0;i--) {const j=Math.floor(random()*(i+1));[result[i],result[j]]=[result[j],result[i]];}
  return result;
}
export function makeQuestion(verb, field, random = Math.random) {
  const variants=verb[field].split(/\s*\/\s*/);
  const answer=verb.base==='be'&&field==='past'?'was':variants[0];
  const distractors=[...new Set(verb.choices[field])].filter(x=>!variants.includes(x));
  if(distractors.length<4) throw new Error(`選択肢が不足: ${verb.base} ${field}`);
  return {verb, field, answer, subject:verb.base==='be'&&field==='past'?'主語は I（私は）':null, choices:shuffle([answer,...shuffle(distractors,random).slice(0,4)],random)};
}
export function makeQuiz(verbs, learned, random = Math.random) {
  const pool=shuffle(verbs.filter(v=>!learned.includes(v.id)),random);
  const selected=pool.slice(0,10);
  // Both verb types appear when the remaining pool allows a mixed play.
  if(selected.length>=2&&new Set(pool.map(v=>v.type)).size>1&&new Set(selected.map(v=>v.type)).size===1){
    selected[selected.length-1]=pool.find(v=>v.type!==selected[0].type);
  }
  return shuffle(selected,random).map(v=>makeQuestion(v,random()<.5?'past':'participle',random));
}
export function normalizeState(raw, verbs) {
  const ids=new Set(verbs.map(v=>v.id));
  return {learned:Array.isArray(raw?.learned)?[...new Set(raw.learned.filter(id=>ids.has(id)))]:[],history:Array.isArray(raw?.history)?raw.history.filter(h=>ids.has(h.id)&&typeof h.correct==='boolean'&&['past','participle'].includes(h.field)&&Number.isFinite(h.at)).slice(-3000):[], settings:{bgm:raw?.settings?.bgm===true,sfx:raw?.settings?.sfx!==false,volume:Number.isFinite(raw?.settings?.volume)?Math.max(0,Math.min(1,raw.settings.volume)):.4}};
}
