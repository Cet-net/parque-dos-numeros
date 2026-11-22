(function(root){
 'use strict';
 const activities=[
 {id:'cars',name:'Carros de Trombada',short:'Carros',topic:'Adição e subtração',color:'#ffad31',ink:'#864000',icon:'car',tag:'Junte, tire e descubra'},
 {id:'clowns',name:'Palhaços Saltimbancos',short:'Palhaços',topic:'Composição de números',color:'#ff89af',ink:'#992858',icon:'clown',tag:'Cada palhaço conta'},
 {id:'factory',name:'Fábrica de Risadas',short:'Fábrica',topic:'Grupos e multiplicação',color:'#a298ff',ink:'#4735a0',icon:'factory',tag:'Multiplique a diversão'},
 {id:'patterns',name:'Blocos de Sequência',short:'Blocos',topic:'Padrões e sequências',color:'#65d3bf',ink:'#146a60',icon:'blocks',tag:'Qual é o próximo?'},
 {id:'bubbles',name:'Mestres da Bolha',short:'Bolhas',topic:'Contagem e valor posicional',color:'#78c8ff',ink:'#1c5f99',icon:'bubbles',tag:'Uma descoberta em cada bolha'},
 {id:'clock',name:'Relógio do Espetáculo',short:'Relógio',topic:'Horas e minutos',color:'#ffce65',ink:'#795000',icon:'clock',tag:'O show tem hora para começar',extra:true},
 {id:'tickets',name:'Bilheteria do Circo',short:'Bilheteria',topic:'Dinheiro e troco',color:'#b3d77d',ink:'#43621f',icon:'ticket',tag:'Um ingresso para calcular',extra:true},
 {id:'shapes',name:'Tenda das Formas',short:'Formas',topic:'Figuras e suas propriedades',color:'#d7a5ef',ink:'#714092',icon:'shapes',tag:'A geometria entra em cena',extra:true}
 ];
 activities.push({id:'division',name:'Balões para Todos',short:'Divisão',topic:'Divisão e partilha igual',color:'#ffb4cf',ink:'#8a3f74',icon:'clown',tag:'Um balão para cada um',extra:true});
 const rnd=(a,b)=>a+Math.floor(Math.random()*(b-a+1));
 const shuffle=a=>a.slice().sort(()=>Math.random()-.5);
 function options(answer,min=0,max=100){
  const set=new Set([answer]);
  for(const n of shuffle([-1,1,-2,2,-5,5,10,-10])){let v=answer+n;if(v>=min&&v<=max)set.add(v);if(set.size===4)break;}
  while(set.size<4)set.add(rnd(min,max));
  return shuffle([...set]);
 }
 const shapes=[{id:'circle',name:'círculo',sides:0},{id:'triangle',name:'triângulo',sides:3},{id:'square',name:'quadrado',sides:4},{id:'rectangle',name:'retângulo',sides:4},{id:'pentagon',name:'pentágono',sides:5},{id:'hexagon',name:'hexágono',sides:6}];
 function makeQuestion(id,level){
  level=Math.max(1,Math.min(3,level));let q={id,level,type:'choice'};
  if(id==='division'){
   const divisor=rnd(2,[4,6,9][level-1]),answer=rnd(1,[5,8,10][level-1]),total=divisor*answer;
   return {...q,type:'distribute',divisor,total,answer,options:options(answer,1,12),prompt:`O palhaço tem ${total} balões para ${divisor} crianças. Quantos balões cada criança recebe?`,hint:`Escolha uma quantidade que, repetida para todas as crianças, use todos os balões sem sobrar.`,explain:`${total} ÷ ${divisor} = ${answer}. Cada criança recebeu ${answer} ${answer===1?'balão':'balões'}!`};
  }
  if(id==='cars'){
   let max=[10,20,100][level-1],sub=level>1&&rnd(0,1)===1;
   let a=sub?rnd(3,max):rnd(1,max-1),b=sub?rnd(1,a):rnd(1,max-a);
   let answer=sub?a-b:a+b;
   return {...q,a,b,op:sub?'−':'+',answer,options:options(answer,0,max+10),prompt:'Encontre o resultado, dirija até a pista certa e dê uma trombada!',hint:sub?`Comece em ${a} e volte ${b} casas na contagem.`:`Comece em ${a} e conte mais ${b}.`,explain:`${a} ${sub?'−':'+'} ${b} = ${answer}. Trombada certeira!`};
  }
  if(id==='clowns'){
   const total=rnd(level===1?3:8,[10,20,30][level-1]),a=rnd(1,total-1),b=level===3?rnd(0,total-a-1):0,answer=total-a-b;
   return {...q,type:'build',total,a,b,answer,prompt:`Queremos ${total} palhaços ao todo. Complete o palco azul!`,hint:`Já temos ${a+b}. Pense: ${a+b} + quanto = ${total}?`,explain:`${a}${b?' + '+b:''} + ${answer} = ${total}. Todos juntos no picadeiro!`};
  }
  if(id==='factory'){
   const groups=rnd(2,[3,5,9][level-1]),each=rnd(2,[4,5,9][level-1]),answer=groups*each;
   return {...q,groups,each,answer,options:options(answer,0,99),prompt:`A máquina fez ${groups} grupos com ${each} sorrisos em cada. Quantos sorrisos?`,hint:`Some ${Array(groups).fill(each).join(' + ')}.`,explain:`${groups} × ${each} = ${answer}. Um montão de risadas!`};
  }
  if(id==='patterns'){
   if(level===3){let start=rnd(1,20),step=[2,3,5,10][rnd(0,3)],series=Array.from({length:5},(_,i)=>start+i*step),answer=start+5*step;return {...q,numeric:true,series,step,answer,options:options(answer,0,100),prompt:'Descubra o salto e complete a sequência.',hint:`Cada número aumenta ${step}.`,explain:`O salto é de ${step} em ${step}. Depois de ${series[4]}, vem ${answer}.`};}
   const ids=shuffle(['circle','triangle','square','pentagon']),pattern=level===1?[ids[0],ids[1]]:rnd(0,1)?[ids[0],ids[0],ids[1]]:[ids[0],ids[1],ids[2]],len=level===1?5:rnd(5,7),series=Array.from({length:len},(_,i)=>pattern[i%pattern.length]),answer=pattern[len%pattern.length];
   return {...q,pattern,series,answer,options:shuffle(ids),prompt:'Olhe como os blocos se repetem. Qual vem agora?',hint:'Encontre o pedacinho que se repete e siga a mesma ordem.',explain:'Isso! Você manteve a ordem do padrão.'};
  }
  if(id==='bubbles'){
   if(level===1){let answer=rnd(2,10);return {...q,answer,options:options(answer,1,15),prompt:'Conte as estrelas e estoure a bolha com a quantidade certa.',hint:'Toque em cada estrela enquanto conta, sem repetir nenhuma.',explain:`São ${answer} estrelas!`,count:answer};}
   let tens=rnd(1,9),units=rnd(0,9),hundreds=level===3?rnd(1,9):0,answer=hundreds*100+tens*10+units;
   return {...q,tens,units,hundreds,answer,prompt:`Que número tem ${hundreds?hundreds+' centena'+(hundreds>1?'s':'')+', ':''}${tens} dezena${tens>1?'s':''} e ${units} unidade${units!==1?'s':''}?`,hint:`${hundreds?hundreds+' × 100 + ':''}${tens} × 10 + ${units}.`,explain:`${hundreds?hundreds*100+' + ':''}${tens*10} + ${units} = ${answer}.` ,options:options(answer,0,1000)};
  }
  if(id==='clock'){
   const hour=rnd(1,12),minute=level===1?0:level===2?[0,30][rnd(0,1)]:[0,15,30,45][rnd(0,3)],answer=hour*60+minute;
   const opts=new Set([answer,((hour%12)+1)*60+minute,hour*60+(minute+30)%60,((hour+10)%12+1)*60+minute]);
   return {...q,hour,minute,answer,options:shuffle([...opts]),prompt:'O espetáculo começa no horário do relógio. Que horas são?',hint:'O ponteiro pequeno indica as horas. O grande indica os minutos.',explain:`O relógio marca ${hour}h${String(minute).padStart(2,'0')}. Hora do espetáculo!`};
  }
  if(id==='tickets'){
   let price=level===1?rnd(2,9):level===2?rnd(5,18):rnd(10,35),count=level===3?rnd(2,3):1,total=price*count;
   let paid=level===1?price:Math.ceil((total+1)/10)*10,answer=level===1?total:paid-total;
   return {...q,price,count,total,paid,answer,options:options(answer,0,120),prompt:level===1?'Um ingresso custa esse valor. Qual quantia compra o ingresso?':`Você compra ${count} ingresso${count>1?'s':''} e paga R$ ${paid}. Quanto recebe de troco?`,hint:level===1?`Procure o mesmo valor do ingresso: ${price} reais.`:`A compra custa ${count} × ${price} = ${total} reais. Tire esse valor de ${paid}.`,explain:level===1?`O ingresso custa R$ ${price},00.`:`R$ ${paid},00 − R$ ${total},00 = R$ ${answer},00 de troco.`};
  }
  if(id==='shapes'){
   if(level===1){const target=shapes[rnd(0,3)];return {...q,answer:target.id,options:shuffle(shapes.slice(0,4).map(x=>x.id)),prompt:`Encontre o ${target.name}.`,hint:'Observe o contorno de cada figura.',explain:`Muito bem! Esse é o ${target.name}.`,target};}
   let target=shapes[[1,2,4,5][rnd(0,3)]];
   if(level===2)return {...q,target,answer:target.sides,options:shuffle([3,4,5,6]),prompt:'Quantos lados retos tem esta figura?',hint:'Comece em um canto e acompanhe o contorno até voltar ao começo.',explain:`O ${target.name} tem ${target.sides} lados.`};
   const ask=rnd(0,2),answer=['square','rectangle','circle'][ask],descriptions=['quatro lados iguais e quatro ângulos retos','quatro ângulos retos e dois lados longos e dois curtos','um contorno curvo, sem lados retos nem vértices'];
   return {...q,answer,options:shuffle(shapes.slice(0,4).map(x=>x.id)),prompt:`Qual figura tem ${descriptions[ask]}?`,hint:ask===0?'Pense em uma figura parecida com a face de um dado.':ask===1?'Pense no formato de uma porta.':'Pense no contorno de uma roda.',explain:`É o ${shapes.find(x=>x.id===answer).name}!`};
  }
  throw Error('Atividade desconhecida');
 }
 function evaluate(q,value){return q.answer===value;}
 const api={activities,makeQuestion,evaluate,shapes,options};
 if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.MathPark=api;
})(typeof window!=='undefined'?window:globalThis);
