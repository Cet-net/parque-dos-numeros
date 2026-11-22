(()=>{
'use strict';let active=null;
const people=['lia','kenji','maya','tom'];
function mount(container,q,onAnswer){dispose();const shares=Array(q.divisor).fill(0),timers=new Set();let busy=false,finished=false;
 container.innerHTML=`<section class="balloon-game" aria-label="Divisão de balões"><div class="balloon-bank"><div class="balloon-clown" aria-hidden="true"><img src="assets/clown-performer.webp" alt=""><span class="balloon-bunch">${Array.from({length:7},(_,i)=>`<i style="--i:${i}"></i>`).join('')}</span></div><div><span>COM O PALHAÇO</span><strong id="balloons-left">${q.total}</strong><small>balões para distribuir</small></div><div class="division-equation">${q.total} ÷ ${q.divisor} = <b>?</b></div></div><p class="balloon-instruction">Quantos balões cada criança recebe? Escolha uma resposta.</p><div class="balloon-children">${shares.map((_,i)=>`<div class="balloon-child" data-child="${i}"><div class="child-balloons" aria-hidden="true"></div><div class="give-balloon"><img src="assets/avatar-${people[i%4]}.webp" alt=""><span>Criança ${i+1}</span></div><div class="child-share"><b>0</b><span>balões</span></div></div>`).join('')}</div><div class="balloon-answers" role="group" aria-label="Quantos balões por criança?">${q.options.map(n=>`<button class="balloon-answer" data-answer="${n}"><strong>${n}</strong><span>${n===1?'balão':'balões'} por criança</span></button>`).join('')}</div><p class="balloon-status" aria-live="polite">Todas as crianças devem receber a mesma quantidade, sem sobrar balões.</p></section>`;
 const el=container.firstElementChild,status=el.querySelector('.balloon-status'),buttons=[...el.querySelectorAll('[data-answer]')];
 function later(fn,ms){const t=setTimeout(()=>{timers.delete(t);fn();},ms);timers.add(t);}
 function update(){el.querySelector('#balloons-left').textContent=q.total-shares.reduce((a,b)=>a+b,0);shares.forEach((n,i)=>{const child=el.querySelector('[data-child="'+i+'"]');child.querySelector('b').textContent=n;child.querySelector('.child-balloons').innerHTML=Array.from({length:n},(_,j)=>`<i style="--j:${j};--n:${n};--color:${['#fb78a1','#8c72d0','#50bfc1','#eeb34b'][j%4]}"></i>`).join('');});}
 function click(e){const b=e.target.closest('[data-answer]');if(!b)return;e.stopPropagation();if(busy||finished)return;const value=Number(b.dataset.answer);
  if(value!==q.answer){b.classList.add('wrong');b.setAttribute('aria-label',`${value} ${value===1?'balão':'balões'} por criança, tente outra resposta`);const used=value*q.divisor;status.textContent=used<q.total?`Com ${value} por criança, sobrariam ${q.total-used} balões. Tente outra quantidade.`:`Com ${value} por criança, faltariam ${used-q.total} balões. Tente outra quantidade.`;later(()=>b.classList.remove('wrong'),550);onAnswer(value);return;}
  busy=true;buttons.forEach(x=>x.disabled=true);b.classList.add('correct');status.textContent='Vamos conferir! O palhaço está entregando a mesma quantidade para cada criança.';
  let delivered=0;const delay=matchMedia('(prefers-reduced-motion: reduce)').matches?0:Math.max(55,Math.min(240,4200/q.total));
  function give(){const i=delivered%q.divisor;shares[i]++;delivered++;update();const child=el.querySelector('[data-child="'+i+'"]');child.classList.remove('receiving');void child.offsetWidth;child.classList.add('receiving');if(delivered<q.total)later(give,delay);else later(()=>{finished=true;busy=false;el.classList.add('division-won');el.querySelector('.division-equation b').textContent=q.answer;status.textContent=`Partilha perfeita! Cada criança recebeu ${q.answer} ${q.answer===1?'balão':'balões'}. Não sobrou nenhum!`;onAnswer(value);},350);}
  give();
 }
 el.addEventListener('click',click);active={dispose(){el.removeEventListener('click',click);timers.forEach(clearTimeout);}};
}
function dispose(){active?.dispose();active=null;}
window.BalloonDivision={mount,dispose};
})();
