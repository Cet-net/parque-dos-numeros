const assert=require('node:assert/strict');
const {activities,makeQuestion,evaluate}=require('./dist/game-data.js');
let total=0;
for(const a of activities)for(let level=1;level<=3;level++)for(let i=0;i<500;i++){
 const q=makeQuestion(a.id,level);assert.equal(q.id,a.id);assert.equal(q.level,level);assert(q.prompt&&q.hint&&q.explain);
 assert(evaluate(q,q.answer));assert(!evaluate(q,typeof q.answer==='number'?q.answer+123456:'invalid'));
 if(q.type==='choice'||q.id==='division'){assert.equal(q.options.length,4);assert.equal(new Set(q.options).size,4);assert(q.options.includes(q.answer));}
 if(a.id==='division'){assert(q.divisor>=2&&q.divisor<=9);assert.equal(q.total/q.divisor,q.answer);assert.equal(q.total%q.divisor,0);assert.equal(q.type,'distribute');}
 if(a.id==='cars')assert.equal(q.answer,q.op==='+'?q.a+q.b:q.a-q.b);
 if(a.id==='clowns'){assert.equal(q.a+q.b+q.answer,q.total);assert(q.answer>0&&q.answer<=30);}
 if(a.id==='factory')assert.equal(q.answer,q.groups*q.each);
 if(a.id==='patterns'&&q.numeric)assert.equal(q.answer,q.series.at(-1)+q.step);
 if(a.id==='bubbles'&&level>1)assert.equal(q.answer,q.hundreds*100+q.tens*10+q.units);
 if(a.id==='clock')assert.equal(q.answer,q.hour*60+q.minute);
 if(a.id==='tickets')assert.equal(q.answer,level===1?q.price:q.paid-q.price*q.count);
 total++;
}
console.log(`OK: ${total} desafios verificados, ${activities.length} atividades × 3 níveis; respostas, alternativas e operações consistentes.`);
