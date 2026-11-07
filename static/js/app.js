const $ = (s) => document.querySelector(s);
const $$ = (s) => [...document.querySelectorAll(s)];
let appData = {};
const descriptions = [
 ["🪝","Phishing Awareness","Phishing uses fake messages to steal information. Never click suspicious links."],
 ["🔐","Password Security","Use strong, unique passwords. Enable Multi-Factor Authentication."],
 ["🎭","Social Engineering","Attackers manipulate people into revealing information. Always verify unexpected requests."],
 ["🦠","Malware Awareness","Malware is harmful software. Download software from trusted sources."],
 ["🌐","Safe Browsing","Check website addresses, avoid unknown downloads and keep your browser updated."]
];
async function api(url, options={}) {
 const res = await fetch(url,{headers:{"Content-Type":"application/json"},...options});
 const data = await res.json();
 if(!res.ok) throw new Error(data.error || "Something went wrong.");
 return data;
}
function showPage(id){
 $$(".page").forEach(p=>p.classList.toggle("active",p.id===id));
 $$(".nav-link").forEach(b=>b.classList.toggle("active",b.dataset.page===id));
 const names={overview:"Overview",learn:"Learning modules",phishing:"Phishing checker",password:"Password checker",quiz:"Cybersecurity quiz",assessment:"Assessment",social:"Social engineering",tips:"Security tips",progress:"Track progress",records:"Student records"};
 $("#page-title").textContent=names[id]||"CyberAware";
 window.scrollTo({top:0,behavior:"smooth"});
}
$("#navigation").addEventListener("click",e=>{const b=e.target.closest("[data-page]");if(b)showPage(b.dataset.page)});
$$("[data-go]").forEach(b=>b.addEventListener("click",()=>showPage(b.dataset.go)));
async function refreshDashboard(){
 try{const d=await api("/api/dashboard");$("#total-students").textContent=d.total_students;$("#attempts").textContent=d.assessment_attempts;$("#avg-assessment").textContent=d.average_assessment+"%";$("#avg-progress").textContent=d.average_progress+"%"}catch(e){console.error(e)}
}
$("#refresh").addEventListener("click",refreshDashboard);
function renderLearning(){
 $("#learning-cards").innerHTML=descriptions.map(([icon,title,desc])=>`<article class="learning-card"><span class="card-icon">${icon}</span><h3>${title}</h3><p>${desc}</p></article>`).join("");
 $("#attack-cards").innerHTML=appData.attacks.map(a=>`<article class="learning-card"><span class="card-icon">🛡️</span><h3>${a.name}</h3><p>${a.description}</p><div class="protection">Protection: ${a.protection}</div></article>`).join("");
 $("#tips-list").innerHTML=appData.tips.map((t,i)=>`<div class="tip-item"><b>${String(i+1).padStart(2,"0")}.</b> ${t}</div>`).join("");
 $("#module-checklist").innerHTML=appData.modules.map((m,i)=>`<label class="check-item"><input type="checkbox" value="${m.replaceAll('"','&quot;')}"> ${m}</label>`).join("");
}
$("#check-message").addEventListener("click",async()=>{
 const message=$("#message-input").value.trim();if(!message){alert("Enter a fictional message first.");return}
 try{const d=await api("/api/phishing",{method:"POST",body:JSON.stringify({message})});
 const box=$("#phishing-result");box.className="result-box "+(d.suspicious?"warn":"good");
 box.innerHTML=`<b>${d.suspicious?"⚠ Warning: suspicious language detected":"✓ Initial keyword check"}</b><p>${d.message}</p>${d.found.length?`<b>Potential warning signs:</b><ul>${d.found.map(w=>`<li>${w}</li>`).join("")}</ul>`:""}<b>Safety recommendations:</b><ol>${d.recommendations.map(x=>`<li>${x}</li>`).join("")}</ol>`;}catch(e){alert(e.message)}
});
$("#toggle-password").addEventListener("click",()=>{const p=$("#password-input");p.type=p.type==="password"?"text":"password";$("#toggle-password").textContent=p.type==="password"?"Show":"Hide"});
$("#check-password").addEventListener("click",async()=>{
 const password=$("#password-input").value;if(!password){alert("Enter a fictional test password.");return}
 try{const d=await api("/api/password",{method:"POST",body:JSON.stringify({password})});const box=$("#password-result");box.className="result-box "+(d.strength==="STRONG"?"good":d.strength==="WEAK"?"warn":"");box.innerHTML=`<b>Password strength: ${d.strength}</b><p>${d.advice}</p><small>Rule score: ${d.score}/6. This is a simple educational estimate, not a guarantee of password security.</small>`;}catch(e){alert(e.message)}
});
function renderQuiz(kind){
 const questions=kind==="quiz"?appData.quiz:appData.assessment;
 const target=kind==="quiz"?"#quiz-area":"#assessment-area";
 const intro=kind==="quiz"?"Choose the best answer for each question.":"Enter an anonymous student ID. Your result will be saved.";
 $(target).innerHTML=`${kind==="assessment"?'<label for="assessment-id">Anonymous student ID</label><input id="assessment-id" placeholder="e.g. STUDENT001">':""}<p class="muted">${intro}</p><form id="${kind}-form">${questions.map((q,i)=>`<div class="question-card"><h3>Question ${i+1}. ${q.question}</h3>${q.options.map(o=>`<label class="option"><input type="radio" name="q${i}" value="${o[0]}" required> ${o}</label>`).join("")}</div>`).join("")}<button class="primary-btn" type="submit">${kind==="quiz"?"Submit quiz":"Submit assessment"} →</button></form><div id="${kind}-result" class="quiz-result"></div>`;
 $(`${target} form`).addEventListener("submit",async e=>{
  e.preventDefault();const answers=questions.map((q,i)=>new FormData(e.target).get("q"+i));
  const student_id=kind==="assessment"?$("#assessment-id").value.trim():"";
  if(kind==="assessment"&&!student_id){alert("Please enter an anonymous student ID.");return}
  try{const d=await api("/api/quiz",{method:"POST",body:JSON.stringify({kind,answers,student_id})});
   const out=$(`${target} #${kind}-result`);out.innerHTML=`<div class="result-box ${d.percentage>=60?"good":"warn"}"><h3>Result: ${d.score}/${d.total} (${d.percentage}%)</h3><b>${d.percentage>=80?"Excellent cybersecurity awareness!":d.percentage>=60?"Good effort! Keep learning.":"Keep practising your cybersecurity knowledge."}</b>${d.details.map((r,i)=>`<p>${r.correct?"✓":"✕"} Question ${i+1}: ${r.correct?"Correct":"Correct answer: "+r.answer}<br><small>${r.explanation}</small></p>`).join("")}${d.saved?"<b>Assessment result saved successfully.</b>":""}</div>`;
   e.target.querySelector("button[type=submit]").disabled=true;refreshDashboard();
  }catch(err){alert(err.message)}
 });
}
$("#random-tip").addEventListener("click",()=>{$("#random-tip-box").textContent=appData.tips[Math.floor(Math.random()*appData.tips.length)]});
$("#save-progress").addEventListener("click",async()=>{
 const student_id=$("#student-id").value.trim();if(!student_id){alert("Enter an anonymous student ID.");return}
 const completed=$$("#module-checklist input:checked").map(x=>x.value);
 try{const d=await api("/api/progress",{method:"POST",body:JSON.stringify({student_id,completed})});const box=$("#progress-result");box.className="result-box good";box.innerHTML=`<b>Progress saved successfully!</b><p>${d.completed_count} of ${d.total_modules} modules completed · ${d.progress_percentage}%</p><p>${d.progress_percentage===100?"All modules completed!":d.progress_percentage>=50?"Good progress. Keep learning!":"Continue learning and practising."}</p>`;refreshDashboard()}catch(e){alert(e.message)}
});
$("#search-records").addEventListener("click",loadRecords);
async function loadRecords(){
 try{const sid=encodeURIComponent($("#record-search").value.trim());const d=await api("/api/records?student_id="+sid);const rows=[];
 d.progress.forEach(r=>rows.push({type:"Learning progress",id:r.student_id,score:`${r.completed_count}/${r.total_modules} modules`,pct:r.progress_percentage+"%",date:r.created_at||"—"}));
 d.assessments.forEach(r=>rows.push({type:"Assessment",id:r.student_id,score:`${r.score}/${r.total_questions}`,pct:r.percentage+"%",date:r.created_at||"—"}));
 $("#records-output").innerHTML=rows.length?`<table class="record-table"><thead><tr><th>TYPE</th><th>STUDENT ID</th><th>SCORE</th><th>RESULT</th><th>DATE</th></tr></thead><tbody>${rows.map(r=>`<tr><td>${r.type}</td><td>${escapeHtml(r.id)}</td><td>${r.score}</td><td>${r.pct}</td><td>${r.date}</td></tr>`).join("")}</tbody></table>`:'<div class="empty">No student records found.</div>';
 }catch(e){$("#records-output").textContent=e.message}
}
function escapeHtml(s){return String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]))}
$("#generate-pdf").addEventListener("click",()=>{const sid=$("#pdf-student-id").value.trim();if(!sid){alert("Enter a student ID.");return}window.location.href="/api/report/"+encodeURIComponent(sid)});
(async function init(){try{appData=await api("/api/content");renderLearning();renderQuiz("quiz");renderQuiz("assessment");$("#random-tip-box").textContent=appData.tips[0];refreshDashboard()}catch(e){console.error(e);alert("Could not load CyberAware. Please restart the Flask server.")}})();
