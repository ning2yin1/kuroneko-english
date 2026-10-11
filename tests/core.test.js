import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {makeQuestion,makeQuiz,normalizeState} from '../core.js';
const verbs=JSON.parse(readFileSync(new URL('../verbs.json',import.meta.url))).verbs;
test('100 unique verbs, 60 irregular and 40 regular, complete examples',()=>{
 assert.equal(verbs.length,100);assert.equal(new Set(verbs.map(v=>v.id)).size,100);
 assert.equal(verbs.filter(v=>v.type==='irregular').length,60);
 assert.equal(verbs.filter(v=>v.type==='regular').length,40);
 for(const v of verbs)for(const f of ['past','participle']){assert.ok(v.examples[f].en);assert.ok(v.examples[f].ja);assert.ok(v[f].split(/\s*\/\s*/).some(form=>new RegExp(`\\b${form}\\b`,'i').test(v.examples[f].en)),`${v.base} ${f}`);}
});
test('every possible question has five unique choices and exactly one valid answer',()=>{
 for(const v of verbs)for(const field of ['past','participle'])for(let i=0;i<20;i++){
 const q=makeQuestion(v,field);assert.equal(q.choices.length,5);assert.equal(new Set(q.choices).size,5);
 assert.equal(q.choices.filter(c=>v[field].split(/\s*\/\s*/).includes(c)).length,1);assert.ok(q.choices.includes(q.answer));
 if(v.base==='be'&&field==='past'){assert.equal(q.answer,'was');assert.ok(q.subject);}
 }
});
test('random plays have no duplicates, exclude learned, and shuffle answers',()=>{
 const ids=verbs.slice(0,30).map(v=>v.id),positions=new Set(),orders=new Set(),fields=new Set();
 for(let i=0;i<100;i++){const q=makeQuiz(verbs,ids);assert.equal(q.length,10);assert.equal(new Set(q.map(x=>x.verb.id)).size,10);assert.equal(new Set(q.map(x=>x.verb.type)).size,2);assert.ok(q.every(x=>!ids.includes(x.verb.id)));orders.add(q.map(x=>x.verb.id).join(','));q.forEach(x=>{positions.add(x.choices.indexOf(x.answer));fields.add(x.field);});}
 assert.equal(positions.size,5);assert.equal(fields.size,2);assert.ok(orders.size>90);
});
test('0–9 unlearned use only remaining verbs; unmarking restores eligibility',()=>{
 for(let n=0;n<10;n++){const ids=verbs.slice(n).map(v=>v.id),q=makeQuiz(verbs,ids);assert.equal(q.length,n);assert.ok(q.every(x=>!ids.includes(x.verb.id)));}
 const ids=verbs.map(v=>v.id);assert.equal(makeQuiz(verbs,ids).length,0);ids.shift();assert.equal(makeQuiz(verbs,ids)[0].verb.id,verbs[0].id);
});
test('saved progress and settings survive serialization and malformed input',()=>{
 const data={learned:['v001','v001','unknown'],history:[{id:'v001',correct:false,field:'past',at:1}],settings:{bgm:true,sfx:false,volume:.7}};
 const state=normalizeState(data,verbs);assert.deepEqual(state.learned,['v001']);assert.deepEqual(normalizeState(JSON.parse(JSON.stringify(state)),verbs),state);assert.equal(normalizeState(null,verbs).learned.length,0);
});
